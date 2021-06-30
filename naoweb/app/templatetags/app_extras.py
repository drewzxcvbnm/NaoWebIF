from django import template

register = template.Library()


@register.filter
def mapget(h, key):
    return h[key]
