"""Evaluation harness: runs eval/questions.json against the live system.

Reports, per question and overall:
  accuracy           an llm judge compares the answer to a reference answer
  citation recall    share of expected evidence groups with at least one cited
                     member (a group lists interchangeable copies, like the
                     same update in gmail and slack)
  citation precision share of cited ids that are in any expected group
  forbidden cites    cited ids that are known stale or superseded
  latency and cost   wall time, tokens, and the projected hosted-model cost

The judge is the same local 3B model unless --judge-model says otherwise, so
treat accuracy as a rough signal. Citation numbers are plain id comparison and
do not depend on any model
"""
import json
import statistics
import time

from . import answer, config, llm, store

QUESTIONS_PATH = config.ROOT / 'eval' / 'questions.json'
RESULTS_DIR = config.ROOT / 'eval' / 'results'
BUDGET_SECONDS = 5.0
BUDGET_DOLLARS = 0.02

JUDGE_SCHEMA = {
    'type': 'object',
    'properties': {
        'reference_key_fact': {'type': 'string'},
        'candidate_says': {'type': 'string'},
        'correct': {'type': 'boolean'},
    },
    'required': ['reference_key_fact', 'candidate_says', 'correct'],
}
# two judge designs failed on this model and are why this one has the fields
# in this order. a bare verdict passed answers about the wrong topic (a reply
# about a moved Globex call to a question about an addendum). asking for lists
# of missing and wrong facts made it flag the reference's own facts as wrong
# writing the key fact and what the candidate says before the verdict, plus two
# worked examples, is the version that behaved
JUDGE_SYSTEM = (
    'You grade a candidate answer against a reference answer. Reply with JSON only, '
    'fields in this order.\n'
    'reference_key_fact: the one or two facts the reference is about, in under 20 words.\n'
    'candidate_says: what the candidate states about those facts, in under 20 words.\n'
    'correct: true only if the candidate states the same facts as the reference and does not '
    'present outdated information as current. false if it is about something else, misses a '
    'listed item, or gives a different date, time, name or decision. Extra true detail is fine. '
    'When the reference says the information is not available, correct is true only if the '
    'candidate says it cannot find it.\n\n'
    'Example 1\nQuestion: When is the launch?\nReference: The launch is March 22, corrected from March 20.\n'
    'Candidate: The launch is on March 20.\n'
    '{"reference_key_fact": "launch is March 22", "candidate_says": "launch is March 20", "correct": false}\n\n'
    'Example 2\nQuestion: Who owns billing?\nReference: Priya Nair owns billing.\n'
    'Candidate: Billing is owned by Priya Nair, who joined in January.\n'
    '{"reference_key_fact": "Priya Nair owns billing", "candidate_says": "Priya Nair owns billing", "correct": true}')


def judge(question, reference, candidate, model):
    prompt = f'Question: {question}\nReference: {reference}\nCandidate: {candidate}'
    parsed = None
    # a long answer can make the judge run out of tokens mid-json. one retry with more room
    # before giving up, and a verdict we never got is counted as a judge failure in the summary
    for room in (300, 700):
        result = llm.chat(JUDGE_SYSTEM, prompt, schema=JUDGE_SCHEMA, model=model, max_tokens=room, role='judge')
        parsed = llm.parse_json(result['text'], None)
        if parsed and 'correct' in parsed:
            break
    if not parsed or 'correct' not in parsed:
        return False, 'judge returned invalid json'
    return bool(parsed['correct']), f"ref: {parsed['reference_key_fact']} | cand: {parsed['candidate_says']}"


def citation_scores(question, result):
    cited = set(result['cited'])
    groups = question['expected_ids']
    if not question['answerable']:
        return {'recall': 1.0 if not cited else 0.0, 'precision': 1.0 if not cited else 0.0,
                'forbidden': 0}
    hits = sum(1 for group in groups if cited & set(group))
    allowed = {i for group in groups for i in group}
    return {
        'recall': hits / len(groups),
        'precision': len(cited & allowed) / len(cited) if cited else 0.0,
        'forbidden': len(cited & set(question['forbidden_ids'])),
    }


def rejudge(path, judge_model=None):
    """Re-grade saved answers with the current judge. Lets a judge change be
    measured on its own, without re-running the system under test"""
    judge_model = judge_model or config.JUDGE_MODEL
    questions = {q['id']: q for q in json.loads(QUESTIONS_PATH.read_text())}
    data = json.loads(path.read_text())
    for row in data['rows']:
        q = questions[row['id']]
        row['correct'], row['judge_reason'] = judge(q['question'], q['reference'], row['answer'], judge_model)
    data['summary'] = summarize(data['rows'], judge_model)
    return data


