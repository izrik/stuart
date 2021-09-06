#!/usr/bin/env python3

import argparse
from datetime import datetime
import logging
import unittest

from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import NotFound

import stuart
from stuart import app


class PageTest(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.cl = app.test_client()
        app.testing = True
        with app.app_context():
            app.db.create_all()

    def tearDown(self):
        app.db.session.rollback()

    def test_init(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # then the title is the same as what was passed to the constructor
        self.assertEqual('title', page.title)

        # then the content is the same as what was passed to the constructor
        self.assertEqual('content', page.content)

        # then the date is the same as what was passed to the constructor
        self.assertEqual(datetime(2017, 1, 1), page.date)

    def test_init_optional_arg_is_private(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # then optional argument "is_private" have its default value of False
        self.assertFalse(page.is_private)

    def test_init_set_is_private(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1), True)

        # then the is_private field is the same as what was passed to the
        # constructor
        self.assertTrue(page.is_private)

    def test_init_set_is_private_named(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1),
                           is_private=True)

        # then the is_private field is the same as what was passed to the
        # constructor
        self.assertTrue(page.is_private)

    def test_init_optional_arg_notes(self):

        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # then optional argument "notes" have its default value of None
        self.assertIsNone(page.notes)

    def test_init_set_notes(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1), False,
                           'notes')

        # then the is_private field is the same as what was passed to the
        # constructor
        self.assertEqual('notes', page.notes)

    def test_init_set_notes_named(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1), False,
                           notes='notes')

        # then the is_private field is the same as what was passed to the
        # constructor
        self.assertEqual('notes', page.notes)

    def test_init_set_slug_from_simple_title(self):
        # when a Page with a simple title is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # then the page's slug is set
        self.assertEqual('title', page.slug)

    def test_init_set_slug_from_title_with_spaces(self):
        # when a Page with a simple title is created
        page = stuart.Page('title  one', 'content', datetime(2017, 1, 1))

        # then the page's slug is set, with consecutive spaces replaced by a
        # single hyphen
        self.assertEqual('title-one', page.slug)

    def test_init_set_slug_from_title_with_leading_spaces(self):
        # when a Page with a simple title is created
        page = stuart.Page(' title', 'content', datetime(2017, 1, 1))

        # then the page's slug is set, with leading spaces removed
        self.assertEqual('title', page.slug)

    def test_init_set_slug_from_title_with_trailing_spaces(self):
        # when a Page with a simple title is created
        page = stuart.Page('title ', 'content', datetime(2017, 1, 1))

        # then the page's slug is set, with trailing spaces removed
        self.assertEqual('title', page.slug)

    def test_init_set_slug_from_title_with_non_word_characters(self):
        # when a Page with a simple title is created
        page = stuart.Page('title ! $,()', 'content', datetime(2017, 1, 1))

        # then the page's slug is set, with non-word chars removed
        self.assertEqual('title', page.slug)

    def test_init_set_slug_from_title_with_upper_case(self):
        # when a Page with a simple title is created
        page = stuart.Page('TITLEtitletItLe', 'content',
                           datetime(2017, 1, 1))

        # then the page's slug is set
        self.assertEqual('titletitletitle', page.slug)

    def test_init_set_summary_from_content(self):
        # when a Page is created
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # then the page's summary is set from the content
        self.assertEqual('content', page.summary)

    def test_init_set_summary_from_content_truncated(self):
        # when a Page is created from content with length == 100
        content = '12345678901234567890123456789012345678901234567890' \
                  '12345678901234567890123456789012345678901234567890'  # 100
        page = stuart.Page('title', content, datetime(2017, 1, 1))

        # then the page's summary is set from the content without modification
        self.assertEqual(content, page.summary)

        # when a Page is created from content with length > 100
        content2 = '12345678901234567890123456789012345678901234567890' \
                   '123456789012345678901234567890123456789012345678901'  # 101
        expected = '12345678901234567890123456789012345678901234567890' \
                   '12345678901234567890123456789012345678901234567890...'
        page = stuart.Page('title', content2, datetime(2017, 1, 1))

        # then the page's summary is set from the truncated content
        self.assertEqual(expected, page.summary)

    def test_init_set_last_updated_date(self):
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # then the page's summary is set from the content without modification
        self.assertEqual(datetime(2017, 1, 1), page.last_updated_date)

    def test_summarize_consecutive_spaces_are_condensed(self):
        # when
        result = stuart.Page.summarize('one  two')

        # then
        self.assertEqual('one two', result)

    def test_summarize_html_tags_are_removed(self):
        # when
        result = stuart.Page.summarize('<a href="/">Home</a>')

        # then
        self.assertEqual('Home', result)

    def test_summarize_punctuation_has_added_space(self):
        # when
        result = stuart.Page.summarize('one,two.three?four!five')

        # then
        self.assertEqual('one, two. three? four! five', result)

    def test_summarize_wordish_chars_are_kept(self):
        # when
        result = stuart.Page.summarize('Something,.?!')

        # then
        self.assertEqual('Something, . ? ! ', result)

    def test_summarize_non_wordish_chars_are_removed(self):
        # when
        result = stuart.Page.summarize(
            'Something :@#$%^&*()[]-_=+[]{}\\|;:\'"/<>')

        # then
        self.assertEqual('Something ', result)

    def test_summarize_long_values_are_truncated(self):
        # when a string has length == 100
        content = '12345678901234567890123456789012345678901234567890' \
                  '12345678901234567890123456789012345678901234567890'  # 100
        result = stuart.Page.summarize(content)

        # then the summarized value is the same
        self.assertEqual(content, result)

        # when a string has length > 100
        content2 = '12345678901234567890123456789012345678901234567890' \
                   '123456789012345678901234567890123456789012345678901'  # 101
        expected2 = '12345678901234567890123456789012345678901234567890' \
                    '12345678901234567890123456789012345678901234567890...'
        result2 = stuart.Page.summarize(content2)

        # then the summarized value is truncated
        self.assertEqual(expected2, result2)

    def test_summary_is_set_when_content_is_set(self):
        # given
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # when
        page.content = 'content2'

        # then
        self.assertEqual('content2', page.summary)

    def test_content_is_not_None(self):
        # given
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))

        # when
        page.content = None

        # then
        self.assertEqual('', page.content)
        self.assertEqual('', page.summary)

    def test_get_by_slug(self):
        # given
        page1 = stuart.Page('title1', 'content1', datetime(2017, 1, 1))
        page2 = stuart.Page('title2', 'content2', datetime(2017, 1, 1))
        page3 = stuart.Page('title3', 'content3', datetime(2017, 1, 1))
        app.db.session.add(page1)
        app.db.session.add(page2)
        app.db.session.add(page3)

        # when
        result = stuart.Page.get_by_slug('title2')

        # then
        self.assertIs(page2, result)

    def test_get_by_slug_missing(self):
        # given
        page1 = stuart.Page('title1', 'content1', datetime(2017, 1, 1))
        page2 = stuart.Page('title2', 'content2', datetime(2017, 1, 1))
        page3 = stuart.Page('title3', 'content3', datetime(2017, 1, 1))
        app.db.session.add(page1)
        app.db.session.add(page2)
        app.db.session.add(page3)

        # when
        result = stuart.Page.get_by_slug('title4')

        # then
        self.assertIsNone(result)

    def test_get_unique_slug(self):
        # when
        slug = stuart.Page.get_unique_slug('title')

        # then
        self.assertEqual('title', slug)

    def test_get_unique_slug_not_unique(self):
        # given a page that already exists
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))
        app.db.session.add(page)

        # when we try to get a slug with the same value
        slug = stuart.Page.get_unique_slug('title')

        # then it increments a counter and returns the slightly different value
        self.assertEqual('title-1', slug)


