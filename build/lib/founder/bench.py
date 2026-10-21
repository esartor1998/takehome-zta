"""Model benchmark: run the three key tasks on each model and compare.

Tasks, each timed and costed on its own:
  load    first call, including cold model load
  ingest  decision labelling over the whole dataset, cold (llm cache cleared)
  brief   the morning brief
  ask     every eval question, judged by one fixed model so scores compare

The judge is held constant across models. Grading each model with itself
would make its score depend on its own blind spots
"""
import json
import re
import time

from . import brief, config, evaluate, ingest, llm, store

CHECKS_PATH = config.ROOT / 'eval' / 'decision_checks.json'
MODELS_DIR = config.ROOT / 'eval' / 'results' / 'models'


def _usage(role):
    row = llm.USAGE.get(role, {})
    return {'calls': row.get('calls', 0), 'prompt_tokens': row.get('prompt_tokens', 0),
            'completion_tokens': row.get('completion_tokens', 0),
            'seconds': row.get('seconds', 0.0), 'cost': row.get('cost', 0.0)}


def decision_checks(conn):
    """Did the model's labels plus our resolvers reach the right state? Three
    kinds of check, each naming items from the answer key: decisions that must
    end with a status, records that must be flagged stale (and two that must
    not), and follow-ups that must be open (and three that must not)"""
    results = []
    for check in json.loads(CHECKS_PATH.read_text()):
        row = conn.execute('SELECT status FROM decisions WHERE item_id=?', (check['item_id'],)).fetchone()
        got = row['status'] if row else 'not labelled'
        ok = got == check['status'] or (check.get('allow_missing') and not row)
        results.append({'name': check['name'], 'ok': bool(ok), 'got': got})
    # checks name items from the answer key. one whose item is not in this export (an older dataset) is left out
    present = {r['id'] for r in conn.execute('SELECT id FROM items')}
    stale = json.loads((CHECKS_PATH.parent / 'stale_checks.json').read_text())
    flagged = {r['item_id'] for r in conn.execute('SELECT item_id FROM stale_records')} | \
              {r['item_id'] for r in conn.execute("SELECT item_id FROM decisions WHERE status='stale'")}
    for item_id in (i for i in stale['must_be_stale'] if i in present):
        results.append({'name': f'stale record found: {item_id}', 'ok': item_id in flagged, 'got': 'stale' if item_id in flagged else 'missed'})
    for item_id in (i for i in stale['must_not_be_stale'] if i in present):
        results.append({'name': f'current record not flagged: {item_id}', 'ok': item_id not in flagged,
                        'got': 'flagged' if item_id in flagged else 'ok'})
    follow = json.loads((CHECKS_PATH.parent / 'followup_checks.json').read_text())
    state = {(r['item_id'], r['kind']): r['status'] for r in conn.execute('SELECT item_id, kind, status FROM followups')}
    for item_id in (i for i in follow['open_asks'] if i in present):
        got = state.get((item_id, 'ask'), 'missing')
        results.append({'name': f'open ask found: {item_id}', 'ok': got == 'open', 'got': got})
    for item_id in (i for i in follow['open_promises'] if i in present):
        got = state.get((item_id, 'promise'), 'missing')
        results.append({'name': f'open promise found: {item_id}', 'ok': got == 'open', 'got': got})
    for item_id in (i for i in follow['must_not_be_open'] if i in present):
        got = state.get((item_id, 'ask'), 'missing')
        results.append({'name': f'handled ask not open: {item_id}', 'ok': got != 'open', 'got': got})
    # people the export names in another way: who wrote this, and which names a person answers to
    identity_path = CHECKS_PATH.parent / 'identity_checks.json'
    if identity_path.exists():
        identity = json.loads(identity_path.read_text())
        for item_id, person in identity['author'].items():
            if item_id in present:
                got = conn.execute('SELECT author FROM items WHERE id=?', (item_id,)).fetchone()['author']
                results.append({'name': f'written by {person}: {item_id}', 'ok': got == person, 'got': got})
        for alias, person in identity['nickname']:
            row = conn.execute('SELECT aliases FROM people WHERE id=?', (person,)).fetchone()
            if row and any(i in present for i in identity['author']):
                results.append({'name': f"'{alias}' is an alias of {person}", 'ok': alias in json.loads(row['aliases']),
                                'got': 'learned' if alias in json.loads(row['aliases']) else 'unknown'})
    return results


