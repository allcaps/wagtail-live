import json

import channels.layers
from asgiref.sync import async_to_sync

from django.db.models.signals import post_save
from django.dispatch import receiver

from website.models import blog_update, LiveBlog
from .models import Snippet


def send_message(event):
    """
    Call back function to send message to the browser
    """
    message = event['text']
    channel_layer = channels.layers.get_channel_layer()
    # Send message to WebSocket
    async_to_sync(channel_layer.send)(text_data=json.dumps(
        message
    ))


@receiver(blog_update, sender=LiveBlog)
def update_job_status_listeners(sender, instance, num_updates, **kwargs):
    """
    Sends job status to the browser when a Job is modified
    """
    group_name = instance.group_name

    message = {
        'type': 'chat_message',
        'message': '{} updates!'.format(num_updates),
    }

    channel_layer = channels.layers.get_channel_layer()

    async_to_sync(channel_layer.group_send)(group_name, message)
