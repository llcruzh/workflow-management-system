from workflow_cli.db import init_db
from workflow_cli.services import create_task, list_tasks, update_task, delete_task

def test_crud(tmp_path):
    db = tmp_path / "test.db"
    init_db(str(db))

    t = create_task("Test", "Hello", priority=5, tags=["unit"], db_path=str(db))
    assert t.title == "Test"

    tasks = list_tasks(db_path=str(db))
    assert len(tasks) == 1

    t2 = update_task(t.id, status="done", db_path=str(db))
    assert t2.status == "done"

    delete_task(t.id, db_path=str(db))
    assert list_tasks(db_path=str(db)) == []
