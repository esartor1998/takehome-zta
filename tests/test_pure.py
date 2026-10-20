"""Tests for the parts of the engine that are plain code, so they run in under
a second with no model, no database and no network. Anything that needs a model
is measured by `founder bench` and `founder ablate` instead"""
import unittest
from datetime import datetime

from founder import followups, stale
from founder.identity import parse_addresses
from founder.normalize import html_to_text, split_quote


class Addresses(unittest.TestCase):
    def test_unquoted_last_first_is_one_address(self):
        got = parse_addresses('ADES, Caroline <caroline@blueharbor.example>')
        self.assertEqual(got, [('ADES, Caroline', 'caroline@blueharbor.example')])

    def test_list_with_names_and_bare_addresses(self):
        got = parse_addresses('A B <a@x.example>, c@y.example')
        self.assertEqual([e for _, e in got], ['a@x.example', 'c@y.example'])


class Quotes(unittest.TestCase):
    def test_inline_replies_are_kept(self):
        body = ('\nOn Fri, Mar 13, 2026 at 3:00 PM Alex <a@x> wrote:\n> Section 2: churn 3%\n'
                'cut this slide\n> Section 3: asks\nadd the cohort chart')
        own, quoted, kind = split_quote(body)
        self.assertIn('cut this slide', own)
        self.assertIn('add the cohort chart', own)
        self.assertNotIn('Section 2', own)

    def test_headerless_quote_keeps_the_answer(self):
        own, _, _ = split_quote('> are you free?\nyes, thursday works')
        self.assertEqual(own, 'yes, thursday works')

    def test_gmail_wrapped_header(self):
        body, quoted, kind = split_quote('Thanks.\n\nOn Thu, Mar 5, 2026 at 5:00 PM\nJordan <j@x> wrote:\n> hi')
        self.assertEqual((body, kind), ('Thanks.', 'reply'))
        self.assertTrue(quoted.startswith('On Thu'))

    def test_forward_marker(self):
        _, _, kind = split_quote('FYI\n\n---------- Forwarded message ---------\nFrom: x')
        self.assertEqual(kind, 'forward')

    def test_plain_text_is_untouched(self):
        self.assertEqual(split_quote('no quote here')[1:], ('', ''))

    def test_html_becomes_text(self):
        self.assertEqual(html_to_text('<p>Hello</p><p>a &amp; b</p>'), 'Hello\na & b')


class Deadlines(unittest.TestCase):
    friday = datetime(2026, 3, 13)      # a Friday

    def test_weekday_resolves_forward(self):
        self.assertEqual(followups.parse_due('by Monday', self.friday), '2026-03-16')

    def test_same_weekday_means_today(self):
        self.assertEqual(followups.parse_due('by Friday', self.friday), '2026-03-13')

    def test_explicit_date_and_relative_words(self):
        self.assertEqual(followups.parse_due('before Mar 20', self.friday), '2026-03-20')
        self.assertEqual(followups.parse_due('tomorrow', self.friday), '2026-03-14')
        self.assertEqual(followups.parse_due('early next week', self.friday), '2026-03-16')

    def test_informal_forms(self):
        self.assertEqual(followups.parse_due('send tmrw', self.friday), '2026-03-14')
        self.assertEqual(followups.parse_due('by 3/18', self.friday), '2026-03-18')
        self.assertEqual(followups.parse_due('need yes/no by thurs', self.friday), '2026-03-19')
        self.assertEqual(followups.parse_due('by the 20th', self.friday), '2026-03-20')
        self.assertEqual(followups.parse_due('eow is fine', self.friday), '2026-03-13')

    def test_month_is_not_monday(self):
        self.assertEqual(followups.parse_due('later this month', self.friday), '')

    def test_no_deadline(self):
        self.assertEqual(followups.parse_due('whenever you can', self.friday), '')


class Staleness(unittest.TestCase):
    def test_new_date_the_record_lacks_disagrees(self):
        self.assertTrue(stale.disagrees('Freeze Mar 10. Ship Mar 20.', 'ship Mar 22, not Mar 20'))

    def test_same_values_agree(self):
        self.assertFalse(stale.disagrees('$59 new, $49 existing', 'new customers pay $59, existing stay at $49'))

    def test_iso_and_prose_dates_compare_equal(self):
        self.assertEqual(stale.concrete_values('close 2026-03-31'), stale.concrete_values('close Mar 31'))

    def test_status_change_without_numbers(self):
        self.assertTrue(stale.disagrees('Offer approved. Status: offer out.', 'Taylor accepted another offer'))

    def test_deal_terms_are_values(self):
        self.assertEqual(stale.concrete_values('2yr 15% fine'), {'15%', '2 year'})
        self.assertTrue(stale.disagrees('Term: 1 year. Discount: 10%.', 'initech renewal is 2 yr at 15% now', 'Initech renewal terms', '#general'))

    def test_slash_dates_compare_to_prose_dates(self):
        self.assertEqual(stale.concrete_values('by 3/18'), stale.concrete_values('by Mar 18'))

    def test_issue_ids_are_not_values(self):
        self.assertEqual(stale.concrete_values('see ACME-431 and PR #218'), set())


if __name__ == '__main__':
    unittest.main()
