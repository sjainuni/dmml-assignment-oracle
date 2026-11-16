import json
import joblib
import mlflow
import numpy as np
import pandas as pd

from scipy.sparse import coo_matrix
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import mean_squared_error

from src.common import ROOT, load_config, get_logger

log = get_logger("train")


def train(ui):
    cfg = load_config()["training"]
    ui = ui.sort_values("last_event")

    counts = ui.groupby("visitorid").itemid.nunique()
    eligible = counts[counts >= 2].index

    test = ui[ui.visitorid.isin(eligible)].groupby("visitorid").tail(1)
    train_df = ui.drop(test.index)

    if len(train_df) > cfg["max_interactions"]:
        train_df = train_df.sample(
            cfg["max_interactions"],
            random_state=cfg["random_state"]
        )

    users = sorted(train_df.visitorid.unique())
    items = sorted(train_df.itemid.unique())

    uidx = {v: i for i, v in enumerate(users)}
    iidx = {v: i for i, v in enumerate(items)}

    tr = train_df[
        train_df.visitorid.isin(users) &
        train_df.itemid.isin(items)
    ]

    mat = coo_matrix(
        (
            np.log1p(tr.affinity),
            (tr.visitorid.map(uidx), tr.itemid.map(iidx))
        ),
        shape=(len(users), len(items))
    ).tocsr()

    k = max(2, min(cfg["svd_components"], min(mat.shape) - 1))

    model = TruncatedSVD(
        n_components=k,
        random_state=cfg["random_state"]
    )

    latent = model.fit_transform(mat)

    # Calculate reconstruction RMSE in batches to avoid excessive RAM usage.
    squared_error = 0.0
    total_values = 0

    for start in range(0, mat.shape[0], 256):
        end = min(start + 256, mat.shape[0])

        reconstructed_batch = (
            latent[start:end] @ model.components_
        )

        actual_batch = mat[start:end].toarray()

        squared_error += np.sum(
            (actual_batch - reconstructed_batch) ** 2
        )
        total_values += actual_batch.size

        del reconstructed_batch, actual_batch

    rmse = float(np.sqrt(squared_error / total_values))

    # Ranking evaluation
    precisions = []
    recalls = []
    ndcgs = []

    for _, row in test.iterrows():
        u = uidx.get(row.visitorid)
        target = iidx.get(row.itemid)

        if u is None or target is None:
            continue

        scores = latent[u] @ model.components_
        seen = mat[u].indices
        scores[seen] = -np.inf

        top = np.argsort(scores)[-cfg["top_k"]:][::-1]
        hit = int(target in top)

        precisions.append(hit / cfg["top_k"])
        recalls.append(float(hit))

        if hit:
            rank = int(np.where(top == target)[0][0]) + 1
            ndcgs.append(1 / np.log2(rank + 1))
        else:
            ndcgs.append(0.0)

    metrics = {
        "rmse_reconstruction_full_matrix": rmse,
        "precision_at_10": float(np.mean(precisions)) if precisions else 0.0,
        "recall_at_10": float(np.mean(recalls)) if recalls else 0.0,
        "ndcg_at_10": float(np.mean(ndcgs)) if ndcgs else 0.0,
        "train_interactions": int(mat.nnz),
        "test_candidates_evaluated": len(precisions),
        "users": len(users),
        "items": len(items),
        "components": k
    }

    (ROOT / "models").mkdir(exist_ok=True)
    (ROOT / "reports").mkdir(exist_ok=True)

    artifact = {
        "model": model,
        "users": uidx,
        "items": iidx,
        "matrix": mat
    }

    joblib.dump(artifact, ROOT / "models" / "recommender_svd.joblib")

    metrics_path = ROOT / "reports" / "model_metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))

    mlflow.set_tracking_uri(f"sqlite:///{ROOT / 'mlflow.db'}")

    with mlflow.start_run(run_name="retailrocket-truncated-svd") as run:
        mlflow.log_params({
            "algorithm": "TruncatedSVD",
            "components": k,
            "max_interactions": cfg["max_interactions"],
            "event_weights": "view=1,addtocart=3,transaction=5"
        })

        mlflow.log_metrics({
            key: value for key, value in metrics.items()
            if isinstance(value, (int, float))
        })

        mlflow.log_artifact(str(metrics_path))
        metrics["mlflow_run_id"] = run.info.run_id

    metrics_path.write_text(json.dumps(metrics, indent=2))

    log.info("Model training complete: %s", metrics)

    return metrics
