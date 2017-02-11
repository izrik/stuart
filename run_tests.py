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
        self.cl = app.test_client()
        app.testing = True
        with app.app_context():
            app.db.create_all()

    def tearDown(self):
        app.db.session.rollback()

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

    def test_init_set_summary_from_content(self):
        # when a Post is created
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # then the post's summary is set from the content
        self.assertEqual('content', post.summary)

    def test_init_set_summary_from_content_truncated(self):
        # when a Post is created from content with length == 100
        content = '12345678901234567890123456789012345678901234567890' \
                  '12345678901234567890123456789012345678901234567890'  # 100
        post = blogware.Post('title', content, datetime(2017, 1, 1))

        # then the post's summary is set from the content without modification
        self.assertEqual(content, post.summary)

        # when a Post is created from content with length > 100
        content2 = '12345678901234567890123456789012345678901234567890' \
                   '123456789012345678901234567890123456789012345678901'  # 101
        expected = '12345678901234567890123456789012345678901234567890' \
                   '12345678901234567890123456789012345678901234567890...'
        post = blogware.Post('title', content2, datetime(2017, 1, 1))

        # then the post's summary is set from the truncated content
        self.assertEqual(expected, post.summary)

    def test_init_set_last_updated_date(self):
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # then the post's summary is set from the content without modification
        self.assertEqual(datetime(2017, 1, 1), post.last_updated_date)

    def test_summarize_consecutive_spaces_are_condensed(self):
        # when
        result = blogware.Post.summarize('one  two')

        # then
        self.assertEqual('one two', result)

    def test_summarize_html_tags_are_removed(self):
        # when
        result = blogware.Post.summarize('<a href="/">Home</a>')

        # then
        self.assertEqual('Home', result)

    def test_summarize_punctuation_has_added_space(self):
        # when
        result = blogware.Post.summarize('one,two.three?four!five')

        # then
        self.assertEqual('one, two. three? four! five', result)

    def test_summarize_wordish_chars_are_kept(self):
        # when
        result = blogware.Post.summarize('Something,.?!')

        # then
        self.assertEqual('Something, . ? ! ', result)

    def test_summarize_non_wordish_chars_are_removed(self):
        # when
        result = blogware.Post.summarize(
            'Something :@#$%^&*()[]-_=+[]{}\\|;:\'"/<>')

        # then
        self.assertEqual('Something ', result)

    def test_summarize_long_values_are_truncated(self):
        # when a string has length == 100
        content = '12345678901234567890123456789012345678901234567890' \
                  '12345678901234567890123456789012345678901234567890'  # 100
        result = blogware.Post.summarize(content)

        # then the summarized value is the same
        self.assertEqual(content, result)

        # when a string has length > 100
        content2 = '12345678901234567890123456789012345678901234567890' \
                   '123456789012345678901234567890123456789012345678901'  # 101
        expected2 = '12345678901234567890123456789012345678901234567890' \
                    '12345678901234567890123456789012345678901234567890...'
        result2 = blogware.Post.summarize(content2)

        # then the summarized value is truncated
        self.assertEqual(expected2, result2)

    def test_summary_is_set_when_content_is_set(self):
        # given
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # when
        post.content = 'content2'

        # then
        self.assertEqual('content2', post.summary)

    def test_content_is_not_None(self):
        # given
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))

        # when
        post.content = None

        # then
        self.assertEqual('', post.content)
        self.assertEqual('', post.summary)

    def test_get_by_slug(self):
        # given
        post1 = blogware.Post('title1', 'content1', datetime(2017, 1, 1))
        post2 = blogware.Post('title2', 'content2', datetime(2017, 1, 1))
        post3 = blogware.Post('title3', 'content3', datetime(2017, 1, 1))
        app.db.session.add(post1)
        app.db.session.add(post2)
        app.db.session.add(post3)

        # when
        result = blogware.Post.get_by_slug('title2')

        # then
        self.assertIs(post2, result)

    def test_get_by_slug_missing(self):
        # given
        post1 = blogware.Post('title1', 'content1', datetime(2017, 1, 1))
        post2 = blogware.Post('title2', 'content2', datetime(2017, 1, 1))
        post3 = blogware.Post('title3', 'content3', datetime(2017, 1, 1))
        app.db.session.add(post1)
        app.db.session.add(post2)
        app.db.session.add(post3)

        # when
        result = blogware.Post.get_by_slug('title4')

        # then
        self.assertIsNone(result)

    def test_get_unique_slug(self):
        # when
        slug = blogware.Post.get_unique_slug('title')

        # then
        self.assertEqual('title', slug)

    def test_get_unique_slug_not_unique(self):
        # given a post that already exists
        post = blogware.Post('title', 'content', datetime(2017, 1, 1))
        app.db.session.add(post)

        # when we try to get a slug with the same value
        slug = blogware.Post.get_unique_slug('title')

        # then it increments a counter and returns the slightly different value
        self.assertEqual('title-1', slug)


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
