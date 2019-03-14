from django.utils import timezone
from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock


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
    message_id = blocks.CharBlock(required=False)
    timestamp = blocks.DateTimeBlock(required=False)

    def clean(self, value):
        """Add timestamp if timestamp is empty.
        This would happen when an block is added via de admin.
        """
        if not value['timestamp']:
            value['timestamp'] = timezone.now()
        return super().clean(value)


class TextUpdate(AbstractUpdateBlock):
    message = blocks.CharBlock()

    class Meta:
        template = 'website/blocks/text.html'


class EmbedUpdate(AbstractUpdateBlock):
    embed = EmbedBlock()

    class Meta:
        template = 'website/blocks/embed.html'


class ImageUpdate(AbstractUpdateBlock):
    image = ImageChooserBlock()

    class Meta:
        template = 'website/blocks/image.html'
