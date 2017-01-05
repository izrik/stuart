#!/usr/bin/env python

import argparse
import random
from os import environ

from flask import Flask, render_template_string, redirect, render_template
from flask_login import UserMixin, LoginManager, \
    login_user, logout_user, AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    SECRET_KEY = environ.get('BLOGWARE_SECRET_KEY', 'secret')
    PORT = environ.get('BLOGWARE_PORT', 1177)
    DEBUG = environ.get('BLOGWARE_DEBUG', False)
    DB_URI = environ.get('BLOGWARE_DB_URI', 'sqlite:////tmp/blog.db')
    SITENAME = environ.get('BLOGWARE_SITENAME', 'Site Name')
    SITEURL = environ.get('BLOGWARE_SITEURL', 'http://localhost:1177')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', type=str,
                        default=Config.SECRET_KEY, help='')
    parser.add_argument('--port', type=int, default=Config.PORT,
                        help='')
    parser.add_argument('--debug', action='store_true', help='',
                        default=Config.DEBUG)
    parser.add_argument('--db-uri', type=str, action='store',
                        default=Config.DB_URI)
    parser.add_argument('--sitename', type=str,
                        default=Config.SITENAME, help='')
    parser.add_argument('--siteurl', type=str,
                        default=Config.SITEURL, help='')

    parser.add_argument('--create-secret-key', action='store_true')

    args = parser.parse_args()

    if args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
        exit(0)

    Config.SECRET_KEY = args.secret_key
    Config.PORT = args.port
    Config.DEBUG = args.debug
    Config.DB_URI = args.db_uri
    Config.SITENAME = args.sitename
    Config.SITEURL = args.siteurl


app = Flask(__name__)

app.config["SECRET_KEY"] = Config.SECRET_KEY  # for WTF-forms and login
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DB_URI

# extensions
login_manager = LoginManager(app)
db = SQLAlchemy(app)


# user class for providing authentication
class User(UserMixin):
    def __init__(self, name, email):
        self.id = name
        self.name = name
        self.email = email

    def get_name(self):
        return self.name

    @property
    def is_authenticated(self):
        return True


class Guest(AnonymousUserMixin):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User("izrik", "izrik@izrik.com")


@app.route("/")
def index():
    return render_template("index.html", config=Config)


@app.route("/login")
def login():
    user = User("izrik", "izrik@izrik.com")
    login_user(user)
    return redirect("/")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":

    print('Site name: {}'.format(Config.SITENAME))
    print('Site url: {}'.format(Config.SITEURL))

    app.run(debug=Config.DEBUG, port=Config.PORT, use_reloader=Config.DEBUG)
