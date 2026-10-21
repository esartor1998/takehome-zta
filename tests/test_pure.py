"""Tests for the parts of the engine that are plain code, so they run in under
a second with no model, no database and no network. Anything that needs a model
is measured by `founder bench` and `founder ablate` instead"""
import unittest
from datetime import datetime

import json
import tempfile
from pathlib import Path

import sqlite3

from founder import answer, dates, extract, followups, route, stale
from founder.identity import IdentityResolver, Person, parse_addresses
from founder.names import NameSense
from founder.normalize import calendar_items, html_to_text, issue_refs, split_quote


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


class RelativeChanges(unittest.TestCase):
    friday = datetime(2026, 3, 13)      # a Friday

    def test_relative_words_become_dates(self):
        self.assertEqual(stale.concrete_values('moved to next Friday', self.friday), {'mar 20'})
        self.assertEqual(stale.concrete_values('see you tomorrow', self.friday), {'mar 14'})
        self.assertEqual(stale.concrete_values('due end of month', self.friday), {'mar 31'})
        self.assertEqual(stale.concrete_values('in two weeks', self.friday), {'mar 27'})

    def test_without_a_base_they_are_not_values(self):
        self.assertEqual(stale.concrete_values('moved to next Friday'), set())

    def test_moved_to_next_friday_contradicts_a_date(self):
        record = 'Webinar: Thursday Mar 19.'
        self.assertTrue(stale.conflict_strength(record, 'moved the webinar to next Friday', 'Customer webinar',
                                                 record_base=datetime(2026, 3, 5), newer_base=self.friday) > 0)

    def test_same_date_by_another_name_agrees(self):
        record = 'Webinar: Friday Mar 20.'
        self.assertEqual(stale.conflict_strength(record, 'the webinar is next Friday', 'Customer webinar',
                                                  record_base=datetime(2026, 3, 5), newer_base=self.friday), 0)

    def test_month_and_quarter_changes(self):
        base = datetime(2026, 3, 13)
        self.assertTrue(stale.conflict_strength('Beta ships Mar 31.', 'beta slipped to April', 'Beta plan', record_base=base, newer_base=base) > 0)
        self.assertEqual(stale.conflict_strength('Beta ships Mar 31.', 'beta stays in March', 'Beta plan', record_base=base, newer_base=base), 0)
        self.assertTrue(stale.conflict_strength('Launch is Q1.', 'launch is now Q3', 'Launch plan', record_base=base, newer_base=base) > 0)

    def test_a_price_with_a_full_stop_is_the_same_price(self):
        self.assertEqual(stale.concrete_values('it costs $59.'), stale.concrete_values('$59/seat'))


class Names(unittest.TestCase):
    roster = ['daniel', 'rebecca', 'priya', 'marcus', 'sofia', 'hannah', 'michael']

    def test_truncations_need_no_model(self):
        sense = NameSense(self.roster)
        self.assertEqual(sense.resolve('dan'), {'daniel'})
        self.assertEqual(sense.resolve('pri'), {'priya'})
        self.assertEqual(sense.resolve('sof'), {'sofia'})

    def test_two_letters_and_unknown_words_resolve_to_nothing(self):
        sense = NameSense(self.roster)
        self.assertEqual(sense.resolve('da'), set())
        self.assertEqual(sense.resolve('table'), set())

    def test_embedding_needs_a_clear_winner(self):
        vectors = {'becky': [1, 0.1, 0], 'rebecca': [1, 0, 0], 'daniel': [0, 1, 0], 'priya': [0, 0, 1], 'marcus': [0, 0.3, 0.2],
                   'sofia': [0.1, 0.5, 0.5], 'hannah': [0.3, 0.3, 0.3], 'michael': [0, 0.3, 0.2], 'mark': [0, 0.3, 0.2]}
        sense = NameSense(self.roster, embed=lambda words, kind='query': [vectors[w] for w in words])
        self.assertEqual(sense.resolve('becky'), {'rebecca'})
        self.assertEqual(sense.resolve('mark'), set())       # as close to marcus as to michael: unsure

    def test_extending_a_name_is_a_different_name(self):
        vectors = {'daniella': [1, 0], 'daniel': [1, 0], 'priya': [0, 1], 'sammy': [1, 0], 'sam': [1, 0]}
        sense = NameSense(['daniel', 'priya'], embed=lambda words, kind='query': [vectors[w] for w in words])
        self.assertEqual(sense.resolve('daniella'), set())
        sense = NameSense(['sam', 'priya'], embed=lambda words, kind='query': [vectors[w] for w in words])
        self.assertEqual(sense.resolve('sammy'), {'sam'})


