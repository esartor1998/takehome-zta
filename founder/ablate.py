"""Ablation tests: does each retrieval pull earn its place, the vector store
included?

Retrieval fuses five pulls (fts, vector, window, person, structured). The
vector pull is the expensive and least predictable one, so these tests switch
pulls off one at a time and measure what happens to the evidence a model would
see, with no language model involved:

  recall      share of an answer's expected evidence groups present in context
  complete    share of questions where every group is present
  precision   share of context items that belong to an expected group
  mrr         how high the first expected item ranks
  rescued     expected items the full pipeline has and the variant lacks
  displaced   expected items the variant has and the full pipeline lacks

Only questions that go through retrieval count. Schedule, follow-up, blocked and
similar questions are rendered by code from the database and never touch the
vector store, so including them would dilute the answer.

The verdict that matters is per question: how many does the vector pull
help, hurt, or leave alone. `--e2e` repeats that comparison with a model
answering and a judge grading, because better evidence is not the same as a
better answer.
"""
import json

from . import answer, config, evaluate, llm, retrieve, route, store

CONFIGS = {
    'full': {},
    'no_vector': {'disable': {'vector'}},
    'vector_only': {'disable': {'fts', 'window', 'person', 'structured'}},
    'no_fts': {'disable': {'fts', 'window'}},
    'fts_only': {'disable': {'vector', 'person', 'structured'}},
    'no_structured': {'disable': {'structured'}},
    'vector_x0.5': {'weights': {'vector': 0.5}},
    'vector_x2': {'weights': {'vector': 2.0}},
}
PROBES_PATH = config.ROOT / 'eval' / 'semantic_probes.json'
OUT_MD = config.ROOT / 'eval' / 'results' / 'ablation.md'
OUT_JSON = config.ROOT / 'eval' / 'results' / 'ablation.json'


def retrieval_questions(conn, path=None):
    """Answerable questions that go through retrieval, with their plans"""
    cases = []
    for q in json.loads((path or evaluate.QUESTIONS_PATH).read_text()):
        if not q['answerable']:
            continue
        plan = route.plan(conn, q['question'])
        if answer.digest_facts(conn, plan, q['question']) is not None:
            continue
        cases.append((q, plan))
    return cases


def context_ids(conn, question, plan, **options):
    """The items a model could cite for this question under one configuration:
    what retrieval picked, plus the current-decision items it adds"""
    found = retrieve.retrieve(conn, question, plan=plan, **options)
    ids = answer.expand_decision_context(conn, found['ids'], found['decision_topics'])
    ids = [i for i in ids if not (re_email_only(question) and not i.startswith(('gmail:', 'calendar:')))]
    cited = [cite for _, cite in answer.decision_timelines(conn, found['decision_topics'])]
    return ids, [c for c in cited if c not in ids]


def re_email_only(question):
    import re
    return bool(re.search(r'\bemails?\b', question, re.I))


def score(ids, extra, groups):
    allowed = {i for g in groups for i in g}
    present = set(ids) | set(extra)
    hit = sum(1 for g in groups if present & set(g))
    first = next((n for n, i in enumerate(ids, 1) if i in allowed), None)
    return {'recall': hit / len(groups), 'complete': hit == len(groups),
            'precision': (len(set(ids) & allowed) / len(ids)) if ids else 0.0,
            'mrr': (1 / first) if first else 0.0, 'size': len(ids),
            'present': sorted(present & allowed)}


def evaluate_set(conn, cases):
    results = {name: {} for name in CONFIGS}
    for q, plan in cases:
        for name, options in CONFIGS.items():
            ids, extra = context_ids(conn, q['question'], plan, **options)
            results[name][q['id']] = score(ids, extra, q['expected_ids'])
    return results


def timings(conn, cases):
    """Milliseconds each pull takes, averaged over the questions. The vector pull
    pays for an embedding call on every question, so its cost has to be set
    against what it finds"""
    import time
    totals = {'fts': 0.0, 'vector': 0.0, 'person': 0.0, 'structured': 0.0}
    for q, plan in cases:
        text = q['question']
        people = set(plan.people)
        for name, call in (('fts', lambda: retrieve.pull_fts(conn, text)),
                           ('vector', lambda: retrieve.pull_vector(conn, text)),
                           ('person', lambda: retrieve.pull_person(conn, people, text)),
                           ('structured', lambda: retrieve.pull_structured(conn, text, retrieve.detect_intents(text), None, people))):
            start = time.perf_counter()
            call()
            totals[name] += time.perf_counter() - start
    return {k: 1000 * v / len(cases) for k, v in totals.items()}


def run(e2e=False, judge=None):
    conn = store.connect()
    cases = retrieval_questions(conn)
    probes = retrieval_questions(conn, PROBES_PATH)
    print(f'{len(cases)} eval questions and {len(probes)} semantic probes go through retrieval')
    results = evaluate_set(conn, cases)
    probe_results = evaluate_set(conn, probes)
    report = summarise(cases, results, 'Eval questions that use retrieval')
    report += summarise(probes, probe_results, 'Semantic probes: questions worded unlike the source text', levels=2)
    ms = timings(conn, cases)
    report += ('\n## What each pull costs\n\nMean milliseconds per question: ' +
               ', '.join(f'{k} {v:.0f}' for k, v in ms.items()) + '.\n')
    if e2e:
        report += end_to_end(cases, judge)
    OUT_MD.write_text(report)
    OUT_JSON.write_text(json.dumps({'questions': results, 'probes': probe_results, 'ms': ms}, indent=2))
    print(report)
    return results


