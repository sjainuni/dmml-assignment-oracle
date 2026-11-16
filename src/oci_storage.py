import os
from pathlib import Path

import oci
from dotenv import load_dotenv
from oci.object_storage import UploadManager

from src.common import ROOT, get_logger

log = get_logger("oci")


def client():
    load_dotenv(ROOT / ".env")

    cfg = os.path.expanduser(
        os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
    )
    profile = os.getenv("OCI_PROFILE", "SESSION_TEST")

    config = oci.config.from_file(
        file_location=cfg,
        profile_name=profile
    )

    # Read browser-session token and its signing key
    token_file = os.path.expanduser(config["security_token_file"])
    with open(token_file, "r") as f:
        token = f.read().strip()

    private_key = oci.signer.load_private_key_from_file(
        os.path.expanduser(config["key_file"])
    )

    signer = oci.auth.signers.SecurityTokenSigner(
        token, private_key
    )

    config["region"] = os.getenv(
        "OCI_REGION", "ap-mumbai-1"
    )

    return oci.object_storage.ObjectStorageClient(
        config, signer=signer
    )


def upload_file(path, object_key):
    load_dotenv(ROOT / ".env")

    ns = os.environ["OCI_NAMESPACE"]
    bucket = os.environ["OCI_BUCKET"]

    c = client()
    manager = UploadManager(
        c,
        allow_multipart_uploads=True,
        allow_parallel_uploads=True
    )

    manager.upload_file(
        ns, bucket, object_key, str(path)
    )

    log.info(
        "OCI upload succeeded: oci://%s/%s/%s",
        bucket, object_key
    )
    return object_key


def upload_tree(local_dir, prefix):
    root = Path(local_dir)
    results = []

    for p in root.rglob("*"):
        if p.is_file():
            relative_path = p.relative_to(root).as_posix()
            object_key = f"{prefix.strip('/')}/{relative_path}"
            results.append(upload_file(p, object_key))

    return results
