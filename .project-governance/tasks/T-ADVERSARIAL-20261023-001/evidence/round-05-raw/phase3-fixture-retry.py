from independent_suite import *
CASES.extend(json.loads((TEMP/'cases.json').read_text(encoding='utf-8')))
CALLS.extend(json.loads((TEMP/'commands.json').read_text(encoding='utf-8')))
FIXTURES.extend(json.loads((TEMP/'fixtures.json').read_text(encoding='utf-8')))
for carrier,tag,old_id in [('Full','full','AR05-C190'),('Minimal','min','AR05-C202')]:
    task=TEMP/'fixtures/attempt5'/(tag+'-historical-engineering')/'.project-governance/tasks'/('T-'+tag.upper()+'-HISTORICAL-ENGINEERING')
    f=Fixture.__new__(Fixture);f.task=task;f.root=task.parents[2];f.carrier=carrier;f.task_id=task.name;f.path=task/('after.json' if carrier=='Full' else 'task-record.json')
    if carrier=='Full':
        events=g.read_jsonl(task/'run.jsonl')
        for event in events:event['timestamp']='2026-08-15T00:00:00Z'
        (task/'run.jsonl').write_text(''.join(json.dumps(ev,ensure_ascii=False)+'\n' for ev in events),encoding='utf-8')
    else:
        d,_=f.data()
        for event in d['run_ledger']:event['timestamp']='2026-08-15T00:00:00Z'
        dump(f.path,d)
    before={str(p):sha(p) for p in task.iterdir() if p.is_file()}
    p,s,e=f.status(tag+'-historical-corrected-timestamps')
    after={str(p):sha(p) for p in task.iterdir() if p.is_file()}
    c=check(tag+'-historical-corrected-input','Corrected fixture moves ledger timestamp before cutover',str(task),'LegacyUntracked; no bytes changed',{'exit_code':p.returncode,'state':s,'stderr':p.stderr},[e],p.returncode==0 and s['status']=='LegacyUntracked' and before==after)
    for old in CASES:
        if old['id']==old_id:
            old['classification']='FixtureError';old['cause']='The synthetic fixture aging helper changed *_at fields but omitted ledger timestamp; it did not satisfy its claimed pre-cutover input.';old['corrected_by']=c['id']
    save()
