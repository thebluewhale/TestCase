#!/usr/bin/env python3
"""Development evaluation; labels are read only after local inference."""
import argparse,json
from collections import Counter
from hashlib import sha256
from pathlib import Path
from time import perf_counter
from review_product_consistency_v4.metrology_engine import MetrologyRunner
from review_product_consistency_v4.assets import owned_path
from review_product_consistency_v4.report import write_bundle
from review_product_consistency_v4.pipeline import package_fingerprint


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--names',nargs='+')
    parser.add_argument('--product-id',choices=['galaxy-s25-ultra','galaxy-s26-ultra'],default='galaxy-s25-ultra')
    parser.add_argument('--manifest',help='Manifest path relative to v4 root')
    parser.add_argument('--include-excluded',action='store_true',help='Also run reference-overlap/duplicate inputs, tagged in records')
    parser.add_argument('--regions-file',help='Reviewed input region plan relative to v4 root; hash-keyed, no label input')
    parser.add_argument('--timeout',type=float,default=120);parser.add_argument('--side-strip',action='store_true')
    args=parser.parse_args();root=args.root.resolve();out=args.output.resolve()
    if out.exists() or (out.is_relative_to(root) and not out.is_relative_to(root/'outputs')):raise SystemExit('Choose a new outputs/ directory')
    slug=args.product_id.removeprefix('galaxy-').replace('-','_')
    manifest=owned_path(root,args.manifest or f'benchmarks/datasets/{slug}_manifest.jsonl');rows=[json.loads(s) for s in manifest.read_text().splitlines()]
    rows=[r for r in rows if (r['inventory_eligible'] or args.include_excluded) and (not args.names or Path(r['path']).name in args.names)]
    if args.names and len(rows)!=len(set(args.names)):raise SystemExit('Requested images must be unique eligible manifest entries')
    if not rows:raise SystemExit('No evaluation images')
    for row in rows:
        if sha256((root/row['path']).read_bytes()).hexdigest()!=row['sha256']:raise SystemExit('Input changed; refresh manifest review')
    regions={};regions_sha=None
    if args.regions_file:
        from review_product_consistency_v4.metrology.regions import load_regions
        regions,regions_sha=load_regions(owned_path(root,args.regions_file),args.product_id,[r['sha256'] for r in rows])
    out.mkdir(parents=True);runner=MetrologyRunner(root,args.product_id);engine=package_fingerprint();records=[]
    for row in rows:
        start=perf_counter();report,image,refs=runner.run(root/row['path'],timeout=args.timeout,side_strip=args.side_strip,**regions.get(row['sha256'],{}))
        directory=out/Path(row['path']).stem;write_bundle(directory,report,image,refs)
        record={'region_plan_sha256':regions_sha,'input_guidance':regions.get(row['sha256']),'path':row['path'],'inventory_eligible':row['inventory_eligible'],'exclusions':row.get('exclusions',[]),'annotation':row['annotation'],'report':report,'wall_seconds':perf_counter()-start}
        records.append(record)
        (out/'records.json').write_text(json.dumps(records,ensure_ascii=False,allow_nan=False))
        print(json.dumps({'done':len(records),'total':len(rows),'file':Path(row['path']).name,'verdict':report['summary']['verdict'],'mismatches':report['summary']['mismatch_checks'],'reason':report['metrology'].get('reason'),'seconds':round(record['wall_seconds'],2)},ensure_ascii=False),flush=True)
    labels=Counter();items=Counter();normal_alarms=[];failures=[]
    for row in records:
        label=row['annotation'].get('user_image_label','unknown');labels[label]+=1
        for c in row['report']['checks']:items[c['check_id']+':'+c['verdict']+':'+c['execution_status']]+=1
        if not row['report']['metrology']['ok']:failures.append({'path':row['path'],'reason':row['report']['metrology']['reason']})
        if label=='normal' and row['report']['summary']['mismatch_checks']:normal_alarms.append(row['path'])
    summary={'region_plan_sha256':regions_sha,'product_id':args.product_id,'include_excluded':args.include_excluded,'scope':'development evaluation, not holdout accuracy','images':len(records),'labels':dict(labels),'item_counts':dict(items),'normal_alarm_images':normal_alarms,'failures':failures,'external_calls':0,'engine_sha256':engine,'engine_changed_during_run':engine!=package_fingerprint(),'manifest_sha256':sha256(manifest.read_bytes()).hexdigest(),'seconds':[r['wall_seconds'] for r in records],'calibration_status':runner.spec['calibration_status']}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
