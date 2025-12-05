# sample_data.py
from db import init_db, add_task
from datetime import datetime, timedelta

def seed():
    init_db()
    add_task("Finish math assignment", "Finish questions 1-10", (datetime.utcnow()+timedelta(days=2)).isoformat(), 1)
    add_task("Read research paper on AI", "Read and summarize", (datetime.utcnow()+timedelta(days=7)).isoformat(), 3)
    add_task("Grocery shopping", "Buy fruits and milk", None, 4)

if __name__ == "__main__":
    seed()
    print("Seeded sample tasks.")
