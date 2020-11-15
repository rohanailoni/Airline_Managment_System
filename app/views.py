from django.shortcuts import render
import json
from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from random import randint
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from random import randint,choice,uniform
import sys,os
from faker import Faker
import datetime
from django.conf import settings
from django.core.mail import send_mail
from spellchecker.utils import _parse_into_words, ENSURE_UNICODE, load_file
from AMS1.settings import BASE_DIR
from app.models import userinfo,enquiry,flight_info,leg,city_code,auto_correction,comment,one_time_password,login_log,logout_log,shortcuts,passengers
import pytz
from django.utils import timezone
from spellchecker import SpellChecker
from collections import Counter
import re
#spell checking algo start
class SpellChecker1(object):


    __slots__ = ["_distance", "_word_frequency", "_tokenizer", "_case_sensitive"]

    def __init__(
        self,
        language="en",
        local_dictionary=None,
        distance=2,
        tokenizer=None,
        case_sensitive=False,
    ):
        self._distance = None
        self.distance = distance  # use the setter value check

        self._tokenizer = _parse_into_words
        if tokenizer is not None:
            self._tokenizer = tokenizer

        self._case_sensitive = case_sensitive if not language else False
        self._word_frequency = WordFrequency(self._tokenizer, self._case_sensitive)

        if local_dictionary:
            self._word_frequency.load_dictionary(local_dictionary)
        elif language:
            filename = "{}.json.gz".format(language.lower())
            here = os.path.dirname(__file__)
            full_filename = os.path.join(here, "resources", filename)
            if not os.path.exists(full_filename):
                msg = (
                    "The provided dictionary language ({}) does not " "exist!"
                ).format(language.lower())
                raise ValueError(msg)
            self._word_frequency.load_dictionary(full_filename)

    def __contains__(self, key):
        """ setup easier known checks """
        key = ENSURE_UNICODE(key)
        return key in self._word_frequency

    def __getitem__(self, key):
        """ setup easier frequency checks """
        key = ENSURE_UNICODE(key)
        return self._word_frequency[key]

    @property
    def word_frequency(self):
        """ WordFrequency: An encapsulation of the word frequency `dictionary`
            Note:
                Not settable """
        return self._word_frequency

    @property
    def distance(self):
        """ int: The maximum edit distance to calculate
            Note:
                Valid values are 1 or 2; if an invalid value is passed, \
                defaults to 2 """
        return self._distance

    @distance.setter
    def distance(self, val):
        """ set the distance parameter """
        tmp = 2
        try:
            int(val)
            if val > 0 and val <= 2:
                tmp = val
        except (ValueError, TypeError):
            pass
        self._distance = tmp

    def split_words(self, text):
        """ Split text into individual `words` using either a simple whitespace
            regex or the passed in tokenizer
            Args:
                text (str): The text to split into individual words
            Returns:
                list(str): A listing of all words in the provided text """
        text = ENSURE_UNICODE(text)
        return self._tokenizer(text)

    def export(self, filepath, encoding="utf-8", gzipped=True):
        """ Export the word frequency list for import in the future
             Args:
                filepath (str): The filepath to the exported dictionary
                encoding (str): The encoding of the resulting output
                gzipped (bool): Whether to gzip the dictionary or not """
        data = json.dumps(self.word_frequency.dictionary, sort_keys=True)
        write_file(filepath, encoding, gzipped, data)

    def word_probability(self, word, total_words=None):
        """ Calculate the probability of the `word` being the desired, correct
            word
            Args:
                word (str): The word for which the word probability is \
                calculated
                total_words (int): The total number of words to use in the \
                calculation; use the default for using the whole word \
                frequency
            Returns:
                float: The probability that the word is the correct word """
        if total_words is None:
            total_words = self._word_frequency.total_words
        word = ENSURE_UNICODE(word)
        return self._word_frequency.dictionary[word] / total_words

    def correction(self, word):
        """ The most probable correct spelling for the word
            Args:
                word (str): The word to correct
            Returns:
                str: The most likely candidate """
        word = ENSURE_UNICODE(word)
        candidates = list(self.candidates(word))
        return max(sorted(candidates), key=self.word_probability)

    def candidates(self, word):
        """ Generate possible spelling corrections for the provided word up to
            an edit distance of two, if and only when needed
            Args:
                word (str): The word for which to calculate candidate spellings
            Returns:
                set: The set of words that are possible candidates """
        word = ENSURE_UNICODE(word)
        if self.known([word]):  # short-cut if word is correct already
            return {word}

        if not self._check_if_should_check(word):
            return {word}

        # get edit distance 1...
        res = [x for x in self.edit_distance_1(word)]
        tmp = self.known(res)
        if tmp:
            return tmp
        # if still not found, use the edit distance 1 to calc edit distance 2
        if self._distance == 2:
            tmp = self.known([x for x in self.__edit_distance_alt(res)])
            if tmp:
                return tmp
        return {word}

    def known(self, words):
        """ The subset of `words` that appear in the dictionary of words
            Args:
                words (list): List of words to determine which are in the \
                corpus
            Returns:
                set: The set of those words from the input that are in the \
                corpus """
        words = [ENSURE_UNICODE(w) for w in words]
        tmp = [w if self._case_sensitive else w.lower() for w in words]
        return set(
            w
            for w in tmp
            if w in self._word_frequency.dictionary
            and self._check_if_should_check(w)
        )

    def unknown(self, words):
        """ The subset of `words` that do not appear in the dictionary
            Args:
                words (list): List of words to determine which are not in the \
                corpus
            Returns:
                set: The set of those words from the input that are not in \
                the corpus """
        words = [ENSURE_UNICODE(w) for w in words]
        tmp = [
            w if self._case_sensitive else w.lower()
            for w in words
            if self._check_if_should_check(w)
        ]
        return set(w for w in tmp if w not in self._word_frequency.dictionary)

    def edit_distance_1(self, word):
        """ Compute all strings that are one edit away from `word` using only
            the letters in the corpus
            Args:
                word (str): The word for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance one from the \
                provided word """
        word = ENSURE_UNICODE(word).lower() if not self._case_sensitive else ENSURE_UNICODE(word)
        if self._check_if_should_check(word) is False:
            return {word}
        letters = self._word_frequency.letters
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edit_distance_2(self, word):
        """ Compute all strings that are two edits away from `word` using only
            the letters in the corpus
            Args:
                word (str): The word for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance two from the \
                provided word """
        word = ENSURE_UNICODE(word).lower() if not self._case_sensitive else ENSURE_UNICODE(word)
        return [
            e2 for e1 in self.edit_distance_1(word) for e2 in self.edit_distance_1(e1)
        ]

    def __edit_distance_alt(self, words):
        """ Compute all strings that are 1 edits away from all the words using
            only the letters in the corpus
            Args:
                words (list): The words for which to calculate the edit distance
            Returns:
                set: The set of strings that are edit distance two from the \
                provided words """
        words = [ENSURE_UNICODE(w) for w in words]
        tmp = [
            w if self._case_sensitive else w.lower()
            for w in words
            if self._check_if_should_check(w)
        ]
        return [e2 for e1 in tmp for e2 in self.known(self.edit_distance_1(e1))]

    def _check_if_should_check(self, word):
        if len(word) == 1 and word in string.punctuation:
            return False
        if len(word) > self._word_frequency.longest_word_length + 3:  # magic number to allow removal of up to 2 letters.
            return False
        try:  # check if it is a number (int, float, etc)
            float(word)
            return False
        except ValueError:
            pass

        return True


