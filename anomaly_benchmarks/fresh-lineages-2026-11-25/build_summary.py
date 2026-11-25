import json
from pathlib import Path
import numpy as np
from review_anomaly_v3.evaluation.object_comparison import read,validate_plan
from review_anomaly_v3.io import sha256_file,write_json
from review_anomaly_v3.pipeline import validate_artifacts
r=Path('work/object-fresh-lineages-2026-11-25');plan=validate_plan(r);s=read(r/'summary.json')
assert s['samples']==18 and s['scope_status_counts']['lasot_original']['no_report']==0
assert all(row['execution'] not in ('unrun','failed') for row in s['results'])
for sample in plan['samples']:validate_artifacts(r/'reports'/sample['id'])
positive=[x for x in s['results'] if x['events']]
controls=[x for x in s['results'] if x['stratum']=='controlled_synthetic' and not x['events']]
originals=[x for x in s['results'] if x['stratum']=='lasot_original']
lineages={}
for name in ['lasot:cup-1','lasot:hand-2']:
 p=[x for x in positive if x['lineage']==name];n=[x for x in controls if x['lineage']==name]
 lineages[name]={'events':len(p),'detected':sum(e['detected'] for x in p for e in x['events']),
                 'type_matched':sum(e['code_detected'] for x in p for e in x['events']),
                 'normal_controls':len(n),'normal_candidates':sum(x['displayed_candidates'] for x in n),
                 'positive_unmatched':sum(x['unmatched_displayed_candidates'] for x in p)}
api=[read(r/'api'/x['id']/'request.json') for x in plan['samples']]
seed=[read(r/'seeds'/x['id']/'result.json') for x in plan['samples']]
assert all(x['status']=='completed' for x in api)
result={'version':'fresh-lineages-v1','package_version':'0.17.0','samples':18,
        'detected_events':s['detected_events'],'expected_type_matched':sum(e['code_detected'] for x in positive for e in x['events']),
        'positive_events':len(positive),'normal_controls':len(controls),'normal_control_candidates':s['control_candidates'],
        'unlabeled_originals':len(originals),'original_review_candidates':s['original_review_candidates'],
        'positive_unmatched_candidates':sum(x['unmatched_displayed_candidates'] for x in positive),
        'scope_status_counts':s['scope_status_counts'],'lineages':lineages,
        'api_requests':sum(x['logical_requests'] for x in api),'api_poll_sessions':sum(x['poll_sessions'] for x in api),
        'seed_requests':sum(x['logical_requests'] for x in seed),'seed_completed':sum(x['status']=='completed' for x in seed),
        'seed_tokens':sum((x.get('usage_metadata') or {}).get('total_token_count',0) or 0 for x in seed),
        'seed_model_versions':sorted({x.get('model_version','unknown') for x in seed}),
        'api_session_seconds_sum':sum(x['total_session_sec'] for x in api),
        'seed_session_seconds_sum':sum(x['elapsed_sec'] for x in seed),
        'local_p50_p95_sec':np.percentile([x['local_timings_sec']['total_before_publication'] for x in s['results']],[50,95]).tolist(),
        'actual_billing_cost_usd':None,'plan_sha256':sha256_file(r/'plan.json'),'summary_sha256':sha256_file(r/'summary.json'),
        'scope':'Fresh-lineage diagnostic on fixed 0.17.0; original false-positive status awaits human review; no post-result tuning'}
write_json(r/'fresh-summary.json',result)
print(json.dumps(result,ensure_ascii=False,indent=2))
for row in s['results']:
 print(row['id'],row['displayed_candidates'],[(e['detected'],e['code_detected']) for e in row['events']],row['coverage']['observability'],row['miss_diagnostics'])
