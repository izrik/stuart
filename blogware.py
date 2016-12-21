#!/usr/bin/env python

import argparse
import random
from os import environ

from flask import Flask, render_template_string, redirect, render_template
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, \
    login_user, logout_user, AnonymousUserMixin
from flask_blogging import SQLAStorage, BloggingEngine


class Config(object):
    SECRET_KEY = environ.get('BLOGWARE_SECRET_KEY', 'secret')
    PORT = environ.get('BLOGWARE_PORT', 1177)
    DEBUG = environ.get('BLOGWARE_DEBUG', False)
    DB_URI = environ.get('BLOGWARE_DB_URI', 'sqlite:////tmp/blog.db')
    URL_PREFIX = environ.get('BLOGWARE_URL_PREFIX', '')  # e.g. '/blog'
    DISQUS_SITENAME = environ.get('BLOGWARE_DISQUS_SITENAME', '')
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
    parser.add_argument('--url-prefix', type=str,
                        default=Config.URL_PREFIX, help='')
    parser.add_argument('--disqus-sitename', type=str,
                        default=Config.DISQUS_SITENAME, help='')
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
    Config.URL_PREFIX = args.url_prefix
    Config.DISQUS_SITENAME = args.disqus_sitename
    Config.SITENAME = args.sitename
    Config.SITEURL = args.siteurl


app = Flask(__name__)

app.config["SECRET_KEY"] = Config.SECRET_KEY  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = Config.URL_PREFIX
app.config["BLOGGING_DISQUS_SITENAME"] = Config.DISQUS_SITENAME
app.config["BLOGGING_SITENAME"] = Config.SITENAME
app.config["BLOGGING_SITEURL"] = Config.SITEURL
app.config['SQLALCHEMY_DATABASE_URI'] = Config.DB_URI

# extensions
engine = create_engine(Config.DB_URI)
meta = MetaData()
sql_storage = SQLAStorage(engine, metadata=meta)
blog_engine = BloggingEngine(app, sql_storage)
login_manager = LoginManager(app)
meta.create_all(bind=engine)


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
@blog_engine.user_loader
def load_user(user_id):
    return User("izrik", "izrik@izrik.com")


if Config.URL_PREFIX and Config.URL_PREFIX != '/':
    @app.route("/")
    def index():
        return render_template("index.html", config=blog_engine.config)


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

    print('Url prefix: {}'.format(app.config["BLOGGING_URL_PREFIX"]))
    print('Site name: {}'.format(app.config["BLOGGING_SITENAME"]))
    print('Site url: {}'.format(app.config["BLOGGING_SITEURL"]))
    print('Disqus site name: {}'.format(
        app.config["BLOGGING_DISQUS_SITENAME"]))

    app.run(debug=Config.DEBUG, port=Config.PORT, use_reloader=Config.DEBUG)
