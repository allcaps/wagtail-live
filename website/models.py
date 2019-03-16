import re
from datetime import datetime, timedelta

from django.db import models
from django.db.models.signals import ModelSignal
from django.utils.timezone import now
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from website.blocks import EmbedUpdate, ImageUpdate, TextUpdate
from wagtail.embeds.oembed_providers import all_providers


blog_update = ModelSignal(providing_args=['instance', 'removals', 'renders'],
                          use_caching=True)


TEXT = 'text'
IMAGE = 'image'
EMBED = 'embed'

BLOCK_TYPES = [
    (TEXT, TextUpdate()),
    (IMAGE, ImageUpdate()),
    (EMBED, EmbedUpdate()),
]


def construct_text_block(update):
    return {
        'type': TEXT,
        'value': {
            'message_id': update.slack_id,
            'timestamp': update.timestamp,
            'message': update.raw_update,
        }
    }


def construct_image_block(update):
    """Not implemented yet, do text"""
    return construct_text_block(update)


def construct_embed_block(update):
    return {
        'type': EMBED,
        'value': {
            'message_id': update.slack_id,
            'timestamp': update.timestamp,
            'embed': update.raw_update[1:-1],  # Strip leading `<` and trailing `>`.
        }
    }


HANDLERS = {
    TEXT: construct_text_block,
    IMAGE: construct_image_block,
    EMBED: construct_embed_block,
}


def get_block_type(update):
    """
    Get block type

    :param update: The posted slack message (dict)
    :return: TEXT, IMAGE, EMBED (string)
    """
    for provider in all_providers:
        for url_pattern in provider.get('urls', []):
            # Some how Slack links start with `<` and end with `>`.
            # I strip those off.
            val = update.raw_update[1:-1]
            if bool(re.match(url_pattern, val)):
                return EMBED
    return TEXT


class LiveBlog(Page):
    body = StreamField(BLOCK_TYPES, blank=True)
    slack_channel = models.CharField(blank=True, max_length=80)
    last_updated = models.DateTimeField(
        default=datetime.min + timedelta(days=1))

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        # InlinePanel('live_updates'),
    ]

    @property
    def group_name(self):
        return 'liveblog-{}'.format(self.pk)

    def update(self):
        """ apply all pending updates """
        def get_pending_updates():
            return PendingUpdate.objects.filter(
                live_blog=self,
                timestamp__gt=self.last_updated).order_by('-timestamp')

        def mid(stream_value):
            # get message id for stream_value
            return stream_value.value['message_id']

        if self.locked:
            return

        # Set lock
        self.locked = True
        self.save()

        try:
            # Apply updates
            pending_updates = get_pending_updates()
            items = self.body.stream_data
            updated = []
            deleted = []
            for update in pending_updates:
                if update.update_type == PendingUpdate.NEW_MESSAGE:
                    block_type = get_block_type(update)
                    block = HANDLERS[block_type](update)
                    items.append(block)
                    updated.append(update.slack_id)
                elif update.update_type == PendingUpdate.EDIT:
                    # Find message to update. Text block updates only.
                    for option in items:
                        if option['value']['message_id'] == update.slack_id:
                            item = option
                            break
                    else:
                        # No match found to edit :-(
                        continue
                    if item['type'] == TEXT:
                        item['value']['message'] = update.raw_update
                        updated.append(update.slack_id)
                elif update.update_type == PendingUpdate.DELETE:
                    # Find message to delete
                    for option in items:
                        if option['value']['message_id'] == update.slack_id:
                            items.remove(option)
                            deleted.append(update.slack_id)
                            break
                    else:
                        # No match found to delete :-(
                        continue

            # TODO: Maybe order stream data items on timestamp!
            self.last_updated = now()
            self.save()
            # These are handled
            pending_updates.delete()

            # compiled_version = LiveBlog.objects.get(pk=self.pk)
            updated_blocks = [block for block in self.body
                              if mid(block) in updated]
            renders = {mid(value): value.render_as_block()
                       for value in updated_blocks}

            blog_update.send(sender=LiveBlog, instance=self,
                             renders=renders, removals=deleted)
        finally:
            # Unset lock
            self.locked = False
            self.save()

        # Test if there were new updates while the page was locked and
        # publishing. This would still be the moment to handle them
        pending_updates = get_pending_updates()
        if pending_updates:
            self.update()


class PendingUpdate(models.Model):
    """ Pending updates will be added asap! """
    NEW_MESSAGE = 1
    EDIT = 2
    DELETE = 3

    update_type = models.PositiveIntegerField()
    live_blog = models.ForeignKey(LiveBlog, on_delete=models.CASCADE)
    slack_id = models.CharField(max_length=40)
    raw_update = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


class HomePage(Page):
    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        ctx.update({
            'pages': LiveBlog.objects.live()
        })
        return ctx