class WordFrequency(object):


    __slots__ = [
        "_dictionary",
        "_total_words",
        "_unique_words",
        "_letters",
        "_tokenizer",
        "_case_sensitive",
        "_longest_word_length"
    ]

    def __init__(self, tokenizer=None, case_sensitive=False):
        self._dictionary = Counter()
        self._total_words = 0
        self._unique_words = 0
        self._letters = set()
        self._case_sensitive = case_sensitive
        self._longest_word_length = 0

        self._tokenizer = _parse_into_words
        if tokenizer is not None:
            self._tokenizer = tokenizer

    def __contains__(self, key):
        """ turn on contains """
        key = ENSURE_UNICODE(key)
        key = key if self._case_sensitive else key.lower()
        return key in self._dictionary

    def __getitem__(self, key):
        """ turn on getitem """
        key = ENSURE_UNICODE(key)
        key = key if self._case_sensitive else key.lower()
        return self._dictionary[key]

    def pop(self, key, default=None):
        key = ENSURE_UNICODE(key)
        key = key if self._case_sensitive else key.lower()
        return self._dictionary.pop(key, default)

    @property
    def dictionary(self):

        return self._dictionary

    @property
    def total_words(self):

        return self._total_words

    @property
    def unique_words(self):

        return self._unique_words

    @property
    def letters(self):

        return self._letters

    @property
    def longest_word_length(self):

        return self._longest_word_length

    def tokenize(self, text):

        text = ENSURE_UNICODE(text)
        for word in self._tokenizer(text):
            yield word if self._case_sensitive else word.lower()

    def keys(self):

        for key in self._dictionary.keys():
            yield key

    def words(self):

        for word in self._dictionary.keys():
            yield word

    def items(self):

        for word in self._dictionary.keys():
            yield word, self._dictionary[word]

    def load_dictionary(self, filename, encoding="utf-8"):

        with load_file(filename, encoding) as data:
            data = data if self._case_sensitive else data.lower()
            self._dictionary.update(json.loads(data))
            self._update_dictionary()

    def load_text_file(self, filename, encoding="utf-8", tokenizer=None):

        with load_file(filename, encoding=encoding) as data:
            self.load_text(data, tokenizer)

    def load_text(self, text, tokenizer=None):

        text = ENSURE_UNICODE(text)
        if tokenizer:
            words = [x if self._case_sensitive else x.lower() for x in tokenizer(text)]
        else:
            words = self.tokenize(text)

        self._dictionary.update(words)
        self._update_dictionary()

    def load_words(self, words):

        words = [ENSURE_UNICODE(w) for w in words]
        self._dictionary.update(
            [word if self._case_sensitive else word.lower() for word in words]
        )
        self._update_dictionary()

    def add(self, word):

        word = ENSURE_UNICODE(word)
        self.load_words([word])

    def remove_words(self, words):

        words = [ENSURE_UNICODE(w) for w in words]
        for word in words:
            self._dictionary.pop(word if self._case_sensitive else word.lower())
        self._update_dictionary()

    def remove(self, word):

        word = ENSURE_UNICODE(word)
        self._dictionary.pop(word if self._case_sensitive else word.lower())
        self._update_dictionary()

    def remove_by_threshold(self, threshold=5):

        keys = [x for x in self._dictionary.keys()]
        for key in keys:
            if self._dictionary[key] <= threshold:
                self._dictionary.pop(key)
        self._update_dictionary()

    def _update_dictionary(self):
        self._longest_word_length = 0
        self._total_words = sum(self._dictionary.values())
        self._unique_words = len(self._dictionary.keys())
        self._letters = set()
        for key in self._dictionary:
            if len(key) > self._longest_word_length:
                self._longest_word_length = len(key)
            self._letters.update(key)

