# db.py
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        deadline TEXT,
        priority INTEGER,
        status TEXT,
        created_at TEXT,
        completed_at TEXT,
        subtasks TEXT
    )
    ''')
    conn.commit()
    conn.close()

def add_task(title: str, description: str='', deadline: Optional[str]=None,
             priority: int=3, subtasks: Optional[List[Dict]]=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    subtasks_json = json.dumps(subtasks or [])
    cur.execute('''
        INSERT INTO tasks (title, description, deadline, priority, status, created_at, subtasks)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, deadline, priority, 'pending', now, subtasks_json))
    conn.commit()
    conn.close()

def list_tasks(status: Optional[str]=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if status:
        cur.execute('SELECT * FROM tasks WHERE status = ? ORDER BY priority ASC, deadline ASC', (status,))
    else:
        cur.execute('SELECT * FROM tasks ORDER BY priority ASC, deadline ASC')
    rows = cur.fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

def mark_complete(task_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute('UPDATE tasks SET status=?, completed_at=? WHERE id=?', ('completed', now, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id=?', (task_id,))
    conn.commit()
    conn.close()

def get_task(task_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE id=?', (task_id,))
    row = cur.fetchone()
    conn.close()
    return _row_to_dict(row) if row else None

def _row_to_dict(row):
    if not row:
        return None
    id, title, description, deadline, priority, status, created_at, completed_at, subtasks = row
    return {
        'id': id,
        'title': title,
        'description': description,
        'deadline': deadline,
        'priority': priority,
        'status': status,
        'created_at': created_at,
        'completed_at': completed_at,
        'subtasks': json.loads(subtasks or '[]')
    }