class Citations(unittest.TestCase):
    def blocks(self):
        return {1: '[1] email from Priya, Fri 2026-03-13 14:00 UTC, subject: ship date\n    The ship date is now Mar 22 for the roadmap.',
                2: '[2] email from Sofia, Fri 2026-03-13 15:00 UTC, subject: ship date\n    The ship date was Mar 20 for the roadmap.'}

    def test_a_wrong_date_does_not_keep_its_citation(self):
        text, _, _, issues = answer.ground_citations('The roadmap ship date is Mar 20 [1].', self.blocks(), [1, 2])
        self.assertIn('[2]', text)         # the block that says Mar 20 is added

    def test_a_value_no_block_has_is_flagged(self):
        _, _, _, issues = answer.ground_citations('The roadmap ship date is Mar 28 [1].', self.blocks(), [1, 2])
        self.assertEqual([i['kind'] for i in issues], ['value_mismatch'])

    def test_a_right_value_passes(self):
        _, _, _, issues = answer.ground_citations('The roadmap ship date is Mar 22 [1].', self.blocks(), [1, 2])
        self.assertEqual(issues, [])


class IssueRefs(unittest.TestCase):
    def test_any_team_key(self):
        self.assertEqual(issue_refs('fixes ENG-12 and ACME-7, see PR #3'), ['ENG-12', 'ACME-7'])


class Dates(unittest.TestCase):
    def tearDown(self):
        dates.set_slash_order('mdy')

    def test_year_is_the_one_nearest_the_message(self):
        self.assertEqual(followups.parse_due('by Jan 10', datetime(2025, 12, 20)), '2026-01-10')
        self.assertEqual(followups.parse_due('by Mar 1', datetime(2026, 3, 5)), '2026-03-01')

    def test_slash_order_comes_from_the_export(self):
        self.assertEqual(dates.detect_slash_order(['due 3/18', 'by 5/20']), 'mdy')
        self.assertEqual(dates.detect_slash_order(['due 18/3', 'by 20/5', 'see 25/12', 'ok 5/6']), 'dmy')
        self.assertEqual(dates.detect_slash_order(['support is 24/7', 'one 18/3 is not a locale']), 'mdy')

    def test_day_first_dates_read_day_first(self):
        dates.set_slash_order('dmy')
        self.assertEqual(followups.parse_due('by 18/3', datetime(2026, 3, 13)), '2026-03-18')
        self.assertEqual(stale.concrete_values('by 5/3'), {'mar 5'})


