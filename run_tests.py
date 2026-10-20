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


class TokenizeTest(unittest.TestCase):
    def test_splits_on_non_word_characters(self):
        # when
        result = stuart.tokenize('one, two.three  four')

        # then
        self.assertEqual(['one', 'two', 'three', 'four'], result)

    def test_lower_cases_words(self):
        # when
        result = stuart.tokenize('One TWO tHrEe')

        # then
        self.assertEqual(['one', 'two', 'three'], result)

    def test_keeps_digits(self):
        # when
        result = stuart.tokenize('page 42 of x3')

        # then
        self.assertEqual(['page', '42', 'of', 'x3'], result)

    def test_empty_values(self):
        # expect
        self.assertEqual([], stuart.tokenize(''))
        self.assertEqual([], stuart.tokenize(None))
        self.assertEqual([], stuart.tokenize('  ,. '))


class WordVariantsTest(unittest.TestCase):
    def test_word_is_always_a_variant_of_itself(self):
        # expect
        self.assertIn('page', stuart.word_variants('page'))

    def test_plural_shares_a_variant_with_singular(self):
        # expect
        self.assertTrue(
            stuart.word_variants('pages') & stuart.word_variants('page'))

    def test_y_plural_shares_a_variant_with_singular(self):
        # expect
        self.assertTrue(
            stuart.word_variants('stories') & stuart.word_variants('story'))

    def test_verb_endings_share_a_variant(self):
        # expect
        self.assertTrue(
            stuart.word_variants('searching') & stuart.word_variants('search'))
        self.assertTrue(
            stuart.word_variants('searched') &
            stuart.word_variants('searches'))
        self.assertTrue(
            stuart.word_variants('writing') & stuart.word_variants('write'))

    def test_unrelated_words_share_no_variant(self):
        # expect
        self.assertFalse(
            stuart.word_variants('pages') & stuart.word_variants('tags'))

    def test_short_stems_are_not_generated(self):
        # when a word would stem to fewer than three characters
        result = stuart.word_variants('ads')

        # then only the word itself is a variant of it
        self.assertEqual({'ads'}, result)


class ScoreTermInWordsTest(unittest.TestCase):
    def test_exact_match_scores_highest(self):
        # when
        result = stuart.score_term_in_words('alpha', ['beta', 'alpha'])

        # then
        self.assertEqual(1.0, result)

    def test_no_words_scores_zero(self):
        # expect
        self.assertEqual(0.0, stuart.score_term_in_words('alpha', []))

    def test_unrelated_words_score_zero(self):
        # expect
        self.assertEqual(
            0.0, stuart.score_term_in_words('alpha', ['something', 'else']))

    def test_different_inflection_scores_below_exact_match(self):
        # when
        result = stuart.score_term_in_words('searching', ['searches'])

        # then
        self.assertEqual(stuart.SEARCH_STEM_SCORE, result)

    def test_prefix_scores_below_a_shared_stem(self):
        # when
        result = stuart.score_term_in_words('mark', ['markdown'])

        # then
        self.assertEqual(stuart.SEARCH_PREFIX_SCORE, result)

    def test_misspelling_scores_something(self):
        # when a term is misspelled
        result = stuart.score_term_in_words('kitchin', ['kitchen'])

        # then it still matches, but below an exact match
        self.assertGreater(result, 0.0)
        self.assertLess(result, 1.0)

    def test_best_of_several_words_is_used(self):
        # when one word matches exactly and another only loosely
        result = stuart.score_term_in_words('kitchen', ['kitchin', 'kitchen'])

        # then the better match decides the score
        self.assertEqual(1.0, result)

    def test_short_terms_are_not_treated_as_prefixes(self):
        # when a term is shorter than three characters
        result = stuart.score_term_in_words('ab', ['abcdefg'])

        # then it does not match as a prefix of a much longer word
        self.assertEqual(0.0, result)


class ParseSynonymsTest(unittest.TestCase):
    def test_empty_values(self):
        # expect
        self.assertEqual({}, stuart.parse_synonyms(''))
        self.assertEqual({}, stuart.parse_synonyms(None))

    def test_single_group(self):
        # when
        result = stuart.parse_synonyms('cat, feline')

        # then each word maps to the others in its group
        self.assertEqual({'cat': {'feline'}, 'feline': {'cat'}}, result)

    def test_several_groups(self):
        # when
        result = stuart.parse_synonyms('cat, feline; dog, canine, hound')

        # then
        self.assertEqual({'cat'}, result['feline'])
        self.assertEqual({'canine', 'hound'}, result['dog'])

    def test_groups_separated_by_newlines(self):
        # when
        result = stuart.parse_synonyms('cat, feline\ndog, canine')

        # then the groups are kept apart
        self.assertEqual({'feline'}, result['cat'])
        self.assertEqual({'canine'}, result['dog'])


