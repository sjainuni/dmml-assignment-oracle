import argparse, json
from src.pipeline import run
p=argparse.ArgumentParser(); p.add_argument("--full",action="store_true",help="Reserved for full configured run")
args=p.parse_args()
result=run()
print(json.dumps(result,indent=2))
