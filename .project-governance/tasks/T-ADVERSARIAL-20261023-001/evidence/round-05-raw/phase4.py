from independent_suite import *
import importlib.metadata, shutil
CASES.extend(json.loads((TEMP/'cases.json').read_text(encoding='utf-8')))
CALLS.extend(json.loads((TEMP/'commands.json').read_text(encoding='utf-8')))
FIXTURES.extend(json.loads((TEMP/'fixtures.json').read_text(encoding='utf-8')))

def snapshot_case(name,condition,expected,actual,passed,refs=[]):
    if any(x['name']==name for x in CASES): return next(x for x in CASES if x['name']==name)
    ev=LOG/(f'{len(CALLS)+1:03}-{name}.json');dump(ev,{'at':now(),'actual':actual});CALLS.append({'label':name,'method':'read-only independent inspection','evidence':str(ev)});save()
    return check(name,condition,None,expected,actual,[str(ev),*refs],passed)

def derived_check(f,expected,label):
    p,s,e=cli('signals.py',['--project-root',f.root],label+'-signals')
    # Preserve raw structure and use its public task_progress surface.
    records=s.get('task_progress',[]) if isinstance(s,dict) else []
    if not records and isinstance(s,dict):records=s.get('tasks',[])
    target=next((x for x in records if x.get('task_id')==f.task_id),{})
    active=signals.active_task_signal(f.task)
    rec=signals.recommendations([active])
    status=active.get('adversarial_review',{}).get('status')
    is_continue=any('已获同意' in x.get('reason','') for x in rec)
    expected_continue=expected in {'InProgress','Blocked','Stale'}
    check(label+'-signals-status','Derived status and action recommendations',str(f.root),f'{expected}; continue={expected_continue}',{'public_code':p.returncode,'public':s,'active':active,'recommendations':rec},[e],p.returncode==0 and status==expected and is_continue==expected_continue)
    proc,v,ve=cli('generate_review_views.py',['--project-root',f.root,'--project-id','P-AR05'],label+'-views')
    view_path=f.root/'.project-governance/generated'
    matching=[]
    for file in view_path.rglob('*.md'):
        text=file.read_text(encoding='utf-8')
        if (f'# Task Review: {f.task_id}' in text) or (f'# Task {f.task_id}' in text):
            relative=file.relative_to(f.root).as_posix();matching.append({'path':relative,'text':text})
    ev=LOG/(f'{len(CALLS)+1:03}-{label}-markdown.json');dump(ev,matching);CALLS.append({'label':label+'-markdown','method':'generated text inspection','evidence':str(ev)});save()
    check(label+'-markdown-status','Generated review Markdown must use current bound state',str(f.task),f'Shows {expected}',{'view_exit':proc.returncode,'matches':len(matching),'contains_expected':any(expected in x['text'] for x in matching)},[ve,str(ev)],proc.returncode==0 and any(expected in x['text'] for x in matching))

def derived_suite(carrier):
    tag='full' if carrier=='Full' else 'min';f=new(tag+'-derived',carrier)
    derived_check(f,'NotOffered',tag+'-derived-not-offered')
    f.offer(tag+'-derived-offer');derived_check(f,'AwaitingUser',tag+'-derived-await')
    f.decision('Declined',tag+'-derived-decline');derived_check(f,'Declined',tag+'-derived-declined')
    f.decision('Deferred',tag+'-derived-defer');derived_check(f,'Deferred',tag+'-derived-deferred')
    f.decision('Accepted',tag+'-derived-start');derived_check(f,'InProgress',tag+'-derived-active')
    f.entry({'event':'Blocked','reason':'Synthetic environment unavailable','evidence_refs':['ar05-fixture://missing']},tag+'-derived-block','Blocked');derived_check(f,'Blocked',tag+'-derived-blocked')
    r=f.round(tag+'-derived-r1');f.entry(r,tag+'-derived-first','InProgress')
    Path(r['report_ref']).write_text('Synthetic report was materially changed after append.\n',encoding='utf-8');derived_check(f,'Stale',tag+'-derived-stale')
    f.entry(f.round(tag+'-derived-r2'),tag+'-derived-fresh-first','InProgress');f.entry(f.round(tag+'-derived-r3'),tag+'-derived-fresh-second','Passed')
    derived_check(f,'Passed',tag+'-derived-passed')
    (f.task/'evidence'/(tag+'-derived-r3.md')).unlink();derived_check(f,'RestartRequired',tag+'-derived-restart-required')
    f.decision('Accepted',tag+'-derived-new-start');f.decision('Stopped',tag+'-derived-stop');derived_check(f,'Stopped',tag+'-derived-stopped')

