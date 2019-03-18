# Wagtail Live

This was my inspiration for high speed publishing:

https://nos.nl/liveblog/2274672-historische-zege-ajax-in-bernabeu-1-4-voor-het-eerst-sinds-2003-bij-laatste-acht.html

but it could have been faster and more fun, with Wagtail and Slack!

## Installation

1. Create a database

```bash
createdb liveblog
```

2. Add your Slack credentials

```bash
cp liveblog/settings/.env.example liveblog/settings/.env
```

3. Set up the app in a virtual environment:

```bash
virtualenv env -p python3.7
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

4. Log in to the admin. Create a homepage (index) and a child LiveBlog page.

## Use ngrok to expose your local web server

```bash
brew cask install ngrok
ngrok http 8000
```

http://localhost:4040/inspect/http

## Configure the Slack app

https://api.slack.com/apps/AGTF9MAMN/general?

Event API endpoint https://[HASH].ngrok.io/api/event/

## Start Redis

```bash
brew services start redis
```

## Slack documentation

- https://api.slack.com/bot-users
- https://api.slack.com/actions
- https://api.slack.com/docs/verifying-requests-from-slack
