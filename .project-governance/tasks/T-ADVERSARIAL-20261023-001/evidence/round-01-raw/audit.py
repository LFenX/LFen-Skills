import sys, json, copy, hashlib, traceback, subprocess, os
from pathlib import Path
from datetime import datetime, timezone, timedelta
sys.dont_write_bytecode = True
SCRIPTS = Path(r'D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts')
sys.path.insert(0, str(SCRIPTS))
from governance_artifacts import (read_json, read_jsonl, atomic_write_json, append_run_event, close_task, amend_record, amend_record_batch, now_utc, user_decision_subject_sha256, validate_task_directory, validate_embedded_manifest, GovernanceError)
from minimal_task import append_minimal_event, close_minimal_record, minimal_approval_contract, record_minimal_review
from adversarial_review import append_review, review_state, requirements_subject, review_schema
from self_test import new_task, minimal_fixture_record, fixture_discharge_items
from signals import active_task_signal, recommendations
import console_model, console_render, deploy_console
ROOT = Path(__file__).resolve().parent
RESULTS=[]
def log(name, **data):
    entry={'case':name,**data}; RESULTS.append(entry); print(json.dumps(entry, ensure_ascii=False), flush=True)
def load(task):
    minimal=not (task/'before.json').is_file()
    path=task/('task-record.json' if minimal else 'after.json')
    d=read_json(path); o=d['task_outcome'] if minimal else d
    c=minimal_approval_contract(d) if minimal else read_json(task/'before.json')
    e=d['run_ledger'] if minimal else read_jsonl(task/'run.jsonl')
    return path,d,o,c,e
def create(name, minimal=False, depends=()):
    root=ROOT/name; root.mkdir(exist_ok=True)
    tid='T-MIN' if minimal else 'T-FULL'
    if depends:
        # A repair is created beside the original task, using the original project.
        root=Path(depends[0]); tid=name; depends=depends[1]
    task=root/'.project-governance/tasks'/tid
    if minimal:
        path=minimal_fixture_record(root,tid)
        append_minimal_event(task,event_type='run_started',summary='Isolation fixture start',status='started')
        append_minimal_event(task,event_type='verification',summary='Isolation fixture verification',status='succeeded',evidence_refs=['fixture://verified'])
        d=read_json(path)
        record_minimal_review(task,requirement_items=fixture_discharge_items(d['task_contract']),reason='Fixture covered inputs',basis='fixture://original')
        close_minimal_record(task,status='Implemented',established_facts=['Isolation fixture complete'],actual_changes=['Fixture label changed'],verification=['Passed::Isolation check::fixture://verified'])
    else:
        new_task(root,tid,1,depends_on=depends)
        b=read_json(task/'before.json'); b['authority']['required_gates']=[]; atomic_write_json(task/'before.json',b)
        append_run_event(task,run_id='RUN',attempt_id='A1',event_type='run_started',summary='Isolation fixture start',status='started')
        append_run_event(task,run_id='RUN',attempt_id='A1',event_type='verification',summary='Isolation fixture verification',status='succeeded',evidence_refs=['fixture://verified'])
        b=read_json(task/'before.json')
        amend_record(task/'before.json',dotted_path='requirement_items',new_value=fixture_discharge_items(b),reason='Fixture covered inputs',basis='fixture://original')
        append_run_event(task,run_id='RUN',attempt_id='A1',event_type='run_finished',summary='Isolation fixture finish',status='succeeded')
        close_task(task,status='Implemented',established_facts=['Isolation fixture complete'],actual_changes=['Fixture change'],verification=[{'result':'Passed','summary':'Isolation check','evidence_refs':['fixture://verified']}])
    return task

def write(task,item):
    return append_review(task,item,reason='Independent isolated protocol experiment',basis='fixture://adversarial-round-01')
def offer(task):
    write(task,{'event':'Offer','recorded_at':now_utc(),'prompt':'工程结果已保存。是否启动对抗性审查？开始、不需要或稍后决定。','evidence_ref':'fixture://post-completion-question'})
