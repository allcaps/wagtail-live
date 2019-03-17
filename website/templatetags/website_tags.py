import emoji
from django import template
from django.template.defaultfilters import stringfilter
from emoji import EMOJI_ALIAS_UNICODE

register = template.Library()

# Update emoji mapping.
EMOJI_ALIAS_UNICODE.update({
    # Smileys
    ':zipper_mouth_face:': '🤐',
    ':upside_down_face:': '🙃',
    ':money_mouth_face:': '🤑',
    ':face_with_head_bandage:': '🤕',
    ':face_with_cowboy_hat:': '🤠',

    # Gestures
    ':spock-hand:': '🖖',
    ':the_horns:': '🤘',
    ':i_love_you_hand_sign:': '🤟',
})


@register.filter(is_safe=True)
@stringfilter
def emojify(val):
    """
    'Python is :thumbs_up:' => 'Python is 👍'

    Unfortunately not all Slack emojis are supported.
    You can add them yourself with `EMOJI_ALIAS_UNICODE.update`.

    :param val: (string)
    :return: (string)
    """
    return emoji.emojize(val, use_aliases=True)
