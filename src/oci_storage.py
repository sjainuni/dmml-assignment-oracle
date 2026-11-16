import os
from pathlib import Path
from dotenv import load_dotenv
import oci
from oci.object_storage import UploadManager
from src.common import ROOT, get_logger
log=get_logger("oci")
def client():
    load_dotenv(ROOT/".env")
    cfg=os.path.expanduser(os.getenv("OCI_CONFIG_FILE","~/.oci/config"))
    profile=os.getenv("OCI_PROFILE","DEFAULT")
    config=oci.config.from_file(cfg,profile)
    region=os.getenv("OCI_REGION","ap-mumbai-1")
    config["region"]=region
    return oci.object_storage.ObjectStorageClient(config)
def upload_file(path, prefix):
    load_dotenv(ROOT/".env")
    ns=os.environ["OCI_NAMESPACE"]; bucket=os.environ["OCI_BUCKET"]
    c=client(); manager=UploadManager(c,allow_multipart_uploads=True,allow_parallel_uploads=True)
    key=f"{prefix.strip('/')}/{path.name}"
    manager.upload_file(ns,bucket,key,str(path))
    log.info("OCI upload succeeded: oci://%s/%s/%s",bucket,key)
    return key
def upload_tree(local_dir, prefix):
    root=Path(local_dir)
    results=[]
    for p in root.rglob("*"):
        if p.is_file(): results.append(upload_file(p,prefix+"/"+str(p.parent.relative_to(root))))
    return results
