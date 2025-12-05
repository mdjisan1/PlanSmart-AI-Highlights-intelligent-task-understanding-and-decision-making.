# ai_utils.py
from datetime import datetime
import math
from tinydb import TinyDB, Query
import os

DB_FILE = "stats.json"
db = TinyDB(DB_FILE)

def suggest_priority(task_text: str, parsed_priority: int, deadline_iso: str):
    """
    Combine parsed priority and simple learned preference to return final suggested priority.
    Lower number = higher priority (1 highest)
    """
    user_pref = db.table('prefs').all()
    # simple learned bias: if user marks many early-deadline tasks complete as high, slightly boost
    bias = 0
    stats = db.table('stats')
    rec = stats.get(doc_id=1)
    if rec:
        bias = rec.get('priority_bias', 0)

    # base = parsed_priority
    final = parsed_priority + bias
    final = max(1, min(4, int(final)))
    return final

def record_task_completion(task):
    """
    Update lightweight stats when a task is completed to learn preferences.
    """
    stats = db.table('stats')
    rec = stats.get(doc_id=1)
    if not rec:
        stats.insert({'completed_count': 0, 'priority_bias': 0, 'hour_counts': {}})
        rec = stats.get(doc_id=1)
    # increment completed
    stats.update({'completed_count': rec['completed_count'] + 1}, doc_ids=[rec.doc_id])

    # update hour-of-day counts (UTC)
    try:
        completed_at = task.get('completed_at')
        h = datetime.fromisoformat(completed_at).hour if completed_at else datetime.utcnow().hour
    except Exception:
        h = datetime.utcnow().hour
    hc = rec.get('hour_counts', {})
    hc[str(h)] = hc.get(str(h), 0) + 1
    stats.update({'hour_counts': hc}, doc_ids=[rec.doc_id])

    # update priority_bias slightly toward user's behavior (if they often complete high priority tasks fast)
    pb = rec.get('priority_bias', 0)
    # simple rule: if completed task had low priority number (urgent), nudge bias negative
    if task.get('priority', 3) <= 2:
        pb = pb - 0.02
    else:
        pb = pb + 0.01
    pb = max(-1, min(1, pb))
    stats.update({'priority_bias': pb}, doc_ids=[rec.doc_id])

def get_productivity_profile():
    """
    Return the hour-of-day where the user is most productive (based on completions).
    """
    stats = db.table('stats')
    rec = stats.get(doc_id=1)
    if not rec:
        return None
    hc = rec.get('hour_counts', {})
    if not hc:
        return None
    # return hour with max count
    max_hour = max(hc.items(), key=lambda kv: kv[1])[0]
    return int(max_hour)