def decision(task, choice='Accepted'):
    write(task,{'event':'Decision','recorded_at':now_utc(),'outcome':choice,'response':'Fixture explicit '+choice,'decided_by':'synthetic-fixture-user','evidence_ref':'fixture://answer'})
def ready(task): offer(task); decision(task)
def round_entry(task,number,delivery=None,**changes):
    _,_,o,c,e=load(task)
    _,_,do,dc,de=load(delivery or task)
    item={'event':'Round','round_id':f'R{number}','started_at':now_utc(),'recorded_at':now_utc(),'reviewer':'independent-isolation-fixture','delivery_task_id':(delivery or task).name,'subject_sha256':user_decision_subject_sha256(dc,de,do),'requirements_sha256':requirements_subject(c),'coverage':'Complete','unreviewed_items':[],'evidence_refs':[f'fixture://{task.parent.parent.parent.name}/report-{number}'],'findings':[],'resolutions':[]}
    item.update(changes); item['recorded_at']=now_utc(); return item

def attempt(name, task, item, expected='reject'):
    p,*_=load(task); before=p.read_bytes()
    try:
        write(task,item)
        actual='accepted'; err=''
    except (GovernanceError,OSError,ValueError,KeyError,TypeError) as ex:
        actual='rejected'; err=str(ex)
    log(name,expected=expected,actual=actual,error=err,unchanged=p.read_bytes()==before,state=review_state(load(task)[2],load(task)[3]))

