# nlp_utils.py
import dateparser
import re
from typing import Tuple, List, Optional
from datetime import datetime

PRIORITY_KEYWORDS = {
    'urgent': 1,
    'asap': 1,
    'important': 2,
    'high': 2,
    'medium': 3,
    'low': 4,
    'later': 4
}

def parse_task_text(text: str) -> Tuple[str, Optional[str], int, List[dict]]:
    """
    Returns: (title, deadline_iso_or_None, priority (1-4), subtasks)
    """
    text = text.strip()
    # 1) Extract deadline using dateparser (looks for phrases like "by Monday", "on 10 Aug", "tomorrow")
    date_settings = {'PREFER_DATES_FROM': 'future'}
    dt = dateparser.search.search_dates(text, settings=date_settings) if hasattr(dateparser, 'search') else None

    deadline_iso = None
    if dt:
        # dt is list of tuples (matched_text, datetime)
        # choose earliest matched datetime
        try:
            first = dt[0][1]
            deadline_iso = first.isoformat()
        except Exception:
            deadline_iso = None

    # 2) Priority: look for explicit keywords
    priority = 3
    for k, v in PRIORITY_KEYWORDS.items():
        if re.search(r'\b' + re.escape(k) + r'\b', text, flags=re.IGNORECASE):
            priority = v
            break

    # 3) Simple heuristics: closer deadline -> higher priority
    if deadline_iso:
        try:
            d = dateparser.parse(deadline_iso)
            if d:
                days = (d - datetime.now()).days
                if days <= 0:
                    priority = min(priority, 1)
                elif days <= 2:
                    priority = min(priority, 1)
                elif days <= 7:
                    priority = min(priority, 2)
        except Exception:
            pass

    # 4) Subtask detection: split by commas, 'then', '->', ';', 'and'
    subtasks = []
    # If "break into" or "steps" phrase present, make subtasks
    if re.search(r'\b(break|steps|step|then|subtasks)\b', text, flags=re.IGNORECASE):
        parts = re.split(r',|\band\b|then|->|;|\n', text)
        # keep short fragments as subtasks if longer than 5 chars
        for p in parts:
            p = p.strip()
            if len(p) > 5 and len(p.split()) <= 12:
                subtasks.append({'title': p, 'done': False})

    # 5) Title: use text without deadline phrase and priority words (naive)
    title = text
    # remove phrases like 'by Monday' using regex that matches common date words
    title = re.sub(r'\bby\s+\w+\b', '', title, flags=re.IGNORECASE)
    # remove explicit priority words
    for k in PRIORITY_KEYWORDS.keys():
        title = re.sub(r'\b' + re.escape(k) + r'\b', '', title, flags=re.IGNORECASE)
    title = re.sub(r'\s+', ' ', title).strip()
    if len(title) > 200:
        title = title[:197] + '...'
    return title or text, deadline_iso, priority, subtasks
