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