#spell checking algo ends here
# Create your views here.
@login_required(login_url='/login/')
def seat_render(request):
    print(request.path)
    return render(request,'ap/seat_pattern2.html',{"f":"disabled","k":2})

def seat_con(request):
    x=request.POST.get("seat-assignment")

    return HttpResponseRedirect('/seat_booking/')

def login_render(request):
    return render(request,'ap/login.html')

def register_render(request):
    return render(request,'ap/register.html')

def register_auth(request):

    first_name=request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    username = request.POST.get('username')
    password = request.POST.get('pass')
    rep_password = request.POST.get('repeat-pass')
    if password==rep_password:
        if User.objects.filter(username=username).exists():
            messages.info(request,"Username Taken")
            return HttpResponseRedirect('/register/')
        elif User.objects.filter(email=email).exists():
            messages.info(request,"email taken")
            return HttpResponseRedirect('/register/')
        else:
            user = User.objects.create_user(username=username, password=password, first_name=first_name,last_name=last_name, email=email)
            user.save()
            userid=None
            while(True):
                userid=randint(1000,9999)
                if userinfo.objects.filter(userid=userid).exists():
                    pass;
                else:
                    s=userinfo(userid=userid,user=user)
                    s.save()
                    break


            return HttpResponseRedirect('/login/')
    else:
        messages.info(request, "Passwords Didnt Match!!!!!")
        return HttpResponseRedirect('/register/')

