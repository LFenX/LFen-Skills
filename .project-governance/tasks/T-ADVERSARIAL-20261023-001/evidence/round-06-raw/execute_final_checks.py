from review_cases import *
CASES.extend(json.loads((ARCHIVE/'cases.json').read_text(encoding='utf-8')))
BASE=ARCHIVE/'final-fixtures'

def cli(args,label):
    cmd=[sys.executable,'-X','utf8']+[str(x) for x in args]
    p=subprocess.run(cmd,cwd=ARCHIVE,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    d={'command':cmd,'cwd':str(ARCHIVE),'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'at':stamp()};jwrite(RAW/(label+'-command.json'),d);return d

for carrier in ['Full','Minimal']:
    k=carrier[0];root=BASE/('io-'+carrier);t=create(root,'T-IO-'+k,carrier);authorize(t)
    write_entry(t,roundentry(t,'before-io'))
    e=roundentry(t,'io-retry');before=snapshot(t);replace=ga.os.replace
    def fail_replace(src,dst):
        if Path(dst).parent.resolve()==t.resolve():raise OSError('SYNTHETIC AR06 injected atomic replacement failure in Temp only')
        return replace(src,dst)
    def injected():
        ga.os.replace=fail_replace
        try:return write_entry(t,e)
        finally:ga.os.replace=replace
    case('IO'+k+'01','Atomic write failure leaves prior engineering/review/acceptance facts and authorization intact',{'entry':e,'fault':'os.replace Temp-only OSError'},'OSError, no stored changes or leaked lock/temp file',injected,lambda a:not a['accepted'] and a.get('exception')=='OSError' and snapshot(t)==before)
    def retry():write_entry(t,e);return ar.review_status(t)
    case('IO'+k+'02','Retry same authorized failed append can succeed without repeated human consent',e,'Passed / clean2 with one actual appended retry',retry,lambda a:a['accepted'] and a['value']['status']=='Passed' and a['value']['rounds']==2)
    # Active current parent, but false dependency/project must fail.
    p=create(root,'T-OWNERSHIP-P-'+k,carrier);authorize(p)
    not_child=create(root,'T-NOT-CHILD-'+k,carrier)
    case('P'+k+'01','Repair ownership requires direct dependency on original task',{'candidate':not_child.name,'parent':p.name},'Rejected',lambda:ar.require_review_parent(not_child,saved(not_child)[2],p.name),reject)
    contract=copy.deepcopy(saved(not_child)[2]);contract['depends_on']=[p.name];contract['project_id']='P-SYNTHETIC-OTHER'
    case('P'+k+'02','Repair association cannot cross project authority boundary',{'candidate_contract':contract,'parent':p.name},'Rejected',lambda:ar.require_review_parent(not_child,contract,p.name),reject)
    # Simulate genuine pre-cutover read-only structure. These are not real historical claims.
    hroot=BASE/('precutover-'+carrier);h=create(hroot,'T-PRECUTOVER-'+k,carrier)
    old='2026-09-01T00:00:00Z'
    if carrier=='Full':
        b=ga.read_json(h/'before.json');a=ga.read_json(h/'after.json');events=ga.read_jsonl(h/'run.jsonl')
        for d in [b,a]:
            d.pop('proof_contract_version',None);d['amendments']=[]
        b['created_at']=old;b['frozen_at']=old;a['completed_at']=old
        for it in b['requirement_items']:it.pop('review',None)
        for it in b['decisions']:it.pop('outcome',None);it.pop('subject_sha256',None);it['decided_at']=old
        a.pop('user_decision',None);a.pop('adversarial_review',None);a.pop('scope_reconciliation',None)
        for it in events:it['timestamp']=old
        jwrite(h/'before.json',b);jwrite(h/'after.json',a);(h/'run.jsonl').write_text(''.join(json.dumps(it,ensure_ascii=False)+'\n' for it in events),encoding='utf-8')
    else:
        d=ga.read_json(h/'task-record.json');d.pop('proof_contract_version',None);d['amendments']=[];d['created_at']=old;d['completed_at']=old
        for it in d['task_contract']['requirement_items']:it.pop('review',None)
        for it in d['task_contract']['decisions']:it.pop('outcome',None);it.pop('subject_sha256',None);it['decided_at']=old
        for it in d['run_ledger']:it['timestamp']=old
        d['task_outcome'].pop('user_decision',None);d['task_outcome'].pop('adversarial_review',None);d['task_outcome']['completed_at']=old
        jwrite(h/'task-record.json',d)
    old_snapshot=snapshot(h)
    def histread():
        errors=ga.validate_task_directory(h)
        data=ga.read_json(h/('before.json' if carrier=='Full' else 'task-record.json'))
        outcome=ga.read_json(h/'after.json') if carrier=='Full' else data['task_outcome']
        events=ga.read_jsonl(h/'run.jsonl') if carrier=='Full' else data['run_ledger']
        return {'errors':errors,'proof':ga.proof_validation_for_read(data,events,outcome,minimal=carrier=='Minimal')[0],'review':ar.review_status(h),'unchanged':snapshot(h)==old_snapshot}
    case('HP'+k+'01','Pre-cutover outcomes retain original status without fabricated review/approval or source rewrites',{'task':h.name,'synthetic_pre_cutover_fixture':True},'valid / HistoricalNotRevalidated / LegacyUntracked / unchanged',histread,lambda a:a['accepted'] and a['value']['errors']==[] and a['value']['proof']['status']=='HistoricalNotRevalidated' and a['value']['review']['status']=='LegacyUntracked' and a['value']['unchanged'])

# Shared schema, runtime protected hashes and installed source boundary.
schema1=ga.read_json(SKILL/'assets/runtime/schemas/task-after.schema.json')['properties']['adversarial_review']
schema2=ga.read_json(SKILL/'assets/runtime/schemas/minimal-task-record.schema.json')['properties']['task_outcome']['oneOf'][1]['properties']['adversarial_review'] if False else None
# Find the aggregate outcome node independent of its nullable schema wrapper.
def find_review(node):
    if isinstance(node,dict):
        if 'properties' in node and 'adversarial_review' in node['properties']:return node['properties']['adversarial_review']
        for v in node.values():
            found=find_review(v)
            if found is not None:return found
    if isinstance(node,list):
        for v in node:
            found=find_review(v)
            if found is not None:return found
    return None
schema2=find_review(ga.read_json(SKILL/'assets/runtime/schemas/minimal-task-record.schema.json'))
case('D01','Full and Minimal schemas share the runtime review protocol definition',{'schemas':['task-after.schema.json','minimal-task-record.schema.json']},'both equal review_schema()',lambda:{'full_matches':schema1==ar.review_schema(),'minimal_matches':schema2==ar.review_schema(),'protected_errors':ga.validate_embedded_manifest(SKILL)},lambda a:a['accepted'] and a['value']['full_matches'] and a['value']['minimal_matches'] and a['value']['protected_errors']==[])
diff=json.loads((ARCHIVE/'distribution-hash-differences.json').read_text(encoding='utf-8'))
case('D02','Installed distribution equals 96-file frozen bundle except explicitly retained other-chat patch',{'expected_installed_override':'add9aff766c9b5ddb3eed0cdf5da8f7e464707648f5ea4870c98a462002ae153'},'95 equal, only known governance_artifacts.py patch differs',lambda:diff,lambda a:a['accepted'] and a['value']['file_count']==96 and len(a['value']['differences'])==1 and a['value']['differences'][0]['path']=='scripts/governance_artifacts.py' and a['value']['differences'][0]['installed']=='add9aff766c9b5ddb3eed0cdf5da8f7e464707648f5ea4870c98a462002ae153')

for carrier in ['Full','Minimal']:
    root=ARCHIVE/'executed-fixtures'/'lifecycle'/carrier;t=next((root/'.project-governance/tasks').iterdir());k=carrier[0]
    result=cli([SKILL/'scripts/generate_review_views.py','--project-root',root,'--project-id','P-AR06'],'CLI-'+k+'-GENERATE')
    rp=root/'.project-governance/generated/reviews'/(t.name+'.md')
    case('D'+k+'03','Documented generation command renders current review state from bound authority source',{'command_evidence':'raw/CLI-'+k+'-GENERATE-command.json'},'exit0; task review shows InProgress/clean1 and independent Rejected Acceptance',lambda:{'cli':result,'text':rp.read_text(encoding='utf-8')},lambda a:a['accepted'] and a['value']['cli']['returncode']==0 and 'InProgress' in a['value']['text'] and "'clean_streak': 1" in a['value']['text'] and '用户验收未通过' in a['value']['text'])

actual=REPO/'.project-governance/tasks/T-ADVERSARIAL-20261023-005'
case('A01','Actual frozen 005 delivery reads as Implemented/ManagedByParent with independent Pending decision',{'task':actual.name},'valid; ManagedByParent; expected saved subject',lambda:{'validation':ga.validate_task_directory(actual),'status_cli':cli([SKILL/'scripts/adversarial_review.py',actual],'ACTUAL-005-STATE'),'decision':ga.read_json(actual/'after.json')['user_decision']},lambda a:a['accepted'] and a['value']['validation']==[] and a['value']['decision']=={'outcome':'Pending'} and json.loads(a['value']['status_cli']['stdout'])['status']=='ManagedByParent' and json.loads(a['value']['status_cli']['stdout'])['subject_sha256']=='1ec6406b7c95580a24ef77723932c6bfd76fbd1a40bbf900f685f7261fd6acac')
original=json.loads((ARCHIVE/'allowed-original-input.json').read_text(encoding='utf-8'))
case('A02','Actual preserved original words and explicit post-completion choice match authorized task inputs',{'expected_requirements_sha256':'57bfbf29e4c6814f1e5638d026ebc0c59a448ec654942469a082c53d94dd92ca'},'matching source binding; explicit Accepted starts actual review; Pending Acceptance independent',lambda:{'requirements_sha256':ar.requirements_subject(original),'offer_decision':original['offer_decision']},lambda a:a['accepted'] and a['value']['requirements_sha256']=='57bfbf29e4c6814f1e5638d026ebc0c59a448ec654942469a082c53d94dd92ca' and a['value']['offer_decision'][1]['outcome']=='Accepted' and a['value']['offer_decision'][1]['response']=='开始审查')

# Check rejected append atomicity recorded throughout the first suite.
lines=[json.loads(l) for l in (RAW/'api-events.jsonl').read_text(encoding='utf-8').splitlines()]
atomic=[l for l in lines if l['kind']=='append_snapshot']
failmap={c['id']:c for c in CASES}
selected=[l for l in atomic if failmap.get(l['input']['case'],{}).get('actual',{}).get('accepted') is False]
case('IO03','All rejected protocol appends retained exactly the prior stored files',{'rejected_snapshot_count':len(selected)},'each before snapshot equals after',lambda:{'checked':len(selected),'mismatches':[l['input']['case'] for l in selected if l['input']['before']!=l['output']]},lambda a:a['accepted'] and a['value']['checked']>0 and a['value']['mismatches']==[])
jwrite(ARCHIVE/'cases.json',CASES)
print('TOTAL',len(CASES),'FAILED',sum(c['result']=='Failed' for c in CASES),flush=True)