log('runtime_integrity',errors=validate_embedded_manifest())
for minimal in (False,True):
    kind='Minimal' if minimal else 'Full'
    t=create('baseline-'+kind,minimal)
    p,d,o,c,e=load(t)
    log(kind+' initial',state=review_state(o,c),validation=validate_task_directory(t),user_decision=o['user_decision'])
    attempt(kind+' decision-before-offer',t,{'event':'Decision','recorded_at':now_utc(),'outcome':'Accepted','response':'accepted','decided_by':'fixture','evidence_ref':'fixture://answer'})
    offer(t)
    attempt(kind+' no-response-no-round',t,round_entry(t,1))
    for choice in ('Declined','Deferred'):
        decision(t,choice); attempt(kind+' '+choice+'-no-round',t,round_entry(t,1)); offer(t)
    decision(t)
    attempt(kind+' wrong-subject',t,round_entry(t,1,subject_sha256='0'*64))
    attempt(kind+' wrong-original',t,round_entry(t,1,requirements_sha256='0'*64))
    attempt(kind+' naive-time',t,round_entry(t,1,started_at='2026-10-23T00:00:00'))
    attempt(kind+' future-time',t,{**round_entry(t,1),'recorded_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()})
    attempt(kind+' prior-optin-start',t,round_entry(t,1,started_at='2026-01-01T00:00:00Z'))
    write(t,round_entry(t,1))
    log(kind+' one-clean',state=review_state(load(t)[2],load(t)[3]))
    attempt(kind+' same-id',t,round_entry(t,1,evidence_refs=['fixture://new-report']))
    attempt(kind+' same-ref',t,round_entry(t,2,evidence_refs=load(t)[2]['adversarial_review'][-1]['evidence_refs']))
    write(t,round_entry(t,2,findings=[{'id':'F1','summary':'Fixture confirmed bug','evidence_refs':['fixture://repro']}]))
    log(kind+' found-issue',state=review_state(load(t)[2],load(t)[3]))
    write(t,round_entry(t,3))
    log(kind+' unresolved-finding',state=review_state(load(t)[2],load(t)[3]))
    attempt(kind+' fixed-with-same-version',t,round_entry(t,4,resolutions=[{'finding_id':'F1','disposition':'Fixed','reason':'fixture claimed fix','evidence_refs':['fixture://fix']}]))
    write(t,round_entry(t,4,resolutions=[{'finding_id':'F1','disposition':'NotAnIssue','reason':'fixture disproved finding','evidence_refs':['fixture://counterexample']}]))
    write(t,round_entry(t,5,coverage='Incomplete'))
    log(kind+' incomplete',state=review_state(load(t)[2],load(t)[3]))
    write(t,round_entry(t,6,unreviewed_items=['fixture unavailable branch']))
    log(kind+' unreviewed',state=review_state(load(t)[2],load(t)[3]))
    write(t,{'event':'Blocked','recorded_at':now_utc(),'reason':'fixture unavailable service','evidence_refs':['fixture://blocker']})
    log(kind+' blocked',state=review_state(load(t)[2],load(t)[3]))
    write(t,round_entry(t,7)); write(t,round_entry(t,8))
    log(kind+' two-clean',state=review_state(load(t)[2],load(t)[3]),validation=validate_task_directory(t),user_decision_preserved=load(t)[2]['user_decision']==o['user_decision'],ledger_preserved=load(t)[4]==e)
    attempt(kind+' after-pass-extra-round',t,round_entry(t,9))
    offer(t); decision(t); decision(t,'Stopped')
    attempt(kind+' stopped',t,round_entry(t,9))
    # Legacy record reads remain untracked; append enrollment is forbidden.
    clone=ROOT/('legacy-'+kind); import shutil; shutil.copytree(t.parent.parent.parent,clone)
    lt=clone/'.project-governance/tasks'/t.name
    lp,ld,lo,lc,le=load(lt); lo.pop('adversarial_review'); atomic_write_json(lp,ld)
    log(kind+' legacy-read',state=review_state(lo,lc))
    attempt(kind+' legacy-append',lt,{'event':'Offer','recorded_at':now_utc(),'prompt':'Fixture legacy question','evidence_ref':'fixture://legacy'})

# Counterexample 1: a public Full outcome amendment changes the delivery binding after Passed.
t=create('stale-version'); ready(t); write(t,round_entry(t,1)); write(t,round_entry(t,2))
p,d,o,c,e=load(t); old_subject=user_decision_subject_sha256(c,e,o)
checks=copy.deepcopy(o['verification']); checks[0]['summary']='Corrected verification against delivery B'; checks[0]['evidence_refs']=['fixture://verified-B']
amend_record(p,dotted_path='verification',new_value=checks,reason='Isolated correction to the engineering validation',basis='fixture://verified-B')
p,d,o,c,e=load(t); new_subject=user_decision_subject_sha256(c,e,o)
cli=subprocess.run([sys.executable,'-B','-X','utf8',str(SCRIPTS/'adversarial_review.py'),str(t)],capture_output=True,text=True,encoding='utf-8')
log('counterexample-stale-Passed-after-delivery-change',old_subject=old_subject,new_subject=new_subject,subject_changed=old_subject!=new_subject,state=review_state(o,c),validation=validate_task_directory(t),cli_exit=cli.returncode,cli_stdout=cli.stdout,cli_stderr=cli.stderr,fixture=str(t))

# Counterexample 2: repair rounds can begin before the referenced result was verified/saved.
for minimal in (False,True):
    kind='Minimal' if minimal else 'Full'
    t=create('repair-time-'+kind,minimal); ready(t)
    write(t,round_entry(t,1,findings=[{'id':'F-time','summary':'Fixture repair needed','evidence_refs':['fixture://initial-failure']}]))
    started=now_utc()
    repair=create('T-REPAIR',False,depends=(t.parent.parent.parent,[t.name]))
    _,_,ro,rc,re=load(repair)
    fix={'finding_id':'F-time','disposition':'Fixed','reason':'fixture repair result exists','evidence_refs':['fixture://repair-verified']}
    write(t,round_entry(t,2,delivery=repair,started_at=started,resolutions=[fix]))
    write(t,round_entry(t,3,delivery=repair))
    log(kind+' counterexample-repair-round-before-verified',round_started_at=started,delivery_verified_at=[x['timestamp'] for x in re if x['event_type']=='verification'][-1],delivery_completed_at=ro['completed_at'],state=review_state(load(t)[2],load(t)[3]),validation=validate_task_directory(t),fixture=str(t))

# Counterexample 3: original clarification annotation changes poison append-only history.
t=create('requirements-recovery'); ready(t); write(t,round_entry(t,1))
p,d,o,c,e=load(t); changed=copy.deepcopy(c); changed['clarification']['basis']='Additional survey evidence, same original words'
try:
    observed=review_state(o,changed); error=None
except Exception as ex:
    observed=None; error=str(ex)
log('counterexample-clarification-history-binding',old_requirements=requirements_subject(c),new_requirements=requirements_subject(changed),observed=observed,error=error)
# Apply through supported amendment; Pending acceptance removes independent acceptance binding.
amend_record(t/'before.json',dotted_path='clarification.basis',new_value=changed['clarification']['basis'],reason='Fixture corrects survey basis only',basis='fixture://survey-basis')
try:
    write(t,{'event':'Blocked','recorded_at':now_utc(),'reason':'Old review binding differs','evidence_refs':['fixture://changed-basis']}); blocked='accepted'
except Exception as ex:
    blocked=str(ex)
cli=subprocess.run([sys.executable,'-B','-X','utf8',str(SCRIPTS/'adversarial_review.py'),str(t)],capture_output=True,text=True,encoding='utf-8')
log('counterexample-clarification-change-public-recovery',validation=validate_task_directory(t),blocked_append=blocked,cli_exit=cli.returncode,cli_stdout=cli.stdout,cli_stderr=cli.stderr,fixture=str(t))

# Report strings are not canonical evidence identities: same physical file, aliases.
t=create('report-alias'); ready(t)
report=t/'report.md'; report.write_text('Independent fixture report, reused through an alias.\n',encoding='utf-8')
ref1=str(report); ref2=str(report.parent/'.'/report.name)
# Path string normalization removes dot, so preserve dot as text explicitly.
ref2=str(report.parent)+'/./'+report.name
write(t,round_entry(t,1,evidence_refs=[ref1])); write(t,round_entry(t,2,evidence_refs=[ref2]))
log('counterexample-same-physical-report-aliases',ref1=ref1,ref2=ref2,same_file=Path(ref1).samefile(Path(ref2)),state=review_state(load(t)[2],load(t)[3]),validation=validate_task_directory(t),fixture=str(t))

# Console coverage: test both direct Markdown review and live console detail using real records.
t=create('console-display'); ready(t); write(t,round_entry(t,1,findings=[{'id':'F-CONSOLE-UNIQUE','summary':'Fixture console-visible finding','evidence_refs':['fixture://console-repro']}]))
from governance_artifacts import rebuild_project_state, render_task_review
state=rebuild_project_state(t.parent.parent.parent,project_id='P-TEST')
model=console_model.scan(t.parent.parent.parent); task_model=model['tasks'][0]; html=console_render.page_task(model,t.name)
(ROOT/'console-page.html').write_text(html,encoding='utf-8')
log('console-live-review-visibility',signal=active_task_signal(t)['adversarial_review'],model_keys=list(task_model),html_contains_status='InProgress' in html,html_contains_issue='F-CONSOLE-UNIQUE' in html,html_contains_review_label='对抗性审查' in html,markdown_contains_review='Adversarial review' in render_task_review(load(t)[3],load(t)[2]),fixture=str(t))
log('console-import-closure',declared=list(deploy_console.SNAPSHOT_MODULES),computed=list(deploy_console.computed_closure(SCRIPTS)),equal=deploy_console.SNAPSHOT_MODULES==deploy_console.computed_closure(SCRIPTS))
log('deployed-console-hashes',status=deploy_console.deployment_status(Path(r'D:\LFEN_project\dev_project\LFen-Skills'),SCRIPTS.parent))
(ROOT/'results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2),encoding='utf-8')
print('EVIDENCE_ROOT='+str(ROOT),flush=True)