def login_auth(request):
    user=authenticate(username=request.POST.get('username'),password=request.POST.get('password'))

    if user is not None:
        login(request,user)
        user1=User.objects.get(username=request.user.username)
        user2=userinfo.objects.get(user=user1)
        while True:
            login_id="IN"+str(randint(1000,4000))
            if login_log.objects.filter(login_id=login_id).exists()==False:
                login_log(login_id=login_id,login_date_time=datetime.datetime.now(),user=user2).save()
                break

        return HttpResponseRedirect('/enqiry/')
    else:
        return HttpResponseRedirect('/login/')

def logout_view(request):
    u=User.objects.get(username=request.user.username)
    u1=userinfo.objects.get(user=u)
    l1=login_log.objects.filter(user=u1)
    mul=[i.login_date_time for i in l1]
    max1=max(mul)
    index=mul.index(max1)
    l1=l1[index]
    logout_log(login_id=l1,logout_date=datetime.datetime.now()).save()
    logout(request)
    return HttpResponseRedirect('/login/')

def enqiury(request):

    if request.user.is_authenticated:
        f=True
        arr=[]
        city=city_code.objects.all()
        for i in city:
            arr.append(i.city_name)
        arr.sort()
    else:
        f=False
        arr = []
        city = city_code.objects.all()
        for i in city:
            arr.append(i.city_name)
        arr.sort()
    return render(request,'ap/enqiry.html',{"login":f,'c':arr})

def contact(request):
    f=flight_info.objects.all()
    c=comment.objects.all()
    if 'term' in request.GET:

        qs = auto_correction.objects.filter(Title__icontains=request.GET.get('term'))
        titles = list()
        for product in qs:
            titles.append(product.title)
        # titles = [product.title for product in qs]
        return JsonResponse(titles, safe=False)
    return render(request,"ap/contact.html",{"f":f,"c":c})

