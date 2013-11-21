from django import template


register = template.Library()

@register.simple_tag
def lookup(dict, key):
    return dict[key]
