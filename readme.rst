Install
-------

# Create a db
createdb liveblog

# Add your SLACK credentials
cp liveblog/settings/.env.example liveblog/settings/.env

virtualenv env -p python3.7
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Login to the admin create homepage (index) and a child LiveBlog page.


Public URLs for exposing your local web server
----------------------------------------------

brew cask install ngrok
ngrok http 8000

http://localhost:4040/inspect/http


Configure the Slack app
-----------------------

https://api.slack.com/apps/AGTF9MAMN/general?

Event API endpoint https://[HASH].ngrok.io/api/event/


Start Redis
-----------

brew services start redis


https://api.slack.com/bot-users
https://api.slack.com/actions
https://api.slack.com/docs/verifying-requests-from-slack
