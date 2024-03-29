# Generated by Django 3.1.1 on 2020-09-28 02:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='auto_correction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('table1', models.CharField(blank=True, max_length=100, null=True)),
                ('table2', models.CharField(blank=True, max_length=100, null=True)),
                ('table3', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='city_code',
            fields=[
                ('city_code', models.CharField(max_length=3, primary_key=True, serialize=False, unique=True)),
                ('city_name', models.CharField(max_length=100)),
                ('airport_name', models.CharField(default='null', max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='flight_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('flight_id', models.CharField(max_length=6)),
                ('models_type', models.CharField(default='tour', max_length=3)),
                ('total_seats', models.IntegerField(default=50)),
            ],
        ),
        migrations.CreateModel(
            name='userinfo',
            fields=[
                ('userid', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='leg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leg_id', models.CharField(max_length=200)),
                ('from_place', models.CharField(max_length=150)),
                ('to_place', models.CharField(max_length=150)),
                ('duration', models.IntegerField(default=0)),
                ('date_time_departure_stamp', models.DateTimeField()),
                ('date_time_arrival_stamp', models.DateTimeField()),
                ('flight_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.flight_info')),
            ],
        ),
        migrations.CreateModel(
            name='enquiry',
            fields=[
                ('enquiry_id', models.IntegerField(primary_key=True, serialize=False)),
                ('search_arri_city', models.CharField(max_length=50)),
                ('search_depa_city', models.CharField(max_length=50)),
                ('search_date_time', models.DateTimeField()),
                ('search_for_date', models.DateField()),
                ('search_way_type', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.userinfo')),
            ],
        ),
    ]
