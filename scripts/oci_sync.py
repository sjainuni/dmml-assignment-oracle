import sys
from pathlib import Path
from src.common import ROOT
from src.oci_storage import upload_tree
if len(sys.argv)!=2 or sys.argv[1]!="upload":
    raise SystemExit("Usage: python scripts/oci_sync.py upload")
for folder,prefix in [(ROOT/"data"/"lake"/"raw","raw"),(ROOT/"data"/"processed","processed"),(ROOT/"data"/"features","features"),(ROOT/"reports","reports")]:
    if folder.exists():
        print("Uploading",folder)
        upload_tree(folder,prefix)
