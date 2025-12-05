# dashboard.py
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def plot_completion_trend(tasks):
    # tasks: list of dicts (from db.list_tasks)
    df = pd.DataFrame(tasks)
    if df.empty or 'completed_at' not in df.columns:
        fig = plt.figure()
        plt.text(0.5,0.5,'No data', ha='center')
        return fig
    df['completed_at'] = pd.to_datetime(df['completed_at'])
    df = df.dropna(subset=['completed_at'])
    if df.empty:
        fig = plt.figure()
        plt.text(0.5,0.5,'No completions yet', ha='center')
        return fig
    df['date'] = df['completed_at'].dt.date
    series = df.groupby('date').size()
    fig = plt.figure()
    series.plot(kind='bar')
    plt.title("Tasks completed (by day)")
    plt.xlabel("Date")
    plt.ylabel("Completed tasks")
    plt.tight_layout()
    return fig

def plot_priority_distribution(tasks):
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.DataFrame(tasks)
    if df.empty:
        fig = plt.figure()
        plt.text(0.5,0.5,'No tasks', ha='center')
        return fig
    fig = plt.figure()
    df['priority'].value_counts().sort_index().plot(kind='bar')
    plt.title("Tasks by priority")
    plt.xlabel("Priority (1 = highest)")
    plt.ylabel("Count")
    plt.tight_layout()
    return fig