def brief_checks(conn, text):
    """Cheap, model-independent facts about the brief: every cited id exists,
    the stale record is called out, and the meeting is in the focus section"""
    ids = set(re.findall(r'\[((?:gmail|slack|linear|calendar|github|crm|notion):[^\]]+)\]', text))
    known = {r['id'] for r in conn.execute('SELECT id FROM items')}
    focus = text.split('## Today')[0]
    return {'cited_ids': len(ids), 'invalid_ids': len(ids - known),
            'stale_called_out': 'out of date' in text.lower(),
            'meeting_in_focus': 'Weekly Product Sync' in focus or 'Globex check-in' in focus}


def bench_model(spec, judge, cold=True):
    config.use_model(spec)
    llm.forget_cache()
    llm.reset_usage()
    out = {'model': config.CHAT_MODEL, 'judge': judge, 'thinking': config.THINKING}
    print(f'\n=== {config.CHAT_MODEL} ===')

    out['load_seconds'] = llm.warm()
    out['placement'] = llm.placement()

    if cold and config.LLM_CACHE_PATH.exists():
        config.LLM_CACHE_PATH.unlink()
        llm.forget_cache()
    if cold:
        # the glossary memo is a second cache. a cold run that kept it would skip the glossary calls and
        # report a cheaper, faster ingest than a first run really is
        (config.STATE_DIR / 'glossary_memo.json').unlink(missing_ok=True)
    llm.reset_usage()
    started = time.time()
    ingest.run()
    out['ingest'] = {'seconds': time.time() - started, **_usage('extract'),
                     'schema_failures': llm.COUNTERS['schema_failures']}
    conn = store.connect()
    out['decision_checks'] = decision_checks(conn)

    llm.reset_usage()
    started = time.time()
    result = brief.generate(conn)
    out['brief'] = {'seconds': time.time() - started, **_usage('brief'),
                    **brief_checks(conn, result['text'])}
    config.STATE_DIR.mkdir(parents=True, exist_ok=True)
    (config.STATE_DIR / 'brief.md').write_text(result['text'])
    conn.close()

    llm.reset_usage()
    started = time.time()
    summary, rows = evaluate.run(judge_model=judge, save=False)
    out['ask'] = {**summary, 'wall_seconds': time.time() - started}
    out['retries'] = llm.COUNTERS['retries']
    out['judge_usage'] = _usage('judge')
    out['rows'] = rows

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    (MODELS_DIR / f'{config.model_slug(config.CHAT_MODEL)}.json').write_text(json.dumps(out, indent=2))
    return out


def pct(value):
    return '-' if value is None else f'{value:.0%}'


