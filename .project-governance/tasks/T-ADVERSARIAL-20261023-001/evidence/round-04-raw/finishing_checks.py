import review_harness as h, json, pathlib, hashlib, subprocess, os
h.CASES=json.loads((h.BASE/'cases.json').read_text(encoding='utf-8')); h.COUNTER=max(int(p.name[:4]) for p in h.RAW.glob('[0-9][0-9][0-9][0-9]-*.json'))
# Correct the isolated deployment fixture's missing precondition and retain both rejected attempts.
root=h.BASE/'deployed-console'; (root/'.project-governance').mkdir(exist_ok=True)
for flag,label in [([], 'deployment-retry-with-governance'),(['--check'],'deployment-retry-integrity')]:
    raw,res,p=h.cli('deploy_console.py',['--project-root',root,*flag],label)
    h.check(label,raw,{'exit_code':0},raw,raw['exit_code']==0,{'root':str(root),'prerequisite':'.project-governance exists'},p)
snapshot=root/'.project-governance/console/snapshot'
expected=['adversarial_review.py','audit_console.py','check_write_guard.py','console.py','console_assets.py','console_model.py','console_render.py','deploy_console.py','governance_artifacts.py','manage_project_docs.py','minimal_task.py']
match={name:hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==hashlib.sha256((h.SCRIPTS/name).read_bytes()).hexdigest() for name in expected}
p=h.write(h.RAW/'deployment-snapshot-byte-matches.json',match)
h.check('deployment-snapshot-bytes',None,{'all_declared_modules_match':True},match,all(match.values()),{'snapshot':str(snapshot)},p)
# A real saved delivery's subject/time are read, without opening the parent task's past reports.
t=h.REPO/'.project-governance/tasks/T-ADVERSARIAL-20261023-004'
raw,res,p=h.cli('adversarial_review.py',[t],'actual-delivery-004-readonly')
h.check('actual-delivery-004-binding',raw,{'status':'ManagedByParent','subject_sha256':'cec29541e44fc647f301f859e7fcc7f195bf8293615af3d755e534758b2f324a'},res,raw['exit_code']==0 and res['status']=='ManagedByParent' and res['subject_sha256']=='cec29541e44fc647f301f859e7fcc7f195bf8293615af3d755e534758b2f324a',{'task':str(t)},p)
actual=gdoc=h.g.read_json(t/'after.json'); events=h.g.read_jsonl(t/'run.jsonl')
h.write(h.BASE/'actual-delivery.json',{'task_id':t.name,'completed_at':actual['completed_at'],'last_verification_at':max(e['timestamp'] for e in events if e['event_type']=='verification' and e['status']=='succeeded'),'subject_sha256':res['subject_sha256'],'session_start_marker':'2026-10-23T12:32:59.265574Z'})
# Recheck every frozen source at review end.
manifest=json.loads((h.REPO/'.project-governance/tasks/T-ADVERSARIAL-20261023-004/evidence/source-files-a6d4cdcbfd9e3544.json').read_text(encoding='utf-8'))
files=manifest['source_files']; mismatches=[]
for f in files:
    actual=hashlib.sha256((h.REPO/f['path']).read_bytes()).hexdigest()
    if actual!=f['sha256']: mismatches.append({**f,'actual':actual})
p=h.write(h.RAW/'end-freeze-verification.json',{'at':h.now(),'count':len(files),'mismatches':mismatches})
h.check('end-freeze-unchanged',None,{'file_count':96,'mismatches':[]},{'file_count':len(files),'mismatches':mismatches},len(files)==96 and not mismatches,ref=p)
# Classify rejected setup attempts separately from the single confirmed product root cause.
for c in h.CASES:
    if c['id'] in ['C172','C173']:
        c['classification']='HarnessSetup'; c['reason']='Synthetic fixture omitted the required .project-governance directory. Public CLI correctly rejected it; retried after satisfying the prerequisite.'
    elif c['result']=='Failed':
        c['classification']='ProductFinding'; c['finding_ids']=['AR04-F01']
        if c['id'] in ['C157','C158','C159']: c['dependent_cascade']=True
    else: c['classification']='Verified'
h.write(h.BASE/'cases.json',h.CASES)
h.write(h.BASE/'final-case-summary.json',{'at':h.now(),'case_count':len(h.CASES),'passed':sum(c['result']=='Passed' for c in h.CASES),'product_assertion_failures':sum(c.get('classification')=='ProductFinding' for c in h.CASES),'setup_failures_retried':sum(c.get('classification')=='HarnessSetup' for c in h.CASES),'unique_confirmed_findings':['AR04-F01']})
print((h.BASE/'final-case-summary.json').read_text(encoding='utf-8'))