class SearchTest(unittest.TestCase):
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

    def add_page(self, title, content='content', is_private=False, notes=None,
                 tags=()):
        page = stuart.Page(title, content, datetime(2017, 1, 1), is_private,
                           notes)
        for name in tags:
            page.tags.append(stuart.Tag(name))
        app.db.session.add(page)
        app.db.session.commit()
        return page

    def search(self, search_terms, include_private=False):
        results = stuart.Page.search(search_terms,
                                     include_private=include_private)
        return [page for page, _ in results]

    def test_empty_query_finds_nothing(self):
        # given
        self.add_page('title')

        # expect
        self.assertEqual([], stuart.Page.search(''))
        self.assertEqual([], stuart.Page.search('   '))

    def test_matches_on_title(self):
        # given
        page = self.add_page('Lemon Cake', 'nothing relevant here')
        self.add_page('Something Else', 'nor here')

        # when
        results = self.search('lemon')

        # then
        self.assertEqual([page], results)

    def test_matches_on_content(self):
        # given
        page = self.add_page('Some Title', 'a recipe for lemon cake')
        self.add_page('Another Title', 'nothing relevant here')

        # when
        results = self.search('lemon')

        # then
        self.assertEqual([page], results)

    def test_matches_on_notes(self):
        # given
        page = self.add_page('Some Title', 'content',
                             notes='remember the lemons')
        self.add_page('Another Title', 'content')

        # when
        results = self.search('lemon')

        # then
        self.assertEqual([page], results)

    def test_matches_on_tags(self):
        # given
        page = self.add_page('Some Title', 'content', tags=['lemon'])
        self.add_page('Another Title', 'content')

        # when
        results = self.search('lemon')

        # then
        self.assertEqual([page], results)

    def test_matches_a_misspelled_term(self):
        # given
        page = self.add_page('Lemon Cake')

        # when the query is misspelled
        results = self.search('lemmon')

        # then the page is still found
        self.assertEqual([page], results)

    def test_matches_a_different_inflection(self):
        # given
        page = self.add_page('Baking Cakes')

        # when
        results = self.search('bake cake')

        # then
        self.assertEqual([page], results)

    def test_matches_a_prefix(self):
        # given
        page = self.add_page('Markdown Syntax')

        # when
        results = self.search('markd')

        # then
        self.assertEqual([page], results)

    def test_title_match_outranks_content_match(self):
        # given a page with the term in its content
        content_match = self.add_page('Unrelated', 'all about lemons')
        # and a page with the term in its title
        title_match = self.add_page('Lemons', 'unrelated content')

        # when
        results = self.search('lemons')

        # then the title match comes first
        self.assertEqual([title_match, content_match], results)

    def test_matching_more_terms_outranks_matching_fewer(self):
        # given a page matching one term
        one = self.add_page('Lemon', 'unrelated content')
        # and a page matching both
        both = self.add_page('Lemon Cake', 'unrelated content')

        # when
        results = self.search('lemon cake')

        # then the page matching both terms comes first
        self.assertEqual([both, one], results)

    def test_equal_scores_are_ordered_by_title(self):
        # given two pages that match equally well
        beta = self.add_page('Beta Lemon')
        alpha = self.add_page('Alpha Lemon')

        # when
        results = self.search('lemon')

        # then they are ordered by title
        self.assertEqual([alpha, beta], results)

    def test_private_pages_are_excluded_by_default(self):
        # given
        public = self.add_page('Public Lemons')
        self.add_page('Private Lemons', is_private=True)

        # when
        results = self.search('lemons')

        # then
        self.assertEqual([public], results)

    def test_private_pages_are_included_when_asked_for(self):
        # given
        self.add_page('Public Lemons')
        self.add_page('Private Lemons', is_private=True)

        # when
        results = self.search('lemons', include_private=True)

        # then
        self.assertEqual(2, len(results))

    def test_no_matches(self):
        # given
        self.add_page('Lemon Cake')

        # when
        results = self.search('bicycle')

        # then
        self.assertEqual([], results)

    def test_synonyms_are_matched_when_the_site_defines_them(self):
        # given a page that uses one word
        page = self.add_page('Feline Behavior')

        # precondition: a search for an unrelated synonym finds nothing
        self.assertEqual([], self.search('cat'))

        # when the site declares the two words equivalent
        app.db.session.add(stuart.Option('search_synonyms', 'cat, feline'))
        app.db.session.commit()

        # then the page is found by either word
        self.assertEqual([page], self.search('cat'))

    def test_synonym_match_scores_below_a_direct_match(self):
        # given
        app.db.session.add(stuart.Option('search_synonyms', 'cat, feline'))
        direct = self.add_page('Cat')
        synonym = self.add_page('Feline')
        app.db.session.commit()

        # when
        results = self.search('cat')

        # then the page that uses the term itself comes first
        self.assertEqual([direct, synonym], results)


