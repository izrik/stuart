#!/usr/bin/env python

import argparse
import random

from flask import Flask, render_template_string, redirect, render_template
from sqlalchemy import create_engine, MetaData
from flask_login import UserMixin, LoginManager, \
    login_user, logout_user, AnonymousUserMixin
from flask_blogging import SQLAStorage, BloggingEngine

secret_key = 'secret'
port = 1177
debug = False
db_uri = 'sqlite:////tmp/blog.db'
url_prefix = ''  # e.g. '/blog'
disqus_sitename = ''
sitename = 'Site Name'
siteurl = 'http://localhost:1177'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', type=str, default=secret_key, help='')
    parser.add_argument('--port', type=int, default=port, help='')
    parser.add_argument('--debug', action='store_true', help='')
    parser.add_argument('--db-uri', type=str, action='store', default=db_uri)

    parser.add_argument('--url-prefix', type=str, default=url_prefix, help='')
    parser.add_argument('--disqus-sitename', type=str, default=disqus_sitename,
                        help='')
    parser.add_argument('--sitename', type=str, default=sitename, help='')
    parser.add_argument('--siteurl', type=str, default=siteurl, help='')

    parser.add_argument('--create-secret-key', action='store_true')

    args = parser.parse_args()

    if args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in xrange(48)))
        print(key)
        exit(0)

    secret_key = args.secret_key
    port = args.port
    debug = args.debug
    db_uri = args.db_uri
    url_prefix = args.url_prefix
    disqus_sitename = args.disqus_sitename
    sitename = args.sitename
    siteurl = args.siteurl

app = Flask(__name__)

app.config["SECRET_KEY"] = secret_key  # for WTF-forms and login
app.config["BLOGGING_URL_PREFIX"] = url_prefix
app.config["BLOGGING_DISQUS_SITENAME"] = disqus_sitename
app.config["BLOGGING_SITENAME"] = sitename
app.config["BLOGGING_SITEURL"] = siteurl

# extensions
engine = create_engine(db_uri)
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


if url_prefix and url_prefix != '/':
    @app.route("/")
    def index():
        return render_template("index.html", config=blog_engine.config)


@app.route("/login/")
def login():
    user = User("izrik", "izrik@izrik.com")
    login_user(user)
    return redirect("/")


@app.route("/logout/")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":

    print('Url prefix: {}'.format(app.config["BLOGGING_URL_PREFIX"]))
    print('Site name: {}'.format(app.config["BLOGGING_SITENAME"]))
    print('Site url: {}'.format(app.config["BLOGGING_SITEURL"]))
    print('Disqus site name: {}'.format(
        app.config["BLOGGING_DISQUS_SITENAME"]))

    app.run(debug=debug, port=port, use_reloader=debug)