try:
    # Inspect manifest entries from disk independently, without invoking the project's self-test.
    roots={'source':SCRIPTS.parent,'installed':Path(r'C:/Users/Administrator/.lfenskills/skills/product-engineering/run-governed-product-workflow')}
    comparisons=[]
    for label,root in roots.items():
        manifest=json.loads((root/'assets/runtime/embedded-manifest.json').read_text(encoding='utf-8-sig'))
        rows=[{'path':x['embedded'],'expected':x['sha256'],'actual':sha(root/x['embedded'])} for x in manifest['files']]
        snapshot_case(label+'-manifest-hashes','Every declared protected runtime asset matches its manifest','All hashes equal',rows,all(x['expected']==x['actual'] for x in rows))
        comparisons.append({'root':label,'files':len(rows)})
    review_paths=['SKILL.md','commands/verify.md','commands/close.md','commands/minimal.md','commands/status.md','scripts/adversarial_review.py','scripts/minimal_task.py','scripts/manage_minimal_task.py','scripts/close_task.py','scripts/signals.py','assets/runtime/schemas/task-after.schema.json','assets/runtime/schemas/minimal-task-record.schema.json']
    rows=[{'path':p,'source_sha256':sha(roots['source']/p),'installed_sha256':sha(roots['installed']/p)} for p in review_paths]
    snapshot_case('review-distribution-files','All review instructions, protocol, carrier close entrypoints, and schemas','Source and installed review files identical',rows,all(x['source_sha256']==x['installed_sha256'] for x in rows))
    after=json.loads((roots['source']/'assets/runtime/schemas/task-after.schema.json').read_text())
    minimal=json.loads((roots['source']/'assets/runtime/schemas/minimal-task-record.schema.json').read_text())
    expected=ar.review_schema()
    actual={'full_matches':after['properties']['adversarial_review']==expected,'minimal_matches':minimal['properties']['task_outcome']['oneOf'][1]['properties']['adversarial_review']==expected}
    snapshot_case('full-minimal-schema-contract','Full and Minimal serialized protocol definitions','Both equal the shared schema',actual,all(actual.values()))
    # Confirm the actual prompt/decision chronology without loading any existing Round report or finding list.
    original=json.loads((REPO/'.project-governance/tasks/T-ADVERSARIAL-20261023-001/after.json').read_text(encoding='utf-8'))
    actual={'completed_at':original['completed_at'],'offers':[x for x in original['adversarial_review'] if x['event']=='Offer'],'decisions':[x for x in original['adversarial_review'] if x['event']=='Decision']}
    latest=json.loads((REPO/'.project-governance/tasks/T-ADVERSARIAL-20261023-005/after.json').read_text(encoding='utf-8'))
    offer=actual['offers'][0];decision=actual['decisions'][0]
    okay=actual['completed_at']<offer['recorded_at']<decision['recorded_at'] and decision['outcome']=='Accepted' and decision['response']=='开始审查' and decision['recorded_at']=='2026-10-23T09:58:06.866514Z' and latest['user_decision']=={'outcome':'Pending'}
    snapshot_case('actual-offer-consent-order','Real engineering outcome saved, then real question, then explicit choice','Chronology matches supplied trusted human source; Acceptance remains Pending',actual,okay)
    # Inspect the two explicit source artifacts, no older round artifacts.
    for key,entry in [('offer',offer),('consent',decision)]:
        p=REPO/entry['evidence_ref'];copy_to=TEMP/('actual-'+key+'-source.json');shutil.copyfile(p,copy_to)
        snapshot_case('actual-'+key+'-source','Actual recorded interaction evidence exists','Nonempty exact source file',{'path':entry['evidence_ref'],'sha256':sha(p),'text':p.read_text(encoding='utf-8')},p.stat().st_size>0,[str(copy_to)])
    derived_suite('Full');derived_suite('Minimal')
    # Exercise installed public CLI against a fresh independently built compatible fixture.
    f=new('installed-public','Full')
    source_scripts=globals()['SCRIPTS']
    import independent_suite as base
    base.SCRIPTS=roots['installed']/'scripts'
    try:
        f.offer('installed-offer');f.decision('Accepted','installed-accept')
        f.entry(f.round('installed-round1'),'installed-first','InProgress');f.entry(f.round('installed-round2'),'installed-second','Passed')
        p,s,e=f.status('installed-passed')
        check('installed-public-clean-pair','Installed protocol consumes independently built fixture',str(f.task),'Passed; clean_streak=2',s,[e],p.returncode==0 and s['status']=='Passed' and s['clean_streak']==2)
    finally:base.SCRIPTS=source_scripts
    dump(TEMP/'phase4-complete.json',{'ended_at':now(),'cases':len(CASES),'failed':[c['id'] for c in CASES if c['result']=='Failed']})
except Exception:
    (TEMP/'phase4-error.txt').write_text(traceback.format_exc(),encoding='utf-8');print(traceback.format_exc());save();sys.exit(1)

