# lsts
A todo list website. 
Check it out here at [lsts.xyz](https://lsts.xyz/).

## Description
This website allows users to keep track of tasks and todos.
It allows users to register an account, log in. User's can then view, create, edit and delete todo lists.
Has forms for creating and editing lists and todo items. Has an email password reset using JWT.
I deployed this app myself on a Linode server remotely through ssh using nginx and gunicorn.

[![](https://i.imgur.com/9KuvKeL.png?1)](https://lsts.xyz/)

## Learned on project
- got a familiarity to Flask web framework
- first database, learned SQLAlchemy ORM with SQLite database
- jinja2 templates for html
- bootstrap/css for styling
- responsive website that handles mobile and desktop views
- bcrypt to hash passwords more securely
- forms and validating the returned data
- JWT for email reset
- dealing with user authentication and logging in and out

## Tech
- Python
- Flask web framework and the following extensions:
  - flask_login
  - flask_mail
  - flask_wtf (forms)
- SQLAlchemy + SQLite for database
- Nginx and Gunicorn hosted on my Linode Ubuntu server
