import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/events_prepared.parquet"
OUT = ROOT / "reports/figures"
OUT.mkdir(parents=True, exist_ok=True)

print("Reading prepared Retailrocket data...")
df = pd.read_parquet(DATA, columns=[
    "visitorid", "itemid", "event", "event_datetime"
])

def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("Created:", name)

# 1. Event distribution
counts = df["event"].value_counts()
fig, ax = plt.subplots(figsize=(8, 5))
counts.plot(kind="bar", ax=ax)
ax.set_title("Retailrocket Event Distribution")
ax.set_xlabel("Event Type")
ax.set_ylabel("Number of Events")
ax.tick_params(axis="x", rotation=0)
save(fig, "event_distribution.png")

# 2. Event percentage
fig, ax = plt.subplots(figsize=(7, 5))
counts.plot(kind="pie", autopct="%1.1f%%", ax=ax, startangle=90)
ax.set_title("Share of Event Types")
ax.set_ylabel("")
save(fig, "event_percentage.png")

# 3. User activity distribution
user_counts = df.groupby("visitorid").size()
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(user_counts.clip(upper=user_counts.quantile(.99)), bins=40)
ax.set_title("User Activity Distribution (99th Percentile Clipped)")
ax.set_xlabel("Events per Visitor")
ax.set_ylabel("Number of Visitors")
save(fig, "user_activity.png")

# 4. Detailed user activity (log scale)
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(user_counts, bins=60, log=True)
ax.set_title("Detailed User Activity Distribution")
ax.set_xlabel("Events per Visitor")
ax.set_ylabel("Number of Visitors (log scale)")
save(fig, "user_activity_detailed.png")

# 5. Item activity distribution
item_counts = df.groupby("itemid").size()
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(item_counts, bins=60, log=True)
ax.set_title("Item Interaction Distribution")
ax.set_xlabel("Interactions per Item")
ax.set_ylabel("Number of Items (log scale)")
save(fig, "item_activity_distribution.png")

# 6. Top 20 popular items
popular = item_counts.nlargest(20).sort_values()
fig, ax = plt.subplots(figsize=(10, 7))
popular.plot(kind="barh", ax=ax)
ax.set_title("Top 20 Items by Interaction Count")
ax.set_xlabel("Number of Interactions")
ax.set_ylabel("Item ID")
save(fig, "item_popularity_top20.png")

# 7. Hourly activity (timestamps are UTC)
hourly = df["event_datetime"].dt.hour.value_counts().sort_index()
fig, ax = plt.subplots(figsize=(9, 5))
hourly.reindex(range(24), fill_value=0).plot(kind="bar", ax=ax)
ax.set_title("Hourly User Activity (UTC)")
ax.set_xlabel("Hour of Day (UTC)")
ax.set_ylabel("Number of Events")
save(fig, "hourly_activity.png")

# 8. Weekday activity (Monday = 0)
weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
weekday = df["event_datetime"].dt.dayofweek.value_counts().sort_index()
fig, ax = plt.subplots(figsize=(9, 5))
weekday.reindex(range(7), fill_value=0).plot(kind="bar", ax=ax)
ax.set_title("Activity by Weekday (UTC)")
ax.set_xlabel("Day of Week")
ax.set_ylabel("Number of Events")
ax.set_xticklabels(weekday_names, rotation=30, ha="right")
save(fig, "weekday_activity.png")

print("\nAll EDA plots generated successfully.")
print("Output directory:", OUT)
