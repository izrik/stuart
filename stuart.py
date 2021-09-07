#!/usr/bin/env python3

# stuart - a python wiki system
# Copyright (C) 2016-2017 izrik
#
# This file is a part of stuart.
#
# Stuart is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Stuart is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with stuart.  If not, see <http://www.gnu.org/licenses/>.


import argparse
from datetime import datetime
from itertools import cycle
from os import environ
import random
import re

import dateutil.parser
from flask import flash
from flask import Flask
from flask import Markup
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_bcrypt import Bcrypt
from flask_login import AnonymousUserMixin
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import LoginManager
from flask_login import logout_user
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import gfm  # noqa: F401
import jinja2
import markdown
from slugify import slugify
from werkzeug.exceptions import BadRequest
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import ServiceUnavailable
from werkzeug.exceptions import Unauthorized
from werkzeug.serving import run_simple
from werkzeug.middleware.dispatcher import DispatcherMiddleware

__version__ = '0.4'
try:
    import git
    try:
        __revision__ = git.Repo('.').git.describe(tags=True, dirty=True,
                                                  always=True, abbrev=40)
    except git.InvalidGitRepositoryError:
        __revision__ = 'unknown'
except ImportError:
    __revision__ = 'unknown'


class Config(object):
    SECRET_KEY = environ.get('STUART_SECRET_KEY', 'secret')
    HOST = environ.get('STUART_HOST', '127.0.0.1')
    PORT = environ.get('STUART_PORT', 2512)
    DEBUG = environ.get('STUART_DEBUG', False)
    DB_URI = environ.get('STUART_DB_URI')
    DB_URI_FILE = environ.get('STUART_DB_URI_FILE')
    SITENAME = environ.get('STUART_SITENAME', 'Site Name')
    PATH_PREFIX = environ.get('STUART_PATH_PREFIX', '')
    CUSTOM_TEMPLATES = environ.get('STUART_CUSTOM_TEMPLATES', None)
    AUTHOR = environ.get('STUART_AUTHOR', 'The Author')
    LOCAL_RESOURCES = environ.get('STUART_LOCAL_RESOURCES', False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret-key', type=str,
                        default=Config.SECRET_KEY, help='')
    parser.add_argument('--host', type=str, default=Config.HOST,
                        help='The ip address to listen on. Set to 0.0.0.0 to '
                             'accept any incoming connections on any network '
                             'interface. Defaults to 127.0.0.1 for testing.')
    parser.add_argument('--port', type=int, default=Config.PORT,
                        help='')
    parser.add_argument('--debug', action='store_true', help='',
                        default=Config.DEBUG)
    parser.add_argument('--db-uri', type=str, action='store',
                        default=Config.DB_URI)
    parser.add_argument('--db-uri-file', type=str, action='store',
                        default=Config.DB_URI_FILE)
    parser.add_argument('--sitename', type=str,
                        default=Config.SITENAME, help='')
    parser.add_argument('--path-prefix', type=str,
                        default=Config.PATH_PREFIX, help='')
    parser.add_argument('--custom-templates', type=str,
                        default=Config.CUSTOM_TEMPLATES,
                        help="The path to a directory on the filesystem from "
                             "which to load template files. If none is "
                             "specified, the app's default internal template "
                             "location will be used.")
    parser.add_argument('--author', type=str, default=Config.AUTHOR,
                        help='The name of the author of the site. This name '
                             'will appear in the "Posted by" line on pages, '
                             'and in the copyright section in the footer.')
    parser.add_argument('--local-resources', action='store_true',
                        default=Config.LOCAL_RESOURCES,
                        help='Use local resources (CSS and JS served from the '
                             'app instead of from global URLs).')

    parser.add_argument('--create-secret-key', action='store_true')
    parser.add_argument('--create-db', action='store_true')
    parser.add_argument('--hash-password', action='store', metavar='PASSWORD')
    parser.add_argument('--reset-slug', action='store', metavar='PAGE_ID')
    parser.add_argument('--set-date', action='store', nargs=2,
                        metavar=('PAGE_ID', 'DATE'))
    parser.add_argument('--set-last-updated-date', action='store', nargs=2,
                        metavar=('PAGE_ID', 'DATE'))
    parser.add_argument('--reset-summary', action='store', metavar='PAGE_ID')
    parser.add_argument('--list-options', action='store', nargs='?',
                        metavar='SEARCH_TERM', const='')
    parser.add_argument('--set-option', action='store', nargs=2,
                        metavar=('NAME', 'VALUE'))
    parser.add_argument('--clear-option', action='store', metavar='NAME')

    args = parser.parse_args()

    if args.create_secret_key:
        digits = '0123456789abcdef'
        key = ''.join((random.choice(digits) for x in range(48)))
        print(key)
        exit(0)

    Config.SECRET_KEY = args.secret_key
    Config.HOST = args.host
    Config.PORT = args.port
    Config.DEBUG = args.debug
    Config.DB_URI = args.db_uri
    Config.DB_URI_FILE = args.db_uri_file
    Config.SITENAME = args.sitename
    Config.PATH_PREFIX = args.path_prefix
    Config.CUSTOM_TEMPLATES = args.custom_templates
    Config.AUTHOR = args.author
    Config.LOCAL_RESOURCES = args.local_resources


