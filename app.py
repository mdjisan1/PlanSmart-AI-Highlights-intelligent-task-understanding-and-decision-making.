# app.py
import streamlit as st
from db import init_db, add_task, list_tasks, mark_complete, delete_task, get_task
from nlp_utils import parse_task_text
from ai_utils import suggest_priority, record_task_completion, get_productivity_profile
from dashboard import plot_completion_trend, plot_priority_distribution
import pandas as pd

st.set_page_config(page_title="Smart Task Manager", layout="wide")
st.title("Smart Task Manager — Prototype")

# initialize DB
init_db()

# Sidebar: Add new task
st.sidebar.header("Add a new task")
raw = st.sidebar.text_area("Write task in plain English", height=120, placeholder='e.g. "Finish assignment by Monday evening, urgent"')
if st.sidebar.button("Parse & Add"):
    if not raw.strip():
        st.sidebar.error("Please enter a task.")
    else:
        title, deadline_iso, parsed_priority, subtasks = parse_task_text(raw)
        final_priority = suggest_priority(raw, parsed_priority, deadline_iso)
        add_task(title=title, description=raw, deadline=deadline_iso, priority=final_priority, subtasks=subtasks)
        st.sidebar.success(f"Task added: {title}")

# Main view: Pending tasks
st.header("Pending Tasks")
tasks = list_tasks(status='pending')
if not tasks:
    st.info("No pending tasks. Add one from the sidebar.")
else:
    for t in tasks:
        col1, col2, col3 = st.columns([6,2,2])
        with col1:
            st.markdown(f"**[{t['id']}] {t['title']}**")
            if t['description']:
                st.write(t['description'])
            if t['subtasks']:
                st.write("Subtasks:")
                for s in t['subtasks']:
                    st.write(f" - {s.get('title')}")
        with col2:
            st.write(f"**Priority:** {t['priority']}")
            st.write(f"**Deadline:** {t['deadline'] or '—'}")
        with col3:
            if st.button(f"Complete {t['id']}", key=f"complete_{t['id']}"):
                mark_complete(t['id'])
                # reflect in stats
                updated = get_task(t['id'])
                record_task_completion(updated)
                st.experimental_rerun()
            if st.button(f"Delete {t['id']}", key=f"delete_{t['id']}"):
                delete_task(t['id'])
                st.experimental_rerun()

# Completed tasks panel
st.header("Completed Tasks")
completed = list_tasks(status='completed')
if completed:
    dfc = pd.DataFrame(completed)
    st.dataframe(dfc[['id','title','completed_at','priority']])
else:
    st.write("No completed tasks yet.")

# Dashboard section
st.header("Dashboard")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Completion Trend")
    fig = plot_completion_trend(list_tasks(status='completed'))
    st.pyplot(fig)
with col2:
    st.subheader("Priority Distribution")
    fig2 = plot_priority_distribution(list_tasks())
    st.pyplot(fig2)

# Productivity suggestion
suggested_hour = get_productivity_profile()
st.sidebar.subheader("Smart Suggestion")
if suggested_hour is not None:
    st.sidebar.write(f"You are most productive around **{suggested_hour}:00** (UTC). Try scheduling deep tasks then.")
else:
    st.sidebar.write("No productivity data yet — it will appear after you complete some tasks.")

st.sidebar.markdown("---")
st.sidebar.write("Prototype: simple, explainable heuristics. Extend with ML models later.")