class SearchRouteTest(unittest.TestCase):
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

    def test_search_finds_a_matching_page(self):
        # given
        page = stuart.Page('Lemon Cake', 'a recipe', datetime(2017, 1, 1))
        app.db.session.add(page)
        app.db.session.commit()

        # when
        resp = self.cl.get('/search?q=lemon')

        # then
        self.assertEqual(200, resp.status_code)
        self.assertIn('Lemon Cake', resp.get_data(as_text=True))

    def test_search_without_terms_prompts_for_them(self):
        # when
        resp = self.cl.get('/search')

        # then
        self.assertEqual(200, resp.status_code)
        self.assertIn('Enter something to search for',
                      resp.get_data(as_text=True))

    def test_search_without_matches_says_so(self):
        # given
        page = stuart.Page('Lemon Cake', 'a recipe', datetime(2017, 1, 1))
        app.db.session.add(page)
        app.db.session.commit()

        # when
        resp = self.cl.get('/search?q=bicycle')

        # then
        self.assertEqual(200, resp.status_code)
        self.assertIn('No pages found', resp.get_data(as_text=True))

    def test_search_hides_private_pages_from_anonymous_users(self):
        # given
        page = stuart.Page('Lemon Cake', 'a recipe', datetime(2017, 1, 1),
                           is_private=True)
        app.db.session.add(page)
        app.db.session.commit()

        # when an anonymous user searches
        resp = self.cl.get('/search?q=lemon')

        # then the private page is not among the results
        self.assertEqual(200, resp.status_code)
        self.assertIn('No pages found', resp.get_data(as_text=True))

    def test_search_results_are_paginated(self):
        # given more pages than fit on one page of results
        for i in range(3):
            app.db.session.add(stuart.Page('Lemon {}'.format(i), 'a recipe',
                                           datetime(2017, 1, 1)))
        app.db.session.commit()

        # when the second page of results is requested
        resp = self.cl.get('/search?q=lemon&per_page=2&page=2')

        # then it holds the leftover result, and the pagination links keep
        # the search terms
        self.assertEqual(200, resp.status_code)
        text = resp.get_data(as_text=True)
        self.assertIn('Lemon 2', text)
        self.assertNotIn('Lemon 0', text)
        self.assertIn('q=lemon', text)

    def test_search_box_is_in_the_navbar(self):
        # when any page is requested
        resp = self.cl.get('/all-pages')

        # then it has a search box
        self.assertEqual(200, resp.status_code)
        self.assertIn('name="q"', resp.get_data(as_text=True))


class PaginateItemsTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.testing = True

    def paginate(self, items, query_string=''):
        with app.test_request_context('/search?' + query_string):
            return stuart.paginate_items(items)

    def test_first_page_by_default(self):
        # when
        pager = self.paginate(list(range(5)))

        # then
        self.assertEqual(1, pager.page)
        self.assertEqual([0, 1, 2, 3, 4], pager.items)
        self.assertEqual(5, pager.total)

    def test_requested_page_and_size(self):
        # when
        pager = self.paginate(list(range(5)), 'page=2&per_page=2')

        # then
        self.assertEqual([2, 3], pager.items)
        self.assertEqual(3, pager.pages)
        self.assertTrue(pager.has_prev)
        self.assertTrue(pager.has_next)

    def test_invalid_values_fall_back_to_defaults(self):
        # when
        pager = self.paginate(list(range(5)), 'page=0&per_page=0')

        # then
        self.assertEqual(1, pager.page)
        self.assertEqual(20, pager.per_page)
        self.assertEqual([0, 1, 2, 3, 4], pager.items)

    def test_page_past_the_end_is_empty(self):
        # when
        pager = self.paginate(list(range(5)), 'page=9&per_page=2')

        # then
        self.assertEqual([], pager.items)


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
        stuart.cmd_create_db()

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
