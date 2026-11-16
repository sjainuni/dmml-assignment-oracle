# EDA Methodology and Rationale

## 1. Dataset structure
**Applied:** Inspected the prepared dataset dimensions and unique users and items.

**Why:** To understand the scale of the recommendation problem and establish the baseline for subsequent analysis.

**Finding:** 2,755,651 prepared events, 1,407,580 unique visitors and 235,061 unique items.

## 2. Event distribution
**Applied:** Frequency counts and percentage distribution for view, addtocart and transaction events.

**Why:** To understand the relative frequency and intent represented by each interaction type.

**Finding:**
- View: 2,664,219 (96.682%)
- Add to cart: 68,975 (2.503%)
- Transaction: 22,457 (0.815%)

**Decision:** Treat the dataset as implicit feedback. Event weights of 1, 3 and 5 are modelling assumptions, not explicit ratings.

## 3. Missing values and duplicates
**Applied:** Checked missing visitor IDs, item IDs, invalid timestamps, unknown event types and duplicate rows.

**Why:** Missing identifiers or invalid timestamps can make interactions unusable. Duplicate records can distort interaction counts.

**Finding:** No missing visitor IDs, missing item IDs, invalid timestamps or unknown event types. There were 460 duplicate raw rows.

**Decision:** The preparation process removes invalid records and exact duplicate rows. The raw data is retained unchanged.

## 4. Temporal analysis
**Applied:** Grouped events by UTC hour and weekday.

**Why:** To identify temporal activity patterns that may inform future time-aware recommendation features.

**Finding:** The highest hourly activity occurred at 20:00 UTC with 187,894 events. Tuesday had the highest weekday count (447,011), while Saturday had the lowest (305,167).

**Decision:** Preserve timestamps and temporal attributes for possible future modelling. These are UTC observations, not local-time conclusions.

## 5. User activity distribution
**Applied:** Counted interactions per visitor and calculated the 25th, 50th, 75th, 90th and 99th percentiles.

**Why:** To understand how much interaction history is available for each visitor.

**Finding:** Median activity was 1 event; the 75th percentile was 2, and the 99th percentile was 13.

**Decision:** The limited interaction history creates a cold-start and sparse-history challenge.

## 6. Item popularity distribution
**Applied:** Counted interactions per item and examined activity percentiles and top items.

**Why:** To identify popular products and investigate long-tail behaviour.

**Finding:** Median item activity was 3 events; the 99th percentile was 143 events. The most interacted-with item was 187946, with 3,412 events.

**Decision:** Consider popularity bias and long-tail coverage when evaluating recommendations.

## 7. User-item matrix sparsity
**Applied:** Calculated unique observed user-item pairs divided by all possible visitor-item combinations.

**Formula:**

Density = Observed user-item pairs / (Unique visitors × Unique items)

Sparsity = 1 − Density

**Why:** To quantify the lack of observed interactions in the recommendation matrix.

**Finding:** Sparsity was approximately 99.99935%.

**Decision:** Collaborative filtering is challenged by extreme sparsity. Future experiments should investigate hybrid and content-based approaches.

## 8. EDA limitations
- The dataset represents a historical snapshot, not live customer activity.
- Temporal analysis uses UTC.
- Event weights are assumptions and require experimentation.
- Observational patterns do not establish causal relationships.
- Popularity and activity statistics do not establish recommendation quality.
