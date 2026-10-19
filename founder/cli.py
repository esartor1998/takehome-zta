"""Command line entry. `founder` alone prints the morning brief."""
import argparse
import sys
from pathlib import Path

from . import brief, config, ingest, llm, store


def cmd_ingest(args):
    ingest.run(skip_decisions=args.skip_decisions)


def _ready():
    if not config.DB_PATH.exists():
        print('no context store yet, ingesting first')
        ingest.run()
    return store.connect()


def cmd_ask(args):
    from . import answer
    conn = _ready()
    result = answer.ask(conn, ' '.join(args.question))
    print(result['answer'])
    if result['ungrounded_sentences']:
        print(f"\n(warning: {len(result['ungrounded_sentences'])} sentence(s) without a valid citation)")
    print(f"\n{result['seconds']:.1f}s, {result['prompt_tokens']}+{result['completion_tokens']} tokens")


def cmd_brief(args):
    conn = _ready()
    result = brief.generate(conn)
    print(result['text'])
    if args.save:
        args.save.parent.mkdir(parents=True, exist_ok=True)
        args.save.write_text(result['text'])


def cmd_eval(args):
    from . import evaluate
    evaluate.run(judge_model=args.judge_model, only=args.only)


def cmd_chat(args):
    from . import answer
    conn = _ready()
    print('ask anything, empty line to quit')
    while True:
        try:
            question = input('> ').strip()
        except EOFError:
            break
        if not question:
            break
        result = answer.ask(conn, question)
        print(result['answer'], f"\n[{result['seconds']:.1f}s]\n")


def main(argv=None):
    parser = argparse.ArgumentParser(prog='founder', description='founder context engine')
    sub = parser.add_subparsers(dest='command')
    ing = sub.add_parser('ingest', help='rebuild the context store from data/raw')
    ing.add_argument('--skip-decisions', action='store_true', help='skip llm decision labelling')
    ing.set_defaults(func=cmd_ingest)
    ask = sub.add_parser('ask', help='ask a question across all sources')
    ask.add_argument('question', nargs='+')
    ask.set_defaults(func=cmd_ask)
    br = sub.add_parser('brief', help='print the morning brief')
    br.add_argument('--save', type=Path)
    br.set_defaults(func=cmd_brief)
    ev = sub.add_parser('eval', help='run eval/questions.json and report accuracy, cites, latency')
    ev.add_argument('--judge-model', help='ollama model for the judge (default: same as answers)')
    ev.add_argument('--only', nargs='*', help='question ids to run')
    ev.set_defaults(func=cmd_eval)
    sub.add_parser('chat', help='interactive questions').set_defaults(func=cmd_chat)

    args = parser.parse_args(argv)
    if not args.command:
        args = parser.parse_args(['brief'])
    args.func(args)


if __name__ == '__main__':
    sys.exit(main())
