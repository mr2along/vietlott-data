from __future__ import annotations
import json
from pathlib import Path

def main():
    root=Path('artifacts/backtest_v2')
    summary=json.loads((root/'backtest_summary.json').read_text(encoding='utf-8'))
    mc=json.loads((root/'random_monte_carlo.json').read_text(encoding='utf-8'))
    median=float(mc['roi_percent']['median']); p05=float(mc['roi_percent']['p05']); p95=float(mc['roi_percent']['p95'])
    results={}
    for row in summary:
        name=row['strategy']; roi=float(row['roi_pct'])
        results[name]={'roi_percent':roi,'difference_vs_random_median':roi-median,'inside_random_p05_p95':p05<=roi<=p95,'screening_conclusion':'not_better_than_random' if roi<=p95 else 'above_random_p95'}
    report={'method':'Monte Carlo percentile screening','random_median_roi_percent':median,'random_p05_roi_percent':p05,'random_p95_roi_percent':p95,'strategies':results,'warning':'Screening only; exact empirical p-values require raw Monte Carlo ROI samples and paired per-draw results.'}
    (root/'strategy_significance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
