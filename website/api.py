from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from slackclient import SlackClient

from website.models import Snippet, LiveBlog, PendingUpdate

SLACK_VERIFICATION_TOKEN = getattr(settings, 'SLACK_VERIFICATION_TOKEN', None)
SLACK_BOT_USER_TOKEN = getattr(settings, 'SLACK_BOT_USER_TOKEN', None)
Client = SlackClient(SLACK_BOT_USER_TOKEN)


# https://medium.com/freehunch/how-to-build-a-slack-bot-with-python-using-slack-events-api-django-under-20-minute-code-included-269c3a9bf64e

class Event(APIView):
    def post(self, request, *args, **kwargs):

        slack_message = request.data

        if slack_message.get('token') != SLACK_VERIFICATION_TOKEN:
            return Response(status=status.HTTP_403_FORBIDDEN)

        # Verification challenge
        if slack_message.get('type') == 'url_verification':
            return Response(data=slack_message, status=status.HTTP_200_OK)

        print(slack_message)

        # Handle app event.
        if 'event' in slack_message:
            event = slack_message['event']

            # TODO: This should be a channel2page selection.
            live_blog: LiveBlog = LiveBlog.objects.first()

            if event['type'] == 'message' and 'subtype' not in event:
                PendingUpdate.objects.create(
                    live_blog=live_blog,
                    update_type=PendingUpdate.NEW_MESSAGE,
                    raw_update=slack_message['event']['text'],
                    slack_id=slack_message['event']['client_msg_id']
                )
            elif event['type'] == 'message' \
                    and event.get('subtype') == 'message_changed':
                PendingUpdate.objects.create(
                    live_blog=live_blog,
                    update_type=PendingUpdate.EDIT,
                    raw_update=slack_message['event']['message']['text'],
                    slack_id=slack_message['event']['message']['client_msg_id']
                )
            else:
                # nothing done
                return

            live_blog.update()

            # snippet = Snippet(
            #     page=LiveBlog.objects.first(),  # This should be a channel2page selection.
            #     message=slack_message['event']['text'],
            # )
            # snippet.save()

            # event_message = slack_message.get('event')
            #
            # # ignore bot's own message
            # if event_message.get('subtype') == 'bot_message':
            #     return Response(status=status.HTTP_200_OK)
            #
            # # process user's message
            # user = event_message.get('user')
            # text = event_message.get('text')
            # channel = event_message.get('channel')
            # bot_text = 'Hi <@{}> :wave:'.format(user)
            # if 'hi' in text.lower():
            #     Client.api_call(
            #         method='chat.postMessage',
            #         channel=channel,
            #         text=bot_text
            #     )
            #     return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)