class Calendar(unittest.TestCase):
    class Ident:
        def from_email(self, email, automated=False):
            return ({'alex@x.example': 'P1', 'pat@x.example': 'P2'}.get(email), 'directory')

    def rows(self, rows):
        folder = Path(tempfile.mkdtemp())
        (folder / 'calendar_events.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
        return calendar_items(folder, self.Ident())

    def test_an_event_with_no_guests_belongs_to_its_organizer(self):
        item = self.rows([{'id': 'a', 'status': 'confirmed', 'summary': 'focus block', 'organizer': {'email': 'alex@x.example'},
                           'start': {'dateTime': '2026-03-16T09:00:00Z', 'timeZone': 'UTC'},
                           'end': {'dateTime': '2026-03-16T11:00:00Z', 'timeZone': 'UTC'}}])[0]
        self.assertEqual(item['people'], ['P1'])

    def test_unknown_guests_are_counted(self):
        item = self.rows([{'id': 'a', 'status': 'confirmed', 'summary': 'chat', 'organizer': {'email': 'alex@x.example'},
                           'attendees': [{'email': 'stranger@y.example', 'responseStatus': 'accepted'}],
                           'start': {'dateTime': '2026-03-16T09:00:00Z', 'timeZone': 'UTC'},
                           'end': {'dateTime': '2026-03-16T10:00:00Z', 'timeZone': 'UTC'}}])[0]
        self.assertEqual(item['meta']['unknown_attendees'], ['stranger@y.example'])

    def test_all_day_starts_at_local_midnight(self):
        rows = [{'id': 'a', 'status': 'confirmed', 'summary': 'offsite', 'organizer': {'email': 'alex@x.example'},
                 'start': {'dateTime': '2026-03-14T09:00:00-07:00', 'timeZone': 'America/Los_Angeles'},
                 'end': {'dateTime': '2026-03-14T10:00:00-07:00', 'timeZone': 'America/Los_Angeles'}},
                {'id': 'b', 'status': 'confirmed', 'summary': 'offsite', 'organizer': {'email': 'alex@x.example'},
                 'start': {'date': '2026-03-16'}, 'end': {'date': '2026-03-17'}}]
        allday = self.rows(rows)[1]
        self.assertEqual(allday['start'], '2026-03-16T07:00:00Z')
        self.assertEqual(allday['meta']['start_local'], '2026-03-16')


class MentionAndWeightTests(unittest.TestCase):
    def resolver(self):
        ident = IdentityResolver.__new__(IdentityResolver)
        ident.people = {'P1': Person('P1', 'Alex Chen'), 'P2': Person('P2', 'Jordan Pryce'),
                        'P3': Person('P3', 'Daniel Kim'), 'P4': Person('P4', 'Daniel Foster'),
                        'P5': Person('P5', 'Will Stone')}
        return ident

    def item(self, n, body, author='P1', people=(), thread=None):
        return {'id': n, 'title': '', 'body': body, 'author': author, 'people': list(people),
                'thread_key': thread or n, 'meta': {}}

    def test_a_unique_first_name_links(self):
        items = [self.item('a', 'Jordan says they cannot close before May 15.', author='P3')]
        self.resolver().link_mentions(items)
        self.assertEqual(items[0]['meta']['mentions'], ['P2'])

    def test_an_ambiguous_name_links_only_through_the_conversation(self):
        items = [self.item('a', 'Daniel is out until Monday.', thread='t'),
                 self.item('b', 'Daniel is out until Monday.', thread='u', people=['P4'])]
        self.resolver().link_mentions(items)
        self.assertNotIn('mentions', items[0]['meta'])
        self.assertEqual(items[1]['meta']['mentions'], ['P4'])

    def test_a_name_the_mail_also_uses_as_a_word_does_not_link(self):
        words = [self.item(f'w{i}', 'we will ship it') for i in range(3)]
        items = words + [self.item('a', 'Will we ship it?')]
        self.resolver().link_mentions(items)
        self.assertNotIn('mentions', items[-1]['meta'])

    def test_greeting_and_sign_off_are_not_mentions(self):
        items = [self.item('a', 'Hi Jordan,\nsee attached.\n-- Alex', author='P3')]
        self.resolver().link_mentions(items)
        self.assertNotIn('mentions', items[0]['meta'])

    def test_rare_shared_words_outweigh_one_ordinary_word(self):
        df = {'ships': 3, 'beta': 2, 'timeline': 3, 'plan': 60}
        one = sum(stale.word_weight(w, df) for w in ['ships'])
        two = sum(stale.word_weight(w, df) for w in ['beta', 'timeline'])
        self.assertGreater(two, one)
        self.assertGreater(stale.word_weight('beta', df), stale.word_weight('plan', df))


class Defects(unittest.TestCase):
    def test_refusal_only_when_it_is_the_whole_answer(self):
        self.assertTrue(answer.is_refusal("I can't find that in the available data."))
        self.assertFalse(answer.is_refusal("Jordan is a partner [1]. I can't find that in the available data."))

    def test_inline_reply_sits_under_its_quoted_line(self):
        _, quoted, _ = split_quote('> Keep the churn slide?\ncut this slide\n> Cohort chart?\nadd it')
        self.assertEqual(normalize_inline(quoted).splitlines()[:2], ['quoted: Keep the churn slide?', 'answer: cut this slide'])

    def test_header_without_quote_marks_is_not_an_inline_reply(self):
        self.assertEqual(normalize_inline('On Mon, Jordan wrote:\nthe plan is May 15'), '')

    def test_retraction_why_gives_the_correcting_item(self):
        found = extract.RETRACTED_RE.match("value 'Mar 20' was retracted in slack:C02PROD:1773.5")
        self.assertEqual(found.group(1), 'slack:C02PROD:1773.5')

    def test_promise_is_kept_only_by_the_founders_own_statement(self):
        promise = {'ts': '2026-03-10T10:00:00Z', 'title': 'Data room'}
        def msg(body, author):
            return {'id': 'x', 'ts': '2026-03-11T10:00:00Z', 'author': author, 'kind': 'message', 'body': body, 'flags': []}
        what = 'send data room access'
        self.assertEqual(followups.kept_by(promise, what, [msg("I've sent the data room access to Caroline.", 'P1')], 'P1'), 'x')
        self.assertEqual(followups.kept_by(promise, what, [msg('Did you send the data room access?', 'P1')], 'P1'), '')
        self.assertEqual(followups.kept_by(promise, what, [msg("I've sent the data room access.", 'P2')], 'P1'), '')


class Grounding(unittest.TestCase):
    def conn(self):
        conn = sqlite3.connect(':memory:')
        conn.row_factory = sqlite3.Row
        conn.execute('CREATE TABLE people (id TEXT, name TEXT, org TEXT, role TEXT)')
        conn.executemany('INSERT INTO people VALUES (?,?,?,?)', [
            ('P2', 'Ann Lee', '', ''), ('X1', 'Bo Park', 'Acme Fund', 'investor'), ('X2', 'Cy Roe', 'Acme Fund', 'investor')])
        return conn

    def test_a_mention_must_quote_the_question(self):
        said = {'mentions': [{'words': 'sam', 'refers_to': 'Ann Lee'}], 'source': ''}
        got = route.ground(self.conn(), said, "what's the deal with sso", {})
        self.assertEqual(got['people'], [])

    def test_a_nickname_resolves_to_the_person_it_names(self):
        said = {'mentions': [{'words': 'al', 'refers_to': 'ann lee'}], 'source': ''}
        self.assertEqual(route.ground(self.conn(), said, 'what did al decide', {})['people'], ['P2'])

    def test_a_role_and_a_company_resolve_and_an_invented_name_does_not(self):
        said = {'mentions': [{'words': 'investors', 'refers_to': 'investor'}, {'words': 'acme fund', 'refers_to': 'Acme Fund'},
                             {'words': 'investors', 'refers_to': 'Zed Nobody'}], 'source': ''}
        got = route.ground(self.conn(), said, 'anything from the investors at acme fund', {})
        self.assertEqual((got['role'], got['company'], got['people']), ('investor', 'Acme', []))

    def test_a_tool_needs_a_word_for_it_in_the_question(self):
        said = {'mentions': [], 'source': 'notion'}
        self.assertEqual(route.ground(self.conn(), said, 'is the plan current', {})['source'], '')
        self.assertEqual(route.ground(self.conn(), said, 'is the notion page current', {})['source'], 'notion')


from founder.normalize import inline_replies as normalize_inline  # noqa: E402


if __name__ == '__main__':
    unittest.main()
