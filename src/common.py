from pathlib import Path
import logging, json, hashlib, os
ROOT = Path(__file__).resolve().parents[1]
def get_logger(name="recomart"):
    (ROOT/"logs").mkdir(exist_ok=True)
    logger=logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        fmt=logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        fh=logging.FileHandler(ROOT/"logs"/"pipeline.log"); fh.setFormatter(fmt)
        sh=logging.StreamHandler(); sh.setFormatter(fmt)
        logger.addHandler(fh); logger.addHandler(sh)
    return logger
def load_config():
    return json.loads((ROOT/"config.json").read_text())
def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
