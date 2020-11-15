from django import template
register = template.Library()

@register.filter
def index1(indexable, i):
    return indexable[i]
