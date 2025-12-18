from __future__ import annotations

from typing import Iterable, Optional

from .db import get_conn
from .models import Task
from .utils import normalize_priority, normalize_status, normalize_tags

def _row_to_task(row) -> Task:
    return Task(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        status=row["status"],
        priority=row["priority"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )

def create_task(
    title: str,
    description: str = "",
    status: str = "todo",
    priority: int | str = 3,
    tags: Iterable[str] = (),
    db_path: str | None = None,
) -> Task:
    title = (title or "").strip()
    if not title:
        raise ValueError("Title cannot be empty.")
    description = (description or "").strip()
    status = normalize_status(status)
    priority = normalize_priority(priority)
    tag_list = normalize_tags(tags)

    with get_conn(db_path) as conn:
        cur = conn.execute(
            "INSERT INTO tasks(title, description, status, priority) VALUES(?,?,?,?)",
            (title, description, status, priority),
        )
        task_id = int(cur.lastrowid)

        for tag in tag_list:
            conn.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
            tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()["id"]
            conn.execute("INSERT OR IGNORE INTO task_tags(task_id, tag_id) VALUES(?,?)", (task_id, tag_id))

        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_task(row)

def get_task(task_id: int, db_path: str | None = None) -> Optional[Task]:
    with get_conn(db_path) as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_task(row) if row else None

def list_tasks(
    status: str | None = None,
    q: str | None = None,
    tag: str | None = None,
    sort: str = "new",
    limit: int = 50,
    offset: int = 0,
    db_path: str | None = None,
) -> list[Task]:
    where = []
    params: list[object] = []

    if status:
        where.append("t.status = ?")
        params.append(normalize_status(status))

    if q:
        where.append("(t.title LIKE ? OR t.description LIKE ?)")
        like = f"%{q.strip()}%"
        params.extend([like, like])

    join_tag = ""
    if tag:
        join_tag = """
          JOIN task_tags tt ON tt.task_id = t.id
          JOIN tags g ON g.id = tt.tag_id
        """
        where.append("g.name = ?")
        params.append(tag.strip().lower())

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    order_sql = {
        "new": "t.created_at DESC",
        "old": "t.created_at ASC",
        "priority": "t.priority DESC, t.created_at DESC",
        "status": "t.status ASC, t.priority DESC, t.created_at DESC",
    }.get(sort, "t.created_at DESC")

    sql = f"""
      SELECT DISTINCT t.*
      FROM tasks t
      {join_tag}
      {where_sql}
      ORDER BY {order_sql}
      LIMIT ? OFFSET ?
    """

    params.extend([int(limit), int(offset)])

    with get_conn(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
        return [_row_to_task(r) for r in rows]

def update_task(
    task_id: int,
    title: str | None = None,
    description: str | None = None,
    status: str | None = None,
    priority: int | str | None = None,
    add_tags: Iterable[str] = (),
    remove_tags: Iterable[str] = (),
    db_path: str | None = None,
) -> Task:
    updates = []
    params: list[object] = []

    if title is not None:
        t = title.strip()
        if not t:
            raise ValueError("Title cannot be empty.")
        updates.append("title = ?")
        params.append(t)

    if description is not None:
        updates.append("description = ?")
        params.append(description.strip())

    if status is not None:
        updates.append("status = ?")
        params.append(normalize_status(status))

    if priority is not None:
        updates.append("priority = ?")
        params.append(normalize_priority(priority))

    updates.append("updated_at = datetime('now')")

    if len(updates) == 1:  # only updated_at
        raise ValueError("No fields provided to update.")

    with get_conn(db_path) as conn:
        exists = conn.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not exists:
            raise ValueError(f"Task {task_id} not found.")

        sql = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        params.append(task_id)
        conn.execute(sql, params)

        for tag in normalize_tags(add_tags):
            conn.execute("INSERT OR IGNORE INTO tags(name) VALUES(?)", (tag,))
            tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()["id"]
            conn.execute("INSERT OR IGNORE INTO task_tags(task_id, tag_id) VALUES(?,?)", (task_id, tag_id))

        for tag in normalize_tags(remove_tags):
            row = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,)).fetchone()
            if row:
                conn.execute("DELETE FROM task_tags WHERE task_id = ? AND tag_id = ?", (task_id, row["id"]))

        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _row_to_task(row)

def delete_task(task_id: int, db_path: str | None = None) -> None:
    with get_conn(db_path) as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cur.rowcount == 0:
            raise ValueError(f"Task {task_id} not found.")

def get_task_tags(task_id: int, db_path: str | None = None) -> list[str]:
    with get_conn(db_path) as conn:
        rows = conn.execute(
            """
            SELECT g.name
            FROM tags g
            JOIN task_tags tt ON tt.tag_id = g.id
            WHERE tt.task_id = ?
            ORDER BY g.name ASC
            """,
            (task_id,),
        ).fetchall()
        return [r["name"] for r in rows]
