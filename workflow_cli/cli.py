from __future__ import annotations

import argparse
import sys
from textwrap import dedent

from .db import init_db
from .services import (
    create_task,
    delete_task,
    get_task,
    get_task_tags,
    list_tasks,
    update_task,
)

def _print_task(task, tags: list[str] | None = None) -> None:
    tags = tags or []
    tag_str = f"  tags: {', '.join(tags)}" if tags else "  tags: (none)"
    print(f"[{task.id}] {task.title}")
    print(f"  status: {task.status} | priority: {task.priority}")
    if task.description:
        print(f"  desc: {task.description}")
    print(tag_str)
    print(f"  created: {task.created_at} | updated: {task.updated_at}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Workflow Management System (CLI) — CRUD + SQLite",
        epilog=dedent(
            """
            Examples:
              workflow init
              workflow add --title "Fix bug" --desc "Repro steps..." --priority 4 --tag backend --tag urgent
              workflow list --status todo --sort priority
              workflow show 1
              workflow update 1 --status in_progress --add-tag sprint-1
              workflow done 1
              workflow delete 1
            """
        ).strip(),
    )

    p.add_argument("--db", default=None, help="Path to SQLite db file (default: ./workflow.db)")

    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Initialize database schema")

    add = sub.add_parser("add", help="Create a new task")
    add.add_argument("--title", required=True)
    add.add_argument("--desc", default="")
    add.add_argument("--status", default="todo", choices=["todo", "in_progress", "done"])
    add.add_argument("--priority", default=3, type=int)
    add.add_argument("--tag", action="append", default=[], help="Repeatable tag: --tag backend --tag urgent")

    ls = sub.add_parser("list", help="List tasks")
    ls.add_argument("--status", default=None, choices=["todo", "in_progress", "done"])
    ls.add_argument("--q", default=None, help="Search in title/description")
    ls.add_argument("--tag", default=None, help="Filter by a tag name")
    ls.add_argument("--sort", default="new", choices=["new", "old", "priority", "status"])
    ls.add_argument("--limit", default=50, type=int)
    ls.add_argument("--offset", default=0, type=int)

    show = sub.add_parser("show", help="Show a task by id")
    show.add_argument("id", type=int)

    upd = sub.add_parser("update", help="Update task fields")
    upd.add_argument("id", type=int)
    upd.add_argument("--title", default=None)
    upd.add_argument("--desc", default=None)
    upd.add_argument("--status", default=None, choices=["todo", "in_progress", "done"])
    upd.add_argument("--priority", default=None, type=int)
    upd.add_argument("--add-tag", action="append", default=[])
    upd.add_argument("--remove-tag", action="append", default=[])

    done = sub.add_parser("done", help="Mark task as done")
    done.add_argument("id", type=int)

    delete = sub.add_parser("delete", help="Delete a task")
    delete.add_argument("id", type=int)

    return p

def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.cmd == "init":
            init_db(args.db)
            print("✅ Database initialized.")
            return 0

        init_db(args.db)  # ensure schema exists before CRUD commands

        if args.cmd == "add":
            task = create_task(
                title=args.title,
                description=args.desc,
                status=args.status,
                priority=args.priority,
                tags=args.tag,
                db_path=args.db,
            )
            print("✅ Created:")
            _print_task(task, get_task_tags(task.id, args.db))
            return 0

        if args.cmd == "list":
            tasks = list_tasks(
                status=args.status,
                q=args.q,
                tag=args.tag,
                sort=args.sort,
                limit=args.limit,
                offset=args.offset,
                db_path=args.db,
            )
            if not tasks:
                print("(no tasks found)")
                return 0
            for t in tasks:
                tags = get_task_tags(t.id, args.db)
                print(f"[{t.id}] {t.title} | {t.status} | p{t.priority} | tags:{','.join(tags) if tags else '-'}")
            return 0

        if args.cmd == "show":
            task = get_task(args.id, args.db)
            if not task:
                print("Not found.")
                return 1
            _print_task(task, get_task_tags(task.id, args.db))
            return 0

        if args.cmd == "update":
            task = update_task(
                task_id=args.id,
                title=args.title,
                description=args.desc,
                status=args.status,
                priority=args.priority,
                add_tags=args.add_tag,
                remove_tags=args.remove_tag,
                db_path=args.db,
            )
            print("✅ Updated:")
            _print_task(task, get_task_tags(task.id, args.db))
            return 0

        if args.cmd == "done":
            task = update_task(task_id=args.id, status="done", db_path=args.db)
            print("✅ Done:")
            _print_task(task, get_task_tags(task.id, args.db))
            return 0

        if args.cmd == "delete":
            delete_task(args.id, args.db)
            print("🗑️ Deleted.")
            return 0

        parser.print_help()
        return 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