#for faking the data
def faker(request):
    all=city_code.objects.all()
    s=[]
    flight_id_array=[]
    classes=["BC","EC","FC"]
    date_dic={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    for i in all:
        s.append(i.IATA)
    flight_object_array=flight_info.objects.all()
    for i in flight_object_array:
        flight_id_array.append(i.flight_id)

    for i in range(10000):
        c1=choice(s)#for slelcting city code
        c2 = choice(s)
        if c1!=c2:
            d1=city_code.objects.filter(IATA=c1)#whole city code module depearture
            d2=city_code.objects.filter(IATA=c2)#arrival city module
            choice_of_class=choice(classes)
            if choice_of_class=="EC":
                price_of_flight=uniform(10000,60000)
            elif choice_of_class=="BC":
                price_of_flight=uniform(50000,100000)
            else:
                price_of_flight=uniform(90000,200000)

            year=choice([2020,2021])
            date=randint(1,29)
            if year==2020:
                month=randint(10,12)
            else:
                month=randint(1,12)

            fake = Faker()
            departure_datetime=fake.date_time_this_year(after_now=True,before_now=False)
            duration = randint(1, 1740)
            hours=duration//60
            min=(duration/60-hours)*60
            arrival_datetime=departure_datetime+datetime.timedelta(hours=hours,minutes=min)
            flight_id=choice(flight_id_array)
            leg_id=str(departure_datetime)+" "+flight_id
            f=flight_info.objects.get(flight_id=flight_id)

            if leg.objects.filter(flight_id=f, date_time_departure_stamp=departure_datetime,date_time_arrival_stamp=arrival_datetime).exists() == False:
                l = leg(leg_id=leg_id, from_place=c1, to_place=c2, duration=duration, flight_id=f,date_time_departure_stamp=departure_datetime, date_time_arrival_stamp=arrival_datetime)
                l.save()
    return HttpResponseRedirect("/enqiry/")

def show_flights(request):
    if request.user.is_authenticated:
        user=request.user
        dep=request.POST.get('from')
        arr=request.POST.get('to')
        dep_date=request.POST.get("departure")
        arri_date=request.POST.get("return")
        passe=request.POST.get('number')
        way=request.POST.get('trip')
        c1=city_code.objects.get(city_name=dep)
        c2=city_code.objects.get(city_name=arr)
        dep_date=dep_date[6]+dep_date[7]+dep_date[8]+dep_date[9]+"-"+dep_date[0]+dep_date[1]+"-"+dep_date[3]+dep_date[4]
        l=leg.objects.filter(date_time_departure_stamp__startswith=dep_date,from_place=c1.IATA,to_place=c2.IATA)
        u=User.objects.get(username=user)
        u1=userinfo.objects.get(user=u)
        while True:
            id="E"+str(randint(10000,20000))
            if enquiry.objects.filter(enquiry_id=id).exists()==False:
                break




        e=enquiry(user=u1,enquiry_id=id,search_arri_city=dep,search_depa_city=arr,search_date_time=datetime.datetime.now(),search_for_date=dep_date,search_way_type=1,no_of_pass=int(passe))
        e.save()
    if request.user.is_anonymous:
        dep = request.POST.get('from')
        arr = request.POST.get('to')
        dep_date = request.POST.get("departure")
        arri_date = request.POST.get("return")
        passe = request.POST.get('number')
        way = request.POST.get('trip')
        c1 = city_code.objects.get(city_name=dep)
        c2 = city_code.objects.get(city_name=arr)
        dep_date = dep_date[6] + dep_date[7] + dep_date[8] + dep_date[9] + "-" + dep_date[0] + dep_date[1] + "-" + dep_date[3] + dep_date[4]
        u = User.objects.filter(username=user)
        u1 = userinfo.objects.filter(user=u[0])
        while True:
            id = "E" + str(randint(10000, 20000))
            if enquiry.objects.filter(enquiry_id=id).exists() == False:
                break


    return render(request,'ap/search.html',{'l':l,"id":id})

def seat_booking(request,todo_id,enq_id):
    e=enquiry.objects.get(enquiry_id=enq_id)

    if e.no_of_pass==1:
        return render(request,'ap/seat_pattern.html',{"pass":e.no_of_pass,'leg':todo_id,'enq':enq_id})
    else:
        return render(request,'ap/seat_pattern2.html',{"pass":e.no_of_pass,'leg':todo_id,'enq':enq_id})

def process(request):
    spell = SpellChecker()
    # os.path.join(BASE_DIR,"package.json")
    #spell.word_frequency.load_dictionary('./package.json')
    name=request.user.username
    u1=User.objects.get(username=request.user)
    u=userinfo.objects.get(user=u1)
    flight_no=request.POST.get('from')
    f1=flight_info.objects.get(flight_id=flight_no)
    while True:
        comment_id="C"+str(randint(1000,3000))
        if comment.objects.filter(comment_id=comment_id).exists()== False:

            break
    date=request.POST.get('date')

    list1=date.split("/")
    date=list1[2]+"-"+list1[1]+"-"+list1[0]
    comment1=request.POST.get('message')
    comment1=comment1.split(" ")
    print(comment1,1)
    index_of_misspelled=[]
    index_of_abbri=[]
    for i in range(len(comment1)):
        if shortcuts.objects.filter(shortcut=comment1[i].lower().rstrip('\r\n')).exists():
            c=shortcuts.objects.get(shortcut=comment1[i].rstrip('\r\n'))
            index_of_abbri.append(i)
            comment1[i]=c.abbri

    comment2=[]
    for i in range(len(comment1)):
        if i not in index_of_abbri:
            comment2.append(comment1[i])
    misspelled = spell.unknown(comment2)
    misspelled1 = list(misspelled)
    
    for i in range(len(misspelled1)):
        if misspelled1[i] in comment1 :
            for j in range(len(comment1)):
                if misspelled1[i]==comment1[j]:
                    index_of_misspelled.append(j)
                    break


    for i in range(len(misspelled1)):

        comment1[index_of_misspelled[i]]=spell.correction(misspelled1[i]).rstrip("\n ")

    corrected_code=""
    for i in comment1:
        corrected_code+=i+" "
    print(corrected_code)
    c=comment(comment_id=comment_id,user=u,flight_id=f1,date_req=date,org_comm=request.POST.get('message'),exp1=corrected_code,date_time=datetime.datetime.now())
    c.save()
    return HttpResponseRedirect('/contact/')

#otp process starts here

def otpprocess(request):
    email = request.POST.get('username')
    if User.objects.filter(email=email).exists():
        otp = randint(100000, 200000)
        start_time = datetime.datetime.now()
        expiry_time = start_time + datetime.timedelta(minutes=5)
        u=User.objects.get(email=email)
        subject = 'reset of your flight login password'
        while True:
            otp_id="O"+str(randint(100,999))
            if one_time_password.objects.filter(otp_id=otp_id).exists()==False:
                break
        message = f'Hi {u.username}, your otp for your password change {otp} and otp id{otp_id} (for sequrity purpose). This otp is valid upto 5 min'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [u.email, ]
        send_mail(subject, message, email_from, recipient_list)
        u1=userinfo.objects.get(user=u)
        status="T"
        o=one_time_password(otp=otp,status=status,start_time=start_time,expiry_time=expiry_time,user_id=u1,otp_id=otp_id)
        o.save()
        con="True"
    return render(request,'ap/otp.html',{'con':con})

def name_otp(request):
    return render(request,'ap/name_otp.html')

def check_otp(request):
    otp_id=request.POST.get("otp_id")
    otp=request.POST.get("otp")

    one=one_time_password.objects.get(otp_id=otp_id)

    now=datetime.datetime.now()
    utc = pytz.UTC
    now=timezone.now()


    x=one_time_password.objects.get(user_id=one.user_id,start_time=one.start_time)
    if x.expiry_time>now:
        if x.otp==int(otp):

             return render(request,'ap/change_password.html',{"otp":otp_id})
        else:
            messages.info(request, "otp Null")
            return render(request,'ap/name_otp.html')
    else:
        messages.info(request,"OTP expired")
        return render(request,'ap/name_otp.html')

def change_password(request,otp_id):
    o=one_time_password.objects.get(otp_id=otp_id)
    u=User.objects.get(username=o.user_id.user.username)
    print(o.user_id.user.username)
    if request.POST.get('confirm_password')==request.POST.get('password'):
        password=request.POST.get('password')
        print(type(password))
        u.set_password(password)
        u.save()

        messages.info(request, "Password changed")
        return HttpResponseRedirect('/login/')
    else:
        messages.info(request, "Password Dosent match")
        return HttpResponseRedirect('/change_password/{}/'.format(otp_id))

#otp process ends here

def faker1(request):
    def freq(str):
        str = str.split()
        str2 = []
        for i in str:
            if i not in str2:
                str2.append(i)

        return str.count(str2[0])





    dirpath = os.path.dirname(os.path.abspath(__file__))
    chap_dirpath = os.path.join(BASE_DIR, "engmix.txt")
    f = open( "app/engmix.txt", "r",encoding='utf-8',errors='ignore')

    for i in f:

        auto_correction(title=i,frequency=freq(i)).save()
    f.close()
    return HttpResponseRedirect("/enqiry/")

def dic(request):
    chap_dirpath = os.path.join(BASE_DIR, "package.json")
    string="string"
    spell = SpellChecker(language=None, case_sensitive=False)
    spell.word_frequency.load_dictionary('./package.json')
    misspelled = spell.unknown(['the'])
    for word in misspelled:
        print(spell.correction(word.rstrip("\n")))
    return HttpResponseRedirect("/enqiry/")

def booking(request,enq,leg1):
    arr=[]
    enq_obj=enquiry.objects.get(enquiry_id=enq)
    for i in range(72):
        arr.append(request.POST.get('seat-assignment{}'.format(i)))
    new_arr=[]
    c1 =city_code.objects.get(city_name=enq_obj.search_depa_city)
    c2=city_code.objects.get(city_name=enq_obj.search_arri_city)
    l=leg.objects.get(leg_id=leg1)
    price=l.total_price

    price=price+price*(randint(1,12)/100)
    price1=price

    price=price*enq_obj.no_of_pass
    for i in arr:
        if i is not None:
            new_arr.append(i)
    return render(request,'ap/pricing.html',{"enq":enq_obj,'c1':c1,'c2':c2,"r":range(1,enq_obj.no_of_pass+1),"leg":leg1,"seats":new_arr,"price":price,"obj":l,"price1":price1})

def payment(request,leg1):
    u=request.user
    u1=User.objects.get(username=u)
    u2=userinfo.objects.get(user_id=u1)
    first_name=[]
    last_name=[]
    age=[]
    seats=[]
    s=request.POST.get("flag")
    s=s.split(",")
    seats.append(s[0][2:len(s[0])-1])
    for i in range(len(s)):
        if i!=0 and i!=len(s)-1:
            seats.append(s[i][2:len(s[i])-1])
    seats.append(s[len(s)-1][2:len(s[0])-1])
    l=leg.objects.get(leg_id=leg1)
    today=l.date_time_departure_stamp
    board=today-datetime.timedelta(minutes=30)
    bcc=board.strftime("%m/%d/%Y, %H:%M:%S")
    bcc=bcc.split(",")
    today1=l.date_time_arrival_stamp
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")
    date_time=date_time.split(",")
    date_time1 = today1.strftime("%m/%d/%Y, %H:%M:%S")
    date_time1 = date_time1.split(",")

    while True:
        trans_id = "#TRA" + str(randint(10000, 99999))
        if passengers.objects.filter(transaction=trans_id).exists()==False:
            break

    for i in range(len(seats)):
        a=request.POST.get("firstName{}".format(i+1))
        b=request.POST.get("lastName{}".format(i+1))
        c=request.POST.get("age{}".format(i+1))

        if a!=None and b!=None and c!=None:
            first_name.append(a)
            last_name.append(b)
            age.append(int(c))
            p=passengers(leg=l,seat_id=seats[i],first_name=first_name[i],last_name=last_name[i],age=age[i],user=u2,transaction=trans_id)
            p.save()
    c1 = city_code.objects.get(IATA=l.from_place)
    c2 = city_code.objects.get(IATA=l.to_place)
    print(u1.email)
    subject = 'Sucessfull flight payment'
    message = f'Hi {u1.username}, your payment is sucessfull.\n your transaction id is {trans_id} '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [u1.email, ]
    send_mail(subject, message, email_from, recipient_list)

    return render(request,'ap/iter.html',{"first":first_name,"last":last_name,"age":age,"seats":seats,"pass":range(len(seats)),"l":l,"c1":c1,"c2":c2,"arri_time":date_time1[1],"dep_time":date_time[1],"date":date_time[0],"board":bcc[1]})

def status(request):
    return render(request,'ap/trans.html')

def status_check(request):
    id=request.POST.get('Transaction')
    p=passengers.objects.filter(transaction=id)
    l=leg.objects.get(leg_id=p[0].leg.leg_id)
    today = l.date_time_departure_stamp
    board = today - datetime.timedelta(minutes=30)
    bcc = board.strftime("%m/%d/%Y, %H:%M:%S")
    bcc = bcc.split(",")
    today1 = l.date_time_arrival_stamp
    date_time = today.strftime("%m/%d/%Y, %H:%M:%S")
    date_time = date_time.split(",")
    date_time1 = today1.strftime("%m/%d/%Y, %H:%M:%S")
    date_time1 = date_time1.split(",")
    c1=city_code.objects.get(IATA=p[0].leg.from_place)
    c2=city_code.objects.get(IATA=p[0].leg.to_place)
    return render(request,'ap/trans1.html',{"p":p,"c1":c1,"c2":c2,"board":bcc[0],"arri_time":date_time1[1],"dep_time":date_time[1],"date":date_time[0]})

#
# def words(text): return re.findall(r'\w+', text.lower())
#
#
# WORDS = Counter(words(open('engmix.txt', "r", encoding='utf-8', errors='ignore').read()))
#
#
# def P(word, N=sum(WORDS.values())):
#     return WORDS[word] / N
#
#
# def correction(word):
#     return max(candidates(word), key=P)
#
#
# def candidates(word):
#     return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])
#
#
# def known(words):
#     return set(w for w in words if w in WORDS)
#
#
# def edits1(word):
#     letters = 'abcdefghijklmnopqrstuvwxyz'
#     splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
#     deletes = [L + R[1:] for L, R in splits if R]
#     transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
#     replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
#     inserts = [L + c + R for L, R in splits for c in letters]
#     return set(deletes + transposes + replaces + inserts)
#
#
# def edits2(word):
#     return (e2 for e1 in edits1(word) for e2 in edits1(e1))