app = Flask(__name__)

if Config.CUSTOM_TEMPLATES:
    loader = jinja2.ChoiceLoader([
        jinja2.FileSystemLoader(Config.CUSTOM_TEMPLATES),
        app.jinja_loader])
    app.jinja_loader = loader

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config["SECRET_KEY"] = Config.SECRET_KEY  # for WTF-forms and login

db_uri = 'sqlite://'
if Config.DB_URI:
    db_uri = Config.DB_URI
elif Config.DB_URI_FILE:
    try:
        with open(Config.DB_URI_FILE) as f:
            db_uri = f.read().strip()
    except FileNotFoundError:
        raise ConfigError(
            f'Could not find uri file "{Config.DB_URI_FILE}".')
    except PermissionError:
        raise ConfigError(
            f'Permission error when opening uri file '
            f'"{Config.DB_URI_FILE}".')
    except Exception as e:
        raise ConfigError(
            f'Error opening uri file "{Config.DB_URI_FILE}": {e}')
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri

app.config['APPLICATION_ROOT'] = Config.PATH_PREFIX

# extensions
login_manager = LoginManager(app)
db = SQLAlchemy(app)
app.db = db
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


tags_table = db.Table(
    'tags_pages',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), index=True),
    db.Column('page_id', db.Integer, db.ForeignKey('page.id'), index=True))


class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(100), name='title')
    slug = db.Column(db.String(100), index=True, unique=True)
    _content = db.Column(db.Text, name='content')
    summary = db.Column(db.Text)
    notes = db.Column(db.Text)
    date = db.Column(db.DateTime)
    last_updated_date = db.Column(db.DateTime, nullable=False)
    is_private = db.Column(db.Boolean, nullable=False, default=False,
                           name='is_private')
    tags = db.relationship('Tag', secondary=tags_table,
                           backref=db.backref('pages', lazy='dynamic'))

    def __init__(self, title, content, date, is_private=False, notes=None):
        self.title = title
        self.content = content
        self.date = date
        self.last_updated_date = date
        self.is_private = is_private
        self.notes = notes

    @property
    def content(self):
        return self._content

    @staticmethod
    def summarize(value):
        stripped = re.sub(r'</?[^>]+/?>', '', value)
        cleaned = re.sub(r'[^a-zA-Z01-9,.?!]', ' ', stripped)
        normalized = re.sub(r'\s*([.,?!])\s*', r'\1 ', cleaned)
        condensed = re.sub(r'\s+', ' ', normalized)
        truncated = condensed
        if len(truncated) > 100:
            truncated = condensed[:100] + '...'
        return truncated

    @content.setter
    def content(self, value):
        if value is None:
            value = ''
        value = str(value)
        self._content = value
        self.summary = self.summarize(value)

    @classmethod
    def get_by_slug(cls, slug):
        return Page.query.filter_by(slug=slug).first()

    @classmethod
    def get_by_title(cls, title):
        return Page.query.filter(Page._title==title).first()

    @classmethod
    def get_unique_slug(cls, title):
        slug = slugify(title)
        if Page.query.filter_by(slug=slug).count() > 0:
            i = 1
            while Page.query.filter_by(slug=slug).count() > 0:
                slug = slugify('{} {}'.format(title, i))
                i += 1
        return slug

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        if not self.slug and self._title:
            self.slug = self.get_unique_slug(self._title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)

    def __init__(self, name):
        self.name = name


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
    def get_sitename():
        return Options.get('sitename', Config.SITENAME)

    @staticmethod
    def get_path_prefix():
        return Options.get('path_prefix', Config.PATH_PREFIX)

    @staticmethod
    def get_revision():
        return __revision__

    @staticmethod
    def get_version():
        return __version__

    @staticmethod
    def seq():
        i = 0
        while True:
            yield i
            i += 1

    cycle = cycle

    @staticmethod
    def get_author():
        return Options.get('author', Config.AUTHOR)

    @staticmethod
    def should_use_local_resources():
        return Config.LOCAL_RESOURCES

    @staticmethod
    def get_main_page():
        return Options.get('main_page')


