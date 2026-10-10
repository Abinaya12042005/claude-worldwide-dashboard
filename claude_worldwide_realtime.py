# claude_worldwide_realtime.py
# Run this in terminal / Colab — generates live-updating CSV
# Power BI reads this CSV every 1 minute via "Scheduled Refresh"

import pandas as pd
import numpy as np
import time
import os
from datetime import datetime, timedelta
import random

# ── CONFIG ──────────────────────────────────────────────
OUTPUT_PATH = "claude_live_data.csv"   # Power BI will connect to this file
REFRESH_EVERY = 60                     # seconds between updates
TOTAL_ROWS = 500                       # rows in dataset (sliding window)

# ── SEED DATA ────────────────────────────────────────────
REGIONS = {
    "North America": {"countries": ["USA","Canada","Mexico"],         "base_users": 71060000},
    "Europe":        {"countries": ["UK","Germany","France","Spain"], "base_users": 50490000},
    "Asia Pacific":  {"countries": ["India","Japan","Australia","Singapore","South Korea"], "base_users": 39270000},
    "Latin America": {"countries": ["Brazil","Argentina","Colombia"], "base_users": 14960000},
    "ME & Africa":   {"countries": ["UAE","South Africa","Nigeria"],  "base_users": 11220000},
}

PLATFORMS   = ["Web", "API", "Mobile", "Desktop"]
PLAT_WEIGHT = [0.41, 0.29, 0.19, 0.11]

USE_CASES   = ["Coding & Dev", "Writing & Content", "Data Analysis", "Education", "Customer Support", "Other"]
UC_WEIGHT   = [0.34, 0.22, 0.18, 0.14, 0.08, 0.04]

PLANS       = ["Free", "Pro", "Team/Enterprise"]
PLAN_WEIGHT = [0.52, 0.31, 0.17]

# ── GENERATE ONE BATCH OF ROWS ────────────────────────────
def generate_batch(n=50):
    rows = []
    now = datetime.utcnow()

    for _ in range(n):
        region = random.choices(list(REGIONS.keys()), weights=[38,27,21,8,6])[0]
        country = random.choice(REGIONS[region]["countries"])
        base = REGIONS[region]["base_users"]

        # simulate realistic jitter
        active_users   = int(base * random.uniform(0.98, 1.02))
        messages_pm    = int(random.uniform(1_300_000, 1_800_000))
        session_min    = round(random.uniform(15, 22), 1)
        avg_revenue    = round(random.uniform(28_000, 32_000), 0)
        platform       = random.choices(PLATFORMS, PLAT_WEIGHT)[0]
        use_case       = random.choices(USE_CASES, UC_WEIGHT)[0]
        plan           = random.choices(PLANS, PLAN_WEIGHT)[0]
        hour_utc       = random.randint(0, 23)
        day_of_week    = random.choice(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
        satisfaction   = round(random.uniform(4.1, 4.9), 2)
        tokens_used    = random.randint(500, 8000)
        is_mobile      = 1 if platform == "Mobile" else 0
        timestamp      = now - timedelta(seconds=random.randint(0, 3600))

        rows.append({
            "Timestamp":        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Region":           region,
            "Country":          country,
            "Platform":         platform,
            "Use_Case":         use_case,
            "Plan":             plan,
            "Active_Users":     active_users,
            "Messages_Per_Min": messages_pm,
            "Session_Min":      session_min,
            "Avg_Revenue_USD":  avg_revenue,
            "Tokens_Used":      tokens_used,
            "Satisfaction":     satisfaction,
            "Hour_UTC":         hour_utc,
            "Day_Of_Week":      day_of_week,
            "Is_Mobile":        is_mobile,
        })
    return pd.DataFrame(rows)

# ── LIVE UPDATE LOOP ──────────────────────────────────────
def run_live():
    print(f"[START] Writing live data to: {OUTPUT_PATH}")
    print(f"        Refreshing every {REFRESH_EVERY}s | Ctrl+C to stop\n")

    all_data = generate_batch(TOTAL_ROWS)       # initial full load
    all_data.to_csv(OUTPUT_PATH, index=False)
    print(f"[INIT]  {len(all_data)} rows written at {datetime.utcnow()}")

    while True:
        time.sleep(REFRESH_EVERY)

        new_rows = generate_batch(50)            # 50 fresh rows each tick
        all_data = pd.concat([all_data, new_rows], ignore_index=True)
        all_data = all_data.tail(TOTAL_ROWS)     # keep sliding window of 500 rows
        all_data.to_csv(OUTPUT_PATH, index=False)

        ts = datetime.utcnow().strftime("%H:%M:%S")
        print(f"[TICK]  {ts} — {len(all_data)} rows | "
              f"Active users (last): {all_data['Active_Users'].iloc[-1]:,} | "
              f"Msgs/min: {all_data['Messages_Per_Min'].iloc[-1]:,}")

if __name__ == "__main__":
    run_live()
