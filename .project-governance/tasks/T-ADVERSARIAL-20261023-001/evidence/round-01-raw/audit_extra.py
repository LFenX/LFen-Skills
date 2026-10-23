import sys, json, hashlib, subprocess, copy, threading, traceback
from pathlib import Path
sys.dont_write_bytecode=True
base=Path(__file__).resolve().parent/'audit.py'
prefix=base.read_text(encoding='utf-8-sig').split("log('runtime_integrity'")[0]
exec(compile(prefix,str(base),'exec'),globals())
# Setup helpers are shared; all new assertions and adversarial inputs are specific to this audit.
from governance_artifacts import validate_json_document
schema=json.loads((SCRIPTS.parent/'assets/runtime/schemas/task-after.schema.json').read_text(encoding='utf-8'))
mschema=json.loads((SCRIPTS.parent/'assets/runtime/schemas/minimal-task-record.schema.json').read_text(encoding='utf-8'))
log('schema-parity',Full=schema['properties']['adversarial_review']==review_schema(),Minimal=mschema['properties']['task_outcome']['oneOf'][1]['properties']['adversarial_review']==review_schema())
for minimal in (False,True):
    kind='Minimal' if minimal else 'Full'
    t=create('extra-valid-version-'+kind,minimal); ready(t); write(t,round_entry(t,1))
    repair=create('T-VALID-REPAIR',False,depends=(t.parent.parent.parent,[t.name]))
    write(t,round_entry(t,2,delivery=repair))
    log(kind+' public-version-change-resets',state=review_state(load(t)[2],load(t)[3]))
    write(t,round_entry(t,3,delivery=repair))
    log(kind+' repaired-two-clean-then-pass',state=review_state(load(t)[2],load(t)[3]))
    attempt(kind+' generic-round-after-pass',t,round_entry(t,4))

# Missing saved result: use independent active task from setup APIs.
for minimal in (False,True):
    kind='Minimal' if minimal else 'Full'
    root=ROOT/('unsaved-'+kind); root.mkdir(); tid='T-UNSAVED'
    if minimal: minimal_fixture_record(root,tid)
    else: new_task(root,tid,1)
    task=root/'.project-governance/tasks'/tid
    try: offer(task); result='accepted'
    except Exception as ex: result=str(ex)
    log(kind+' unsaved-result-refuses-offer',actual=result)

# Local canonical schema/CLI help compatibility and installed copy parity.
from audit_norm_retrieval import canonical_help
expected=json.loads((SCRIPTS.parent/'assets/runtime/evaluations/norm-retrieval-gold.json').read_text(encoding='utf-8'))
def find_cli(obj):
    if isinstance(obj,dict):
        if obj.get('script')=='adversarial_review.py': return obj
        for value in obj.values():
            got=find_cli(value)
            if got: return got
    elif isinstance(obj,list):
        for value in obj:
            got=find_cli(value)
            if got: return got
    return None
help_contract=find_cli(expected)
cli=subprocess.run([sys.executable,'-B',str(SCRIPTS/'adversarial_review.py'),'--help'],capture_output=True,text=True,encoding='utf-8')
log('CLI-help-contract',returncode=cli.returncode,hash=hashlib.sha256(canonical_help(cli.stdout).encode()).hexdigest(),expected=help_contract)
installed=Path(r'C:\Users\Administrator\.lfenskills\skills\product-engineering\run-governed-product-workflow')
paths=['SKILL.md','commands/verify.md','commands/close.md','commands/minimal.md','commands/status.md','scripts/adversarial_review.py','scripts/governance_artifacts.py','scripts/minimal_task.py','scripts/signals.py','scripts/deploy_console.py','scripts/self_test.py','assets/runtime/schemas/task-after.schema.json','assets/runtime/schemas/minimal-task-record.schema.json','assets/runtime/embedded-manifest.json','assets/runtime/evaluations/norm-retrieval-gold.json']
log('installed-runtime-parity',root=str(installed),files=[{'path':p,'exists':(installed/p).is_file(),'same':(installed/p).is_file() and (installed/p).read_bytes()==(SCRIPTS.parent/p).read_bytes()} for p in paths])
# Read-only public query must not modify task or project assets.
t=create('cli-readonly'); ready(t)
root=t.parent.parent.parent
def tree_digest(): return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
before=tree_digest(); cli=subprocess.run([sys.executable,'-B','-X','utf8',str(SCRIPTS/'adversarial_review.py'),str(t)],capture_output=True,text=True,encoding='utf-8'); after=tree_digest()
log('CLI-readonly-byte-preservation',returncode=cli.returncode,unchanged=before==after,added=sorted(set(after)-set(before)))
# Malformed top-level JSON must fail without partial write. Observe exception formatting too.
for value,label in [([], 'array'),(None,'null'),('wrong','string'),({},'object-missing-fields')]:
    payload=ROOT/('invalid-'+label+'.json'); payload.write_text(json.dumps(value),encoding='utf-8')
    before=load(t)[0].read_bytes()
    cli=subprocess.run([sys.executable,'-B','-X','utf8',str(SCRIPTS/'adversarial_review.py'),str(t),'--entry-json-file',str(payload),'--reason','Fixture invalid record','--basis','fixture://invalid'],capture_output=True,text=True,encoding='utf-8')
    log('CLI-invalid-'+label,exit=cli.returncode,traceback='Traceback' in cli.stderr,error=cli.stderr,unchanged=load(t)[0].read_bytes()==before)