def render(results):
    cols = [(r['model'].split(':', 1)[1] if r['model'].startswith('ollama') else r['model']) for r in results]
    cols = [f"{r['model']}" for r in results]
    head = '| metric | ' + ' | '.join(cols) + ' |'
    rule = '| --- |' + ' --- |' * len(cols)

    def row(label, fn):
        return f'| {label} | ' + ' | '.join(fn(r) for r in results) + ' |'

    def checks(r):
        d = r['decision_checks']
        return f"{sum(c['ok'] for c in d)}/{len(d)}"

    def place(r):
        p = r['placement']
        return f"{p['size_gb']:.1f} GB, {100 * p['vram_gb'] / p['size_gb']:.0f}% on gpu" if p else 'hosted'

    def group_accuracy(r, prefix):
        rows = [x for x in r['rows'] if x['id'].startswith(prefix)]
        return f"{sum(x['correct'] for x in rows)}/{len(rows)}" if rows else '-'

    def group_recall(r, prefix):
        rows = [x for x in r['rows'] if x['id'].startswith(prefix)]
        return f"{sum(x['cite_recall'] for x in rows) / len(rows):.0%}" if rows else '-'

    def throughput(r):
        # output tokens per second over the questions that called the model at all
        used = [x for x in r['rows'] if x['completion_tokens']]
        secs = sum(x['seconds'] for x in used)
        return f"{sum(x['completion_tokens'] for x in used) / secs:.0f}" if secs else '-'

    lines = [head, rule,
             row('where it runs', place),
             row('first call incl. load (s)', lambda r: f"{r['load_seconds']:.1f}"),
             row('**ingest** wall (s)', lambda r: f"{r['ingest']['seconds']:.1f}"),
             row('ingest model calls', lambda r: str(r['ingest']['calls'])),
             row('ingest tokens in/out', lambda r: f"{r['ingest']['prompt_tokens']}/{r['ingest']['completion_tokens']}"),
             row('ingest cost ($)', lambda r: f"{r['ingest']['cost']:.4f}"),
             row('ingest checks passed (decisions, stale, follow-ups)', checks),
             row('**brief** wall (s)', lambda r: f"{r['brief']['seconds']:.1f}"),
             row('brief cost ($)', lambda r: f"{r['brief']['cost']:.5f}"),
             row('brief invalid ids', lambda r: str(r['brief']['invalid_ids'])),
             row('brief stale record called out', lambda r: 'yes' if r['brief']['stale_called_out'] else 'NO'),
             row('brief meeting in focus', lambda r: 'yes' if r['brief']['meeting_in_focus'] else 'NO'),
             row('**ask** accuracy (judge)', lambda r: f"{r['ask']['accuracy']:.0%}"),
             row('ask accuracy, original questions (q*)', lambda r: group_accuracy(r, 'q')),
             row('ask accuracy, vague questions (v*)', lambda r: group_accuracy(r, 'v')),
             row('ask citation recall', lambda r: f"{r['ask']['citation_recall']:.0%}"),
             row('ask citation recall, vague (v*)', lambda r: group_recall(r, 'v')),
             row('ask citation precision', lambda r: f"{r['ask']['citation_precision']:.0%}"),
             row('ask answers with a citation flag', lambda r: str(r['ask'].get('flagged_answers', '-'))),
             row('ask flag precision (flagged and judged wrong)', lambda r: pct(r['ask'].get('flag_precision'))),
             row('ask flag recall (wrong answers that were flagged)', lambda r: pct(r['ask'].get('flag_recall'))),
             row('ask forbidden cites', lambda r: str(r['ask']['forbidden_cites'])),
             row('ask uncited sentences', lambda r: str(r['ask']['ungrounded_sentences'])),
             row('ask latency p50 (s)', lambda r: f"{r['ask']['latency_p50']:.1f}"),
             row('ask latency p95 (s)', lambda r: f"{r['ask']['latency_p95']:.1f}"),
             row('ask latency max (s)', lambda r: f"{r['ask']['latency_max']:.1f}"),
             row('ask questions over 5s', lambda r: str(r['ask']['latency_over_budget'])),
             row('ask output tokens per second', throughput),
             row('ask latency mean (s)', lambda r: f"{r['ask']['latency_mean']:.1f}"),
             row('ask questions answered without a model call', lambda r: str(sum(1 for x in r['rows'] if not x['prompt_tokens'] + x['completion_tokens'] - x.get('plan_tokens', 0)))),
             row('ask tokens in/out (mean)', lambda r: f"{r['ask']['tokens_in_mean']:.0f}/{r['ask']['tokens_out_mean']:.0f}"),
             row('ask cost per question ($)', lambda r: f"{r['ask']['actual_cost_mean']:.5f}"),
             row('ask refusals', lambda r: str(r['ask']['refusals'])),
             row('judge verdicts that failed (counted wrong)', lambda r: str(r['ask'].get('judge_failures', '-'))),
             row('schema failures (ask+judge)', lambda r: str(r['ask']['schema_failures'])),
             row('http retries (rate limits, 5xx)', lambda r: str(r.get('retries', '-'))),
             row('whole benchmark wall time (s)', lambda r: f"{r['ingest']['seconds'] + r['brief']['seconds'] + r['ask']['wall_seconds']:.0f}"),
             row('judge cost for this run ($)', lambda r: f"{r['judge_usage']['cost']:.4f}")]
    return '\n'.join(lines)


