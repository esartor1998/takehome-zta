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
do not depend on any model.
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
    'properties': {'correct': {'type': 'boolean'}, 'reason': {'type': 'string'}},
    'required': ['correct', 'reason'],
}
JUDGE_SYSTEM = (
    'You grade an assistant answer against a reference answer. Reply with JSON only.\n'
    'correct = true when the candidate states the same key facts as the reference '
    '(same dates, times, names, decision) and does not contradict it or present '
    'outdated information as current. Extra true detail is fine.\n'
    'When the reference says the information is not available, correct = true only if '
    'the candidate says it cannot find the information and gives no specific figures.\n'
    'Keep reason under 20 words.')


def judge(question, reference, candidate, model):
    prompt = f'Question: {question}\nReference: {reference}\nCandidate: {candidate}'
    result = llm.chat(JUDGE_SYSTEM, prompt, schema=JUDGE_SCHEMA, model=model, max_tokens=80)
    try:
        parsed = json.loads(result['text'])
        return bool(parsed['correct']), parsed.get('reason', '')
    except (ValueError, KeyError):
        return False, 'judge returned invalid json'


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


def projected_cost(result):
    return (result['prompt_tokens'] * config.PROJECTED_PRICE_IN
            + result['completion_tokens'] * config.PROJECTED_PRICE_OUT) / 1e6


def run(judge_model=None, only=None):
    judge_model = judge_model or config.CHAT_MODEL
    questions = json.loads(QUESTIONS_PATH.read_text())
    if only:
        questions = [q for q in questions if q['id'] in only]
    conn = store.connect()
    llm.warm()
    rows = []
    for q in questions:
        result = answer.ask(conn, q['question'])
        correct, reason = judge(q['question'], q['reference'], result['answer'], judge_model)
        cites = citation_scores(q, result)
        rows.append({
            'id': q['id'], 'category': q['category'], 'question': q['question'],
            'answer': result['answer'], 'correct': correct, 'judge_reason': reason,
            'found': result['found'], 'cited': result['cited'], **{f'cite_{k}': v for k, v in cites.items()},
            'ungrounded': len(result['ungrounded_sentences']), 'seconds': result['seconds'],
            'prompt_tokens': result['prompt_tokens'], 'completion_tokens': result['completion_tokens'],
            'projected_cost': projected_cost(result),
        })
        print(f"{q['id']} {'PASS' if correct else 'FAIL'} cite r={cites['recall']:.2f} "
              f"p={cites['precision']:.2f} f={cites['forbidden']} {result['seconds']:.1f}s  {q['question']}")
    summary = summarize(rows, judge_model)
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
        'latency_over_budget': sum(s > BUDGET_SECONDS for s in secs),
        'tokens_in_mean': mean(r['prompt_tokens'] for r in rows),
        'tokens_out_mean': mean(r['completion_tokens'] for r in rows),
        'projected_cost_mean': mean(r['projected_cost'] for r in rows),
        'actual_cost': 0.0,
    }


def render_summary(s):
    return (f"\naccuracy {s['accuracy']:.0%} | citation recall {s['citation_recall']:.0%} "
            f"precision {s['citation_precision']:.0%} | forbidden cites {s['forbidden_cites']} | "
            f"ungrounded sentences {s['ungrounded_sentences']}\n"
            f"latency p50 {s['latency_p50']:.1f}s max {s['latency_max']:.1f}s "
            f"({s['latency_over_budget']} over {BUDGET_SECONDS:.0f}s) | "
            f"projected hosted cost ${s['projected_cost_mean']:.4f}/question, actual $0 (local)")


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