# Invalid dependency/task id are refused through public append.
t=create('dependency-negative'); ready(t)
other=create('T-UNRELATED',False,depends=(t.parent.parent.parent,[]))
attempt('unrelated-delivery-dependency',t,round_entry(t,1,delivery=other))
attempt('traversal-delivery-id',t,round_entry(t,1,delivery_task_id='../T-UNRELATED'))
# An invalid-state append leaves result bytes and ledger unchanged.
p,d,o,c,e=load(t)
for field,value in [('event','Unknown'),('coverage','Partial'),('round_id',''),('reviewer',''),('findings',[{'id':'F','summary':'failure','evidence_refs':[]}])]:
    attempt('schema-reject-'+field,t,round_entry(t,1,**{field:value}))

# Concurrency counterexample: Full public amendment reads before append, then overwrites its new history.
# Interleave only in-memory scheduling of the normal two APIs; no writer bypasses validation.
t=create('concurrent-public-update'); ready(t)
p,d,o,c,e=load(t); old_rounds=len(o['adversarial_review']); old_rev=d['revision']
import governance_artifacts as ga
original_atomic=ga.atomic_write_json
paused=threading.Event(); resume=threading.Event(); thread_errors=[]
def intercept_atomic(path,document):
    if Path(path)==p and threading.current_thread().name=='generic-amendment':
        paused.set()
        if not resume.wait(20): raise RuntimeError('fixture scheduling timeout')
    return original_atomic(path,document)
ga.atomic_write_json=intercept_atomic
new_decision={'outcome':'Rejected','presented':'Fixture verified delivery','response':'Fixture user rejects delivery','decided_by':'synthetic-fixture-user','decided_at':now_utc(),'evidence_ref':'fixture://user-rejection','subject_sha256':user_decision_subject_sha256(c,e,o)}
def amendment_thread():
    try: ga.amend_record(p,dotted_path='user_decision',new_value=new_decision,reason='Fixture delayed user decision',basis='fixture://user-rejection')
    except Exception as ex: thread_errors.append(str(ex))
thread=threading.Thread(target=amendment_thread,name='generic-amendment'); thread.start()
if not paused.wait(20): raise RuntimeError('fixture did not pause amendment')
write(t,round_entry(t,1))
mid=load(t)[2]['adversarial_review'][-1]
resume.set(); thread.join(20); ga.atomic_write_json=original_atomic
p,d,o,c,e=load(t)
log('counterexample-Full-append-lost-by-user-decision-amendment',thread_errors=thread_errors,intermediate_last_event=mid,old_event_count=old_rounds,final_event_count=len(o['adversarial_review']),final_rounds=review_state(o,c)['rounds'],final_user_decision=o['user_decision']['outcome'],validation=validate_task_directory(t),final_revision=d['revision'],old_revision=old_rev,fixture=str(t))
(ROOT/'extra-results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2),encoding='utf-8')
print('EVIDENCE_ROOT='+str(ROOT))