@login_manager.user_loader
def load_user(user_id):
    return User(Options.get_author(), Options.get_author())


@app.context_processor
def setup_options():
    return {'Options': Options}


@app.template_filter(name='gfm')
def render_gfm(s):
    from mdx_gfm import GithubFlavoredMarkdownExtension
    output = markdown.markdown(
        s, extensions=[GithubFlavoredMarkdownExtension()])
    moutput = Markup(output)
    return moutput


@app.route("/")
def index():
    page_name = Options.get_main_page()
    page = Page.get_by_title(page_name)
    if not page:
        page = Page.get_by_slug(page_name)
    if page and page.is_private and not current_user.is_authenticated:
        page = None
    user = current_user
    return render_template('index.html', config=Config, page=page, user=user)


@app.route('/all-pages')
def all_pages():
    query = Page.query
    if not current_user.is_authenticated:
        query = query.filter_by(is_private=False)
    query = query.order_by(Page._title.asc())
    pager = query.paginate()
    pages = query
    return render_template("all_pages.html", pages=pages, pager=pager,
                           page_links_endpoint='all_pages')


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

    user = User(Options.get_author(), Options.get_author())
    login_user(user)
    flash('Logged in successfully')
    # return redirect(request.args.get('next_url') or url_for('index'))
    return redirect(url_for('index'))


@app.route('/page/<slug>', methods=['GET'])
def get_page(slug):

    page = Page.get_by_slug(slug)
    if not page:
        raise NotFound()
    if page.is_private and not current_user.is_authenticated:
        raise Unauthorized()
    user = current_user

    return render_template('page.html', config=Config, page=page, user=user)


@app.route('/edit/<slug>', methods=['GET', 'POST'])
@login_required
def edit_page(slug):
    page = Page.get_by_slug(slug)
    if not page:
        raise NotFound()
    if request.method == 'GET':
        return render_template(
            'edit.html', page=page, config=Config,
            form_action_url=url_for('edit_page', slug=page.slug))

    title = request.form['title'].strip()
    if not title or not slugify(title).strip():
        raise BadRequest("The page's title is invalid.")
    content = request.form['content']
    notes = request.form['notes']
    is_private = not (not ('is_private' in request.form and
                           request.form['is_private']))
    tags = request.form['tags']

    page.title = title
    page.content = content
    page.notes = notes
    page.is_private = is_private
    page.last_updated_date = datetime.now()

    current_tags = set(page.tags)
    next_tag_names = set(
        name for name in (
            name.strip() for name in tags.split(',') if name)
        if name)
    next_tags = set()
    for name in next_tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if tag is None:
            tag = Tag(name)
        next_tags.add(tag)
    tags_to_add = next_tags.difference(current_tags)
    tags_to_remove = current_tags.difference(next_tags)

    for ttr in tags_to_remove:
        page.tags.remove(ttr)
    page.tags.extend(tags_to_add)

    for tta in tags_to_add:
        db.session.add(tta)
    db.session.add(page)
    db.session.commit()
    return redirect(url_for('get_page', slug=page.slug))


@app.route('/new', methods=['GET', 'POST'])
@login_required
def create_new():
    if request.method == 'GET':
        page = Page('', '', datetime.now(), True)
        return render_template('edit.html', page=page, config=Config,
                               form_action_url=url_for('create_new'))

    title = request.form['title'].strip()
    if not title or not slugify(title).strip():
        raise BadRequest("The page's title is invalid.")
    content = request.form['content']
    notes = request.form['notes']
    is_private = not (not ('is_private' in request.form and
                           request.form['is_private']))
    tags = request.form['tags']

    page = Page(title, content, datetime.now(), is_private, notes)

    next_tag_names = set(
        name for name in (
            name.strip() for name in tags.split(',') if name)
        if name)
    next_tags = set()
    for name in next_tag_names:
        tag = Tag.query.filter_by(name=name).first()
        if tag is None:
            tag = Tag(name)
        next_tags.add(tag)
    tags_to_add = next_tags
    page.tags.extend(tags_to_add)

    db.session.add(page)
    db.session.commit()
    return redirect(url_for('get_page', slug=page.slug))


@app.route('/tags', methods=['GET'])
def list_tags():
    tags = Tag.query
    return render_template('list_tags.html', tags=tags)


@app.route('/tags/<tag_id>', methods=['GET'])
def get_tag(tag_id):
    tag = Tag.query.get(tag_id)
    query = tag.pages
    if not current_user.is_authenticated:
        query = query.filter_by(is_private=False)
    pages = query
    return render_template("tag.html", tag=tag, pages=pages)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


def create_db():
    db.create_all()