def rejudge_all(judge):
    """Re-grade every saved answer with the current judge, leaving the answers,
    times and costs as they were. Used when the grading rule changes, so the
    four columns stay comparable without re-running four models"""
    questions = {q['id']: q for q in json.loads(evaluate.QUESTIONS_PATH.read_text())}
    for path in sorted(MODELS_DIR.glob('*.json')):
        data = json.loads(path.read_text())
        llm.reset_usage()
        for row in data['rows']:
            q = questions[row['id']]
            row['correct'], row['judge_reason'] = evaluate.judge(q['question'], evaluate.reference_text(q), row['answer'], judge)
        kept = {k: data['ask'][k] for k in ('wall_seconds', 'warm_seconds') if k in data['ask']}
        data['ask'] = {**evaluate.summarize(data['rows'], judge), **kept}
        data['judge'] = judge
        path.write_text(json.dumps(data, indent=2))
        print(f"{data['model']}: accuracy {data['ask']['accuracy']:.0%}")


def judge_agreement(judges, path=None):
    """How much do graders agree? Re-grade one model's saved answers with each judge,
    twice for the first (self-consistency, which should be 100% at temperature 0 and
    is not for hosted models), and report raw agreement and Cohen's kappa between
    judges. Accuracy numbers mean little without this: a judge that disagrees with
    itself or with a second judge on a fifth of the answers caps what any benchmark
    can show"""
    path = path or sorted(MODELS_DIR.glob('*.json'))[0]
    data = json.loads(path.read_text())
    questions = {q['id']: q for q in json.loads(evaluate.QUESTIONS_PATH.read_text())}
    verdicts = {}
    for label, judge in [(f'{judges[0]} (first pass)', judges[0]), (f'{judges[0]} (second pass)', judges[0])] + \
            [(j, j) for j in judges[1:]]:
        verdicts[label] = [evaluate.judge(questions[r['id']]['question'], evaluate.reference_text(questions[r['id']]), r['answer'], judge)[0]
                           for r in data['rows']]
    labels = list(verdicts)
    saved = [r['correct'] for r in data['rows']]
    out = {'answers_graded': len(saved), 'model': data['model'], 'pairs': []}

    def kappa(a, b):
        n = len(a)
        po = sum(x == y for x, y in zip(a, b)) / n
        pa, pb = sum(a) / n, sum(b) / n
        pe = pa * pb + (1 - pa) * (1 - pb)
        return (po - pe) / (1 - pe) if pe < 1 else 1.0

    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            out['pairs'].append({'a': a, 'b': b, 'agreement': sum(x == y for x, y in zip(verdicts[a], verdicts[b])) / len(saved),
                                 'kappa': kappa(verdicts[a], verdicts[b])})
    out['accuracy_by_judge'] = {k: sum(v) / len(v) for k, v in verdicts.items()}
    (config.ROOT / 'eval' / 'results' / 'judge_agreement.json').write_text(json.dumps(out, indent=2))
    for pair in out['pairs']:
        print(f"{pair['a']} vs {pair['b']}: agree {pair['agreement']:.0%}, kappa {pair['kappa']:.2f}")
    return out


def load_all():
    """Every model result saved so far, so a benchmark run of one model adds a
    column to the table instead of replacing it"""
    return [json.loads(p.read_text()) for p in sorted(MODELS_DIR.glob('*.json'))]


def report(judge=None):
    results = load_all()
    table = render(results)
    judges = sorted({r['judge'] for r in results})
    path = config.ROOT / 'eval' / 'results' / 'benchmark.md'
    path.write_text(f"# Model benchmark\n\njudge: {', '.join(f'`{j}`' for j in judges)} for every column. "
                    f"questions: {results[0]['ask']['questions']}.\n\n{table}\n")
    print('\n' + table)
    return results


def run(specs, judge, cold=True):
    for spec in specs:
        bench_model(spec, judge, cold)
    return report(judge)
