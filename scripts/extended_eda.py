import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIG = REPORTS / "figures"
FIG.mkdir(parents=True, exist_ok=True)

df = pd.read_parquet(ROOT / "data/processed/events_prepared.parquet")

# Event percentages
events = df["event"].value_counts()
percentages = events / events.sum() * 100

# Temporal patterns
hourly = df.groupby(df["event_datetime"].dt.hour).size()
daily = df.groupby(df["event_datetime"].dt.day_name()).size()
daily = daily.reindex(["Monday", "Tuesday", "Wednesday", "Thursday",
                       "Friday", "Saturday", "Sunday"])

# User and item activity
users = df.groupby("visitorid").size()
items = df.groupby("itemid").size()

# Event percentage chart
ax = percentages.plot(kind="bar", figsize=(8, 5))
ax.set_title("Event Type Distribution (%)")
ax.set_ylabel("Percentage of events")
plt.tight_layout()
plt.savefig(FIG / "event_percentage.png", dpi=160)
plt.close()

# Hourly activity
ax = hourly.plot(kind="line", marker="o", figsize=(9, 5))
ax.set_title("Interaction Activity by Hour (UTC)")
ax.set_xlabel("Hour")
ax.set_ylabel("Number of events")
plt.tight_layout()
plt.savefig(FIG / "hourly_activity.png", dpi=160)
plt.close()

# Weekly activity
ax = daily.plot(kind="bar", figsize=(9, 5))
ax.set_title("Interaction Activity by Day of Week (UTC)")
ax.set_ylabel("Number of events")
plt.tight_layout()
plt.savefig(FIG / "weekday_activity.png", dpi=160)
plt.close()

# User activity distribution
plt.figure(figsize=(8, 5))
plt.hist(users.clip(upper=users.quantile(.99)), bins=50)
plt.title("User Activity Distribution (99th percentile clipped)")
plt.xlabel("Events per user")
plt.ylabel("Number of users")
plt.tight_layout()
plt.savefig(FIG / "user_activity_detailed.png", dpi=160)
plt.close()

# Item popularity distribution
plt.figure(figsize=(8, 5))
plt.hist(items.clip(upper=items.quantile(.99)), bins=50)
plt.title("Item Popularity Distribution (99th percentile clipped)")
plt.xlabel("Interactions per item")
plt.ylabel("Number of items")
plt.tight_layout()
plt.savefig(FIG / "item_activity_distribution.png", dpi=160)
plt.close()

summary = {
    "prepared_events": int(len(df)),
    "unique_visitors": int(df.visitorid.nunique()),
    "unique_items": int(df.itemid.nunique()),
    "event_counts": {str(k): int(v) for k, v in events.items()},
    "event_percentages": {str(k): round(float(v), 4) for k, v in percentages.items()},
    "hourly_activity": {str(k): int(v) for k, v in hourly.items()},
    "weekday_activity": {str(k): int(v) for k, v in daily.dropna().items()},
    "user_activity_quantiles": {str(k): float(v) for k, v in users.quantile([.25,.5,.75,.9,.99]).items()},
    "item_activity_quantiles": {str(k): float(v) for k, v in items.quantile([.25,.5,.75,.9,.99]).items()},
    "top_10_items": {str(k): int(v) for k, v in items.nlargest(10).items()},
}
(REPORTS / "extended_eda_summary.json").write_text(json.dumps(summary, indent=2))

report = f"""# Retailrocket Exploratory Data Analysis

## 1. Dataset overview

The prepared dataset contains **{len(df):,} events**, **{df.visitorid.nunique():,} visitors** and **{df.itemid.nunique():,} items**.

## 2. Event type distribution

**What was applied:** Frequency counts and percentage calculation by event type.

**Why:** To understand the balance between browsing, cart activity and purchases. Different events represent different levels of user intent.

| Event | Count | Percentage |
|---|---:|---:|
"""
for event, count in events.items():
    report += f"| {event} | {count:,} | {percentages[event]:.2f}% |\n"

report += """
![Event distribution](figures/event_percentage.png)

**Interpretation:** Views, add-to-cart events and transactions have different frequencies. This supports treating the data as implicit feedback rather than explicit star ratings. The configured weights (view=1, addtocart=3, transaction=5) are modelling assumptions.

## 3. Temporal analysis

**What was applied:** Events were grouped by UTC hour and weekday.

**Why:** To identify time-based activity patterns that may inform future time-aware recommendations.

![Hourly activity](figures/hourly_activity.png)

![Weekday activity](figures/weekday_activity.png)

**Interpretation:** Use the charts to identify peak periods. These timestamps are UTC; they have not been converted to local time.

## 4. User activity distribution

**What was applied:** Counted events per visitor and plotted a histogram, clipping the displayed distribution at the 99th percentile.

**Why:** To inspect whether interactions are evenly distributed or concentrated among a small group of visitors.

![User activity](figures/user_activity_detailed.png)

**Interpretation:** A skewed distribution indicates that users have different levels of activity. This is relevant to cold-start and popularity-bias considerations.

## 5. Item popularity distribution

**What was applied:** Counted interactions per item and plotted a histogram, clipping the display at the 99th percentile.

**Why:** To investigate whether a small number of products account for a large share of interactions.

![Item activity](figures/item_activity_distribution.png)

**Interpretation:** A long-tailed distribution would indicate that many items receive relatively few interactions. This affects recommendation coverage.

## 6. User-item matrix sparsity

The initial profiling measured matrix sparsity at **99.99935%**.

**Why:** Sparsity measures how few possible visitor-item combinations have observed interactions.

**Interpretation:** The interaction matrix is extremely sparse. Collaborative filtering therefore has limited evidence for many user-item combinations. This is a key modelling challenge.

## 7. Data-quality findings

The raw event file contained 2,756,101 rows. Validation found 460 duplicate rows, no missing visitor IDs, no missing item IDs, no invalid timestamps and no unknown event types. The validation status was PASS.

## 8. EDA decisions

1. Retain the three event types as implicit feedback.
2. Use documented event weights as modelling assumptions, not ratings.
3. Preserve timestamps for temporal feature engineering.
4. Consider cold-start and long-tail effects when interpreting recommendation performance.
5. Report the high matrix sparsity as a limitation of collaborative filtering.

## 9. Limitations

This analysis describes the available historical Retailrocket snapshot. It does not establish live customer behaviour or causal effects. UTC is used for temporal grouping. The event-weight values are assumptions and should be tested in future experiments.
"""
(REPORTS / "EDA_REPORT.md").write_text(report)

print("Extended EDA completed.")
print(json.dumps(summary, indent=2))
print("Report:", REPORTS / "EDA_REPORT.md")
