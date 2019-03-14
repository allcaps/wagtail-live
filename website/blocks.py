from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock


class Embed(EmbedBlock):
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'help_text': "Paste a social media detail page url."
            })
        super(Embed, self).__init__(*args, **kwargs)

    class Meta:
        label = 'Embed'
        icon = 'media'
        template = 'website/blocks/embed.html'


class AbstractUpdateBlock(blocks.StructBlock):
    message_id = blocks.CharBlock()
    timestamp = blocks.DateTimeBlock()


class TextUpdate(AbstractUpdateBlock):
    message = blocks.CharBlock()

    class Meta:
        template = 'website/blocks/text.html'