def run(judge_model=None, only=None, save=True):
    judge_model = judge_model or config.JUDGE_MODEL
    questions = json.loads(QUESTIONS_PATH.read_text())
    if only:
        questions = [q for q in questions if q['id'] in only]
    conn = store.connect()
    warm_seconds = llm.warm()
    llm.warm(judge_model) if judge_model != config.CHAT_MODEL else None
    rows = []
    for q in questions:
        result = answer.ask(conn, q['question'])
        correct, reason = judge(q['question'], q['reference'], result['answer'], judge_model)
        cites = citation_scores(q, result)
        rows.append({
            'id': q['id'], 'category': q['category'], 'question': q['question'],
            'answer': result['answer'], 'correct': correct, 'judge_reason': reason,
            'found': result['found'], 'cited': result['cited'], **{f'cite_{k}': v for k, v in cites.items()},
            'ungrounded': len(result['ungrounded_sentences']), 'flags': result.get('flags', []), 'cites_dropped': result['cites_dropped'], 'cites_added': result['cites_added'], 'seconds': result['seconds'],
            'prompt_tokens': result['prompt_tokens'], 'completion_tokens': result['completion_tokens'],
            'cost': result['cost'], 'projected_cost': result['projected_cost'],
        })
        print(f"{q['id']} {'PASS' if correct else 'FAIL'} cite r={cites['recall']:.2f} "
              f"p={cites['precision']:.2f} f={cites['forbidden']} {result['seconds']:.1f}s  {q['question']}")
    summary = summarize(rows, judge_model)
    summary['warm_seconds'] = warm_seconds
    if save:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        (RESULTS_DIR / 'latest.json').write_text(json.dumps({'summary': summary, 'rows': rows}, indent=2))
        (RESULTS_DIR / 'latest.md').write_text(render_markdown(summary, rows))
    print(render_summary(summary))
    return summary, rows


def summarize(rows, judge_model):
    secs = sorted(r['seconds'] for r in rows)
    mean = statistics.mean
    return {
        'questions': len(rows), 'model': config.CHAT_MODEL, 'judge_model': judge_model,
        'accuracy': mean(r['correct'] for r in rows),
        'citation_recall': mean(r['cite_recall'] for r in rows),
        'citation_precision': mean(r['cite_precision'] for r in rows),
        'forbidden_cites': sum(r['cite_forbidden'] for r in rows),
        'ungrounded_sentences': sum(r['ungrounded'] for r in rows),
        'latency_p50': statistics.median(secs), 'latency_max': secs[-1],
        'latency_p95': secs[min(len(secs) - 1, int(round(0.95 * (len(secs) - 1))))],
        'latency_mean': mean(secs), 'schema_failures': llm.COUNTERS['schema_failures'],
        'refusals': sum(not r['found'] for r in rows),
        **flag_quality(rows),
        'judge_failures': sum(1 for r in rows if r['judge_reason'] == 'judge returned invalid json'),
        'latency_over_budget': sum(s > BUDGET_SECONDS for s in secs),
        'tokens_in_mean': mean(r['prompt_tokens'] for r in rows),
        'tokens_out_mean': mean(r['completion_tokens'] for r in rows),
        'projected_cost_mean': mean(r['projected_cost'] for r in rows),
        'actual_cost_mean': mean(r['cost'] for r in rows),
        'actual_cost_total': sum(r['cost'] for r in rows),
    }


def flag_quality(rows):
    """Does the citation flag mean anything? An answer is flagged when a claim's
    citation did not hold and the model could not repair it. Flag precision is the
    share of flagged answers the judge also marked wrong, and flag recall is the
    share of wrong answers that carried a flag. Both are low-count numbers on 41
    questions, so read them as direction"""
    flagged = [r for r in rows if r.get('flags')]
    wrong = [r for r in rows if not r['correct']]
    both = [r for r in flagged if not r['correct']]
    return {'flagged_answers': len(flagged), 'flag_precision': len(both) / len(flagged) if flagged else None,
            'flag_recall': len(both) / len(wrong) if wrong else None,
            'flags_total': sum(len(r.get('flags', [])) for r in rows)}


def render_summary(s):
    return (f"\naccuracy {s['accuracy']:.0%} | citation recall {s['citation_recall']:.0%} "
            f"precision {s['citation_precision']:.0%} | forbidden cites {s['forbidden_cites']} | "
            f"ungrounded sentences {s['ungrounded_sentences']}\n"
            f"latency p50 {s['latency_p50']:.1f}s max {s['latency_max']:.1f}s "
            f"({s['latency_over_budget']} over {BUDGET_SECONDS:.0f}s) | "
            f"cost ${s['actual_cost_mean']:.5f}/question actual, ${s['projected_cost_mean']:.5f} at hosted rates")


def render_markdown(s, rows):
    lines = [f"# Eval results ({s['questions']} questions)", '',
             f"model `{s['model']}`, judge `{s['judge_model']}`", '', '```', render_summary(s).strip(),
             '```', '', '| id | category | correct | cite recall | cite precision | forbidden | sec |',
             '| --- | --- | --- | --- | --- | --- | --- |']
    for r in rows:
        lines.append(f"| {r['id']} | {r['category']} | {'yes' if r['correct'] else 'NO'} | "
                     f"{r['cite_recall']:.2f} | {r['cite_precision']:.2f} | {r['cite_forbidden']} | "
                     f"{r['seconds']:.1f} |")
    lines += ['', '## Answers', '']
    for r in rows:
        lines += [f"**{r['id']}** {r['question']}", f"> {r['answer']}",
                  f"judge: {'pass' if r['correct'] else 'FAIL'} ({r['judge_reason']})", '']
    return '\n'.join(lines)
