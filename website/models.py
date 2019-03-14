from datetime import datetime

from django.db import models
from django.db.models.signals import ModelSignal
from django.template.defaultfilters import truncatewords
from django.utils.timezone import now
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import InlinePanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from website.blocks import EmbedUpdate, ImageUpdate, TextUpdate

BLOCK_TYPES = [
    ('text', TextUpdate()),
    ('image', ImageUpdate()),
    ('embed', EmbedUpdate()),
]

blog_update = ModelSignal(providing_args=['instance', 'num_updates', 'renders'],
                          use_caching=True)


class LiveBlog(Page):
    body = StreamField(BLOCK_TYPES, blank=True)
    last_updated = models.DateTimeField(default=datetime.min)

    content_panels = Page.content_panels + [
        StreamFieldPanel('body'),
        InlinePanel('live_updates'),
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
            for update in pending_updates:
                if update.update_type == PendingUpdate.NEW_MESSAGE:
                    items.append({
                        'type': 'text',
                        'value': {
                            'message_id': update.slack_id,
                            'timestamp': update.timestamp,
                            'message': update.raw_update,
                        }
                    })
                    updated.append(update.slack_id)
                elif update.update_type == PendingUpdate.EDIT:
                    # Find message to update
                    item = None
                    for option in items:
                        if option['value']['message_id'] == update.slack_id:
                            item = option
                            break
                    else:
                        # No match found to edit :-(
                        continue
                    item['value']['message'] = update.raw_update
                    updated.append(update.slack_id)
            # TODO: Maybe order stream data items on timestamp!
            self.last_updated = now()
            self.save()
            num_updates = int(pending_updates.count())
            # These are handled
            pending_updates.delete()

            # compiled_version = LiveBlog.objects.get(pk=self.pk)
            updated_blocks = [block for block in self.body
                              if mid(block) in updated]
            renders = {mid(value): value.render_as_block()
                       for value in updated_blocks}

            blog_update.send(sender=LiveBlog, instance=self,
                             num_updates=num_updates, renders=renders)
        finally:
            # Unset lock
            self.locked = False
            self.save()

        # Test if there were new updates while the page was locked and
        # publishing. This would still be the moment to handle them
        pending_updates = get_pending_updates()
        if pending_updates:
            self.update()


class Snippet(ClusterableModel):
    page = ParentalKey(
        LiveBlog,
        related_name='live_updates',
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(
        max_length=255,
    )

    def save(self, *args, **kwags):
        super(Snippet, self).save(*args, **kwags)

    def __str__(self):
        return truncatewords(self.message, 20)


class PendingUpdate(models.Model):
    """ Pending updates will be added asap! """
    NEW_MESSAGE = 1
    EDIT = 2

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
