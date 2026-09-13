"""Select exponential-decay half-life using only a validation window."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from machine_learning.decay_validation import evaluate_half_life
DATA_PATH=Path("data/power655.jsonl")
OUTPUT_PATH=Path("artifacts/backtest_v2/decay_validation.json")
CANDIDATES=(30,60,90,120,180,270,365,540,730)
def main():
    print("DECAY_VALIDATION_START", flush=True)
    rows=[]
    for line in DATA_PATH.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        r=json.loads(line)
        if len(r.get("result",[]))==7: rows.append({"date":pd.to_datetime(r["date"]).date(),"result":r["result"]})
    df=pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    n=len(df); validation_start=int(n*.70); test_start=int(n*.85)
    dates=df.iloc[validation_start:test_start]["date"].tolist()
    results=[evaluate_half_life(df,dates,h).__dict__ for h in CANDIDATES]
    best=max(results,key=lambda r:(r["avg_hits"],-r["half_life_days"]))
    payload={"dataset_rows":n,"train_rows":validation_start,"validation_rows":test_start-validation_start,"test_rows_reserved":n-test_start,"selection_metric":"average_main_number_hits","random_selection_weight":0.0,"candidates":results,"selected_half_life_days":best["half_life_days"]}
    OUTPUT_PATH.parent.mkdir(parents=True,exist_ok=True); OUTPUT_PATH.write_text(json.dumps(payload,indent=2)+"\n")
    assert len(results)==9 and payload["test_rows_reserved"]>0
    print(json.dumps(payload,indent=2),flush=True); print("DECAY_VALIDATION_COMPLETE",flush=True)
if __name__=="__main__": main()