def mean(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def summarise(cases, results, title, levels=1):
    ids = [q['id'] for q, _ in cases]
    lines = [('#' * levels) + ' ' + title, '',
             f'{len(ids)} answerable questions that go through retrieval '
             f'(model: none, embeddings: `{config.EMBED_MODEL}`, store: `{config.DB_PATH.parent.name}`).', '',
             '| configuration | recall | every group present | precision | mrr | items in context |',
             '| --- | --- | --- | --- | --- | --- |']
    for name in CONFIGS:
        r = results[name]
        lines.append(f"| {name} | {mean(r[i]['recall'] for i in ids):.0%} | {mean(r[i]['complete'] for i in ids):.0%} | "
                     f"{mean(r[i]['precision'] for i in ids):.0%} | {mean(r[i]['mrr'] for i in ids):.2f} | "
                     f"{mean(r[i]['size'] for i in ids):.1f} |")

    full, plain = results['full'], results['no_vector']
    helped = [i for i in ids if full[i]['recall'] > plain[i]['recall']]
    hurt = [i for i in ids if full[i]['recall'] < plain[i]['recall']]
    rescued = {i: sorted(set(full[i]['present']) - set(plain[i]['present'])) for i in ids}
    displaced = {i: sorted(set(plain[i]['present']) - set(full[i]['present'])) for i in ids}
    p_up = [i for i in ids if full[i]['precision'] > plain[i]['precision'] + 1e-9]
    p_down = [i for i in ids if full[i]['precision'] < plain[i]['precision'] - 1e-9]
    lines += ['', '### Vector pull, question by question (full against no_vector)', '',
              f'- recall: helps on **{len(helped)}**, hurts on **{len(hurt)}**, no change on {len(ids) - len(helped) - len(hurt)}',
              f'- precision: higher with the vector pull on {len(p_up)}, lower on {len(p_down)}',
              f"- expected items it brought in: **{sum(len(v) for v in rescued.values())}**, "
              f"expected items it pushed out: **{sum(len(v) for v in displaced.values())}**",
              f"- items per context: {mean(full[i]['size'] for i in ids):.1f} with, {mean(plain[i]['size'] for i in ids):.1f} without", '',
              '| question | recall full | recall no_vector | precision full | precision no_vector | brought in | pushed out |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    by_id = {q['id']: q for q, _ in cases}
    for i in ids:
        if (full[i]['recall'], full[i]['precision']) == (plain[i]['recall'], plain[i]['precision']) and not rescued[i] and not displaced[i]:
            continue
        lines.append(f"| `{i}` {by_id[i]['question'][:44]} | {full[i]['recall']:.0%} | {plain[i]['recall']:.0%} | "
                     f"{full[i]['precision']:.0%} | {plain[i]['precision']:.0%} | {len(rescued[i])} | {len(displaced[i])} |")
    vector_alone = results['vector_only']
    lines += ['', '### On its own', '',
              f"The vector pull alone reaches {mean(vector_alone[i]['recall'] for i in ids):.0%} recall "
              f"(every group on {mean(vector_alone[i]['complete'] for i in ids):.0%} of questions), against "
              f"{mean(results['fts_only'][i]['recall'] for i in ids):.0%} for full text search alone and "
              f"{mean(plain[i]['recall'] for i in ids):.0%} for everything except vectors.", '']
    return '\n'.join(lines) + '\n'


def end_to_end(cases, judge):
    """Answer and grade the same questions with the vector pull on and off"""
    judge = judge or config.CHAT_MODEL
    ids = [q['id'] for q, _ in cases]
    out = {}
    for name, disabled in (('full', set()), ('no_vector', {'vector'})):
        config.DISABLED_PULLS = disabled
        llm.warm()
        summary, rows = evaluate.run(judge_model=judge, only=ids, save=False)
        out[name] = (summary, {r['id']: r for r in rows})
    config.DISABLED_PULLS = set()
    full, plain = out['full'][1], out['no_vector'][1]
    flips_up = [i for i in ids if full[i]['correct'] and not plain[i]['correct']]
    flips_down = [i for i in ids if plain[i]['correct'] and not full[i]['correct']]
    lines = ['', f'## End to end with `{config.CHAT_MODEL}`, judged by `{judge}`', '',
             '| | accuracy | citation recall | citation precision | median seconds |', '| --- | --- | --- | --- | --- |']
    for name in ('full', 'no_vector'):
        s = out[name][0]
        lines.append(f"| {name} | {s['accuracy']:.0%} | {s['citation_recall']:.0%} | {s['citation_precision']:.0%} | {s['latency_p50']:.1f} |")
    lines += ['', f"Judged correct only with the vector pull: {', '.join(flips_up) or 'none'}. "
                  f"Judged correct only without it: {', '.join(flips_down) or 'none'}.", '']
    return '\n'.join(lines)
