from django import template

register = template.Library()


@register.filter
def mapget(h, key):
    return h[key]


@register.filter
def indexOf(li, el):
    for i, v in enumerate(li):
        if v is el:
            return i
    return -1
