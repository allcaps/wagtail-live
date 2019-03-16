import emoji
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def emojify(val):
    """
    'Python is :thumbs_up:' => 'Python is 👍'

    :param val: (string)
    :return: (string)
    """
    return emoji.emojize(val, use_aliases=True)
