-- Logical warehouse schema for curated recommendation data.
CREATE TABLE dim_item (
  itemid BIGINT PRIMARY KEY,
  categoryid BIGINT,
  available BOOLEAN,
  valid_from TIMESTAMP,
  valid_to TIMESTAMP,
  source_version VARCHAR(64)
);
CREATE TABLE fact_interaction (
  visitorid BIGINT NOT NULL,
  itemid BIGINT NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  event_type VARCHAR(20) NOT NULL,
  event_weight DOUBLE PRECISION NOT NULL,
  transactionid BIGINT,
  ingestion_date DATE NOT NULL,
  data_version VARCHAR(64) NOT NULL
);
CREATE TABLE feature_user (
  visitorid BIGINT NOT NULL,
  user_event_count BIGINT,
  user_unique_items BIGINT,
  user_mean_event_weight DOUBLE PRECISION,
  feature_version VARCHAR(32) NOT NULL,
  computed_at TIMESTAMP NOT NULL,
  PRIMARY KEY(visitorid, feature_version)
);
CREATE TABLE feature_item (
  itemid BIGINT NOT NULL,
  item_event_count BIGINT,
  item_unique_visitors BIGINT,
  item_mean_event_weight DOUBLE PRECISION,
  feature_version VARCHAR(32) NOT NULL,
  computed_at TIMESTAMP NOT NULL,
  PRIMARY KEY(itemid, feature_version)
);
CREATE TABLE model_run (
  run_id VARCHAR(128) PRIMARY KEY,
  algorithm VARCHAR(64),
  dataset_version VARCHAR(64),
  parameters_json TEXT,
  metrics_json TEXT,
  created_at TIMESTAMP
);