def hash_password(unhashed_password):
    return bcrypt.generate_password_hash(unhashed_password)


def reset_slug(page_id):
    page = Page.query.get(page_id)
    if not page:
        msg = 'No page found with id {}'.format(page_id)
        raise NotFound(msg)
    print('Resetting the slug for page {}'.format(page_id))
    print('Old slug is "{}"'.format(page.slug))
    page.slug = page.get_unique_slug(page.title)
    db.session.add(page)
    db.session.commit()
    print('New slug is "{}"'.format(page.slug))


if Config.PATH_PREFIX:
    gapp = DispatcherMiddleware(Flask('Dummy-app'), {
        Config.PATH_PREFIX: app
    })
else:
    gapp = app


def run():
    print('__revision__: {}'.format(__revision__))
    print('Site name: {}'.format(Config.SITENAME))
    print('Path prefix: {}'.format(Config.PATH_PREFIX))
    print('Host: {}'.format(Config.HOST))
    print('Port: {}'.format(Config.PORT))
    print('Debug: {}'.format(Config.DEBUG))
    if Config.CUSTOM_TEMPLATES:
        print('Custom template path: {}'.format(Config.CUSTOM_TEMPLATES))
    if Config.DEBUG:
        print('DB URI: {}'.format(Config.DB_URI))
        print('DB URI File: {}'.format(Config.DB_URI_FILE))
        print(f"Effective DB URI: {db_uri}")
        print('Secret Key: {}'.format(Config.SECRET_KEY))
    print('Local Resources: {}'.format(Config.LOCAL_RESOURCES))

    if args.create_db:
        print('Setting up the database')
        create_db()
    elif args.hash_password is not None:
        print(hash_password(args.hash_password))
    elif args.reset_slug is not None:
        try:
            reset_slug(args.reset_slug)
        except NotFound as e:
            print(e.description)
    elif args.set_date is not None:
        page_id, new_date = args.set_date
        page = Page.query.get(page_id)
        if not page:
            print('No page found with id {}'.format(page_id))
            exit(1)
        print('Setting the date for page {}'.format(page_id))
        print('Old date is "{}"'.format(page.date))
        page.date = dateutil.parser.parse(new_date)
        db.session.add(page)
        db.session.commit()
        print('New date is "{}"'.format(page.date))
    elif args.set_last_updated_date is not None:
        page_id, new_date = args.set_last_updated_date
        page = Page.query.get(page_id)
        if not page:
            print('No page found with id {}'.format(page_id))
            exit(1)
        print('Setting the last updated date for page {}'.format(page_id))
        print('Old date is "{}"'.format(page.last_updated_date))
        page.last_updated_date = dateutil.parser.parse(new_date)
        db.session.add(page)
        db.session.commit()
        print('New last updated date is "{}"'.format(page.last_updated_date))
    elif args.reset_summary is not None:
        page_id = args.reset_summary
        page = Page.query.get(page_id)
        if not page:
            print('No page found with id {}'.format(page_id))
            exit(1)
        print('Resetting the summary for page {}'.format(page_id))
        print('Old summary is "{}"'.format(page.summary))
        page.content = page.content
        db.session.add(page)
        db.session.commit()
        print('New summary is "{}"'.format(page.summary))
    elif args.list_options is not None:
        search_term = '%{}%'.format(args.list_options)
        query = Option.query.order_by(Option.name.asc())
        if search_term:
            query = query.filter(Option.name.like(search_term))
        options = query.all()
        if options:
            maxlen = max(len(opt.name) for opt in options)
            print('Options')
            print('-------')
            for option in options:
                print('{:{maxlen}}   {}'.format(option.name, option.value,
                                                maxlen=maxlen))
        else:
            print('No options found')
    elif args.set_option is not None:
        name, value = args.set_option
        option = Option.query.get(name)
        if option:
            print('Setting the value for option {}'.format(name))
            print('Old value is "{}"'.format(option.value))
            option.value = value
        else:
            print('Creating option {}'.format(name))
            option = Option(name, value)
        db.session.add(option)
        db.session.commit()
        print('New value is "{}"'.format(option.value))
    elif args.clear_option is not None:
        name = args.clear_option
        option = Option.query.get(name)
        if not option:
            print('No option found with name {}'.format(name))
            exit(1)
        print('Clearing option {}'.format(name))
        print('Old value is "{}"'.format(option.value))
        db.session.delete(option)
        db.session.commit()
    else:
        run_simple(hostname=Config.HOST, port=Config.PORT,
                   application=gapp,
                   use_debugger=Config.DEBUG, use_reloader=Config.DEBUG,
                   passthrough_errors=True)


if __name__ == "__main__":
    run()
