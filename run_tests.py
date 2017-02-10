#!/usr/bin/env python

import unittest
import argparse
import logging
from datetime import datetime

import blogware
from blogware import app


class PostTest(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['TESTING'] = True
        app.db.create_all()
        self.cl = app.test_client()
        app.testing = True

    def test_init(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # then the title is the same as what was passed to the constructor
        self.assertEqual('title', post.title)

        # then the content is the same as what was passed to the constructor
        self.assertEqual('content', post.content)

        # then the date is the same as what was passed to the constructor
        self.assertEqual(datetime(2017, 1, 1), post.date)

    def test_init_optional_arg_is_draft(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # then optional argument "is_draft" have its default value of False
        self.assertFalse(post.is_draft)

    def test_init_set_is_draft(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1), True)

        # then the is_draft field is the same as what was passed to the
        # constructor
        self.assertTrue(post.is_draft)

    def test_init_set_is_draft_named(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1),
                             is_draft=True)

        # then the is_draft field is the same as what was passed to the
        # constructor
        self.assertTrue(post.is_draft)

    def test_init_optional_arg_notes(self):

        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # then optional argument "notes" have its default value of None
        self.assertIsNone(post.notes)

    def test_init_set_notes(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1), False,
                             'notes')

        # then the is_draft field is the same as what was passed to the
        # constructor
        self.assertEqual('notes', post.notes)

    def test_init_set_notes_named(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1), False,
                             notes='notes')

        # then the is_draft field is the same as what was passed to the
        # constructor
        self.assertEqual('notes', post.notes)

    def test_init_set_slug_from_simple_title(self):
        # when a Post with a simple title is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # then the post's slug is set
        self.assertEqual('title', post.slug)

    def test_init_set_slug_from_title_with_spaces(self):
        # when a Post with a simple title is created
        post = blogware.Post('title  one', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with consecutive spaces replaced by a
        # single hyphen
        self.assertEqual('title-one', post.slug)

    def test_init_set_slug_from_title_with_leading_spaces(self):
        # when a Post with a simple title is created
        post = blogware.Post(' title', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with leading spaces removed
        self.assertEqual('title', post.slug)

    def test_init_set_slug_from_title_with_trailing_spaces(self):
        # when a Post with a simple title is created
        post = blogware.Post('title ', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with trailing spaces removed
        self.assertEqual('title', post.slug)

    def test_init_set_slug_from_title_with_non_word_characters(self):
        # when a Post with a simple title is created
        post = blogware.Post('title ! $,()', 'content', datetime(2017, 1, 1))

        # then the post's slug is set, with non-word chars removed
        self.assertEqual('title', post.slug)

    def test_init_set_slug_from_title_with_upper_case(self):
        # when a Post with a simple title is created
        post = blogware.Post('TITLEtitletItLe', 'content',
                             datetime(2017, 1, 1))

        # then the post's slug is set
        self.assertEqual('titletitletitle', post.slug)


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
