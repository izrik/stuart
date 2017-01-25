#!/usr/bin/env python

# blogware - a python blogging system
# Copyright (C) 2016-2017 izrik
#
# This file is a part of blogware.
#
# Blogware is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Blogware is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with blogware.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import random
from itertools import cycle
from os import environ
from datetime import datetime

from flask import Flask, render_template_string, redirect, render_template, \
    request, url_for, flash, Markup
from flask_login import UserMixin, LoginManager, \
    login_user, logout_user, AnonymousUserMixin, current_user, login_required
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from werkzeug.exceptions import ServiceUnavailable, Unauthorized
import git
import gfm
import markdown

try:
    __revision__ = git.Repo('.').git.describe(tags=True, dirty=True,
                                              always=True, abbrev=40)
except git.InvalidGitRepositoryError:
    __revision__ = 'unknown'

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
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--hash-password', action='store')

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
bcrypt = Bcrypt(app)


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


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    date = db.Column(db.DateTime)
    is_draft = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, title, content, date, is_draft=False):
        self.title = title
        self.content = content
        self.date = date
        self.is_draft = is_draft


class Option(db.Model):
    name = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.String(100), nullable=True)

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Options(object):
    @staticmethod
    def get(key, default_value=None):
        option = Option.query.get(key)
        if option is None:
            return default_value
        return option.value

    @staticmethod
    def get_title():
        return Options.get('title', Config.SITENAME)

    @staticmethod
    def get_revision():
        return __revision__

    @staticmethod
    def seq():
        i = 0
        while True:
            yield i
            i += 1

    cycle = cycle

    Config = Config
    config = Config


@login_manager.user_loader
def load_user(user_id):
    return User("izrik", "izrik@izrik.com")


@app.context_processor
def setup_options():
    return {'Options': Options}


@app.template_filter(name='gfm')
def render_gfm(s):
    output = markdown.markdown(s, extensions=['gfm'])
    moutput = Markup(output)
    return moutput


@app.route("/")
def index():
    query = Post.query
    if not current_user.is_authenticated:
        query = query.filter_by(is_draft=False)
    posts = query.order_by(Post.date.desc()).limit(10)
    return render_template("index.html", posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    nvp = Option.query.get('hashed_password')
    if not nvp:
        raise ServiceUnavailable('No password set')
    stored_password = nvp.value
    if not stored_password:
        raise ServiceUnavailable('No password set')
    password = request.form['password']
    if not bcrypt.check_password_hash(stored_password, password):
        flash('Password is invalid', 'error')
        return redirect(url_for('login'))

    user = User("izrik", "izrik@izrik.com")
    login_user(user)
    flash('Logged in successfully')
    # return redirect(request.args.get('next_url') or url_for('index'))
    return redirect(url_for('index'))


@app.route('/post/<post_id>', methods=['GET'])
def get_post(post_id):

    post = Post.query.get(post_id)
    if post.is_draft and not current_user.is_authenticated:
        raise Unauthorized()
    user = current_user
    return render_template('post.html', config=Config, post=post, user=user)


@app.route('/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get(post_id)
    if request.method == 'GET':
        return render_template('edit.html', post=post, config=Config,
                               post_url=url_for('edit_post', post_id=post.id))

    title = request.form['title']
    content = request.form['content']
    is_draft = not (not ('is_draft' in request.form and
                         request.form['is_draft']))
    post.title = title
    post.content = content
    post.is_draft = is_draft

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('get_post', post_id=post_id))


@app.route('/new', methods=['GET', 'POST'])
@login_required
def create_new():
    if request.method == 'GET':
        post = Post('', '', datetime.now(), True)
        return render_template('edit.html', post=post, config=Config,
                               post_url=url_for('create_new'))

    title = request.form['title']
    content = request.form['content']
    is_draft = not (not ('is_draft' in request.form and
                         request.form['is_draft']))
    post = Post(title, content, datetime.now(), is_draft)

    db.session.add(post)
    db.session.commit()
    return redirect(url_for('get_post', post_id=post.id))


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":

    print('__revision__: {}'.format(__revision__))
    print('Site name: {}'.format(Config.SITENAME))
    print('Site url: {}'.format(Config.SITEURL))
    print('Port: {}'.format(Config.PORT))
    print('Debug: {}'.format(Config.DEBUG))
    if Config.DEBUG:
        print('DB URI: {}'.format(Config.DB_URI))
        print('Secret Key: {}'.format(Config.SECRET_KEY))

    if args.create_db:
        print('Setting up the database')
        db.create_all()
        exit(0)

    if args.hash_password is not None:
        print(bcrypt.generate_password_hash(args.hash_password))
        exit(0)

    app.run(debug=Config.DEBUG, port=Config.PORT, use_reloader=Config.DEBUG)