class CreateDbTest(unittest.TestCase):
    def test_create_db_command(self):
        # given an app with uninitialize database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.cl = app.test_client()
        app.testing = True

        # precondition: the database table have not been created yet
        self.assertRaises(OperationalError, stuart.Page.query.first)
        self.assertRaises(OperationalError, stuart.Tag.query.first)
        self.assertRaises(OperationalError, stuart.Option.query.first)

        # when the create_db function is called
        stuart.create_db()

        # then the database tables are created
        self.assertIsNone(stuart.Page.query.first())
        self.assertIsNone(stuart.Tag.query.first())
        self.assertIsNone(stuart.Option.query.first())


class HashPasswordTest(unittest.TestCase):
    def test_hash_password(self):
        # given
        unhashed_password = '12345'

        # when
        result = stuart.hash_password(unhashed_password)

        # then
        self.assertTrue(
            stuart.bcrypt.check_password_hash(result, unhashed_password))


class CliCommandsTest(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        self.cl = app.test_client()
        app.testing = True
        with app.app_context():
            app.db.create_all()

    def tearDown(self):
        app.db.session.rollback()
        app.db.drop_all()

    def test_reset_slug(self):
        # given a page with a non-standard slug is put into the db
        page = stuart.Page('title', 'content', datetime(2017, 1, 1))
        page.slug = 'slug12345'
        app.db.session.add(page)
        app.db.session.commit()

        # precondition: the page is in the db
        self.assertIsNotNone(page.id)
        page2 = stuart.Page.query.first()
        self.assertIsNotNone(page2.id)
        self.assertIs(page2, page)

        # precondition: the page's slug is different from the title
        self.assertNotEqual('title', page.slug)

        # when the reset_slug function is called
        stuart.reset_slug(page.id)

        # then the page's slug is changed to match the title (plus
        # counter, meh)
        self.assertEqual(page.title, page.slug)

    def test_reset_slug_missing(self):
        # precondition: no pages are in the db
        result = stuart.Page.query.first()
        self.assertIsNone(result)

        # when the function is called with the id of a nonexistent page,
        # then an exception is thrown
        self.assertRaises(NotFound, stuart.reset_slug, 1)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print-log', action='store_true',
                        help='Print the log.')
    args = parser.parse_args()

    if args.print_log:
        logging.basicConfig(level=logging.DEBUG,
                            format=('%(asctime)s %(levelname)s:%(name)s:'
                                    '%(funcName)s:'
                                    '%(filename)s(%(lineno)d):'
                                    '%(threadName)s(%(thread)d):%(message)s'))

    unittest.main(argv=[''])


if __name__ == '__main__':
    run()
