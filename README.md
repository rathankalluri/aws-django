# aws-django
A Django app with boto3, AWS to create a custom API and Web view.

This project is licensed under the terms of the MIT license.

The technology stack used in the project are :

- Django 2.0
- Slack
- DialogFlow
- Heroku

## Django

This is the core business logic, which gets the entities posted by the DialogFlow and also responds back with required data in Json format so that it can be displayed in slack.

## Slack

Slack is the messaging channel I have used here as this is mostly related to business/servers and not a normal chat.

## DialogFlow

The NLP brain for the project, which will read/identify the entites from the natural language posted in the slack channel.

## Heroku

[Heroku](https://www.heroku.com/) is the free hosting provider for this Djanog code.
