from __future__ import annotations
import sys, os, json, hashlib, shutil, subprocess, traceback, copy, inspect
from pathlib import Path
from datetime import datetime, timezone, timedelta
sys.dont_write_bytecode=True
REPO=Path(r'D:\LFEN_project\dev_project\LFen-Skills')
SKILL=REPO/'skills/product-engineering/run-governed-product-workflow'
OUT=Path(r'C:\Users\Administrator\AppData\Local\Temp\LFen-AR03-20261023')
sys.path.insert(0,str(SKILL/'scripts'))
import governance_artifacts as g
import minimal_task as m
import adversarial_review as ar
from self_test import new_task, minimal_fixture_record

def stamp(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def save(path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def task_parts(task): return ar._read_saved(task)
def source_review(contract):
    items=copy.deepcopy(contract['requirement_items'])
    for item in items:
        item['review']={'source_sha256':hashlib.sha256(contract['request_snapshot']['text'].encode()).hexdigest(),'conditions':[], 'cases':[{'condition':None,'branch':'Unconditional','input':'src/label.txt bytes','expected':'label=v1','actual':'label=v1','result':'Passed','evidence_refs':['src/label.txt']}]}
    return items

def finish_full(task,parent=None):
    before=g.read_json(task/'before.json')
    g.amend_record(task/'before.json',dotted_path='requirement_items',new_value=source_review(before),reason='Synthetic fixture original-word review',basis='src/label.txt')
    rid=task.name+'-R'
    for event,status in [('run_started','started'),('verification','succeeded')]:
        g.append_run_event(task,run_id=rid,attempt_id='A-1',event_type=event,summary='Synthetic fixture: local label exact content observed',status=status,evidence_refs=['src/label.txt'])
    before=g.read_json(task/'before.json'); events=g.read_jsonl(task/'run.jsonl')
    g.append_run_event(task,run_id=rid,attempt_id='A-1',event_type='human_gate',summary='Synthetic fixture gate only',status='succeeded',evidence_refs=['fixture://synthetic-independent-gate'],gate={'id':'independent-review','outcome':'Passed','subject_sha256':g.approval_subject_sha256(before,events),'decided_by':'synthetic-fixture','decided_at':stamp(),'authority_ref':'self-test://authority'})
    g.append_run_event(task,run_id=rid,attempt_id='A-1',event_type='run_finished',summary='Synthetic fixture engineering finish',status='succeeded',evidence_refs=['src/label.txt'])
    g.close_task(task,status='Implemented',established_facts=['Synthetic fixture label checked'],actual_changes=['Synthetic local label delivery'],verification=[{'result':'Passed','summary':'Exact local label bytes checked','evidence_refs':['src/label.txt']}],review_parent_task_id=parent)

def build_template(carrier):
    root=OUT/('template-'+carrier)
    if root.exists(): raise RuntimeError('preserve existing evidence: '+str(root))
    root.mkdir()
    (root/'src').mkdir(); (root/'src/label.txt').write_text('label=v1',encoding='utf-8')
    if carrier=='Full':
        task=new_task(root,'T-FULL',1); finish_full(task)
    else:
        path=minimal_fixture_record(root,'T-MIN'); task=path.parent
        rec=g.read_json(path)
        m.record_minimal_review(task,requirement_items=source_review(rec['task_contract']),reason='Synthetic fixture original-word review',basis='src/label.txt')
        for event,status in [('run_started','started'),('verification','succeeded')]:
            m.append_minimal_event(task,event_type=event,summary='Synthetic fixture: local label exact content observed',status=status,evidence_refs=['src/label.txt'])
        m.close_minimal_record(task,status='Implemented',established_facts=['Synthetic fixture label checked'],actual_changes=['Synthetic local label delivery'],verification=['Passed::Exact local label bytes checked::src/label.txt'])
    errors=g.validate_task_directory(task)
    if errors: raise RuntimeError(errors)
    return root,task

RESULTS=[]
def cli(script,args,label,expected_rc=0,expected=None):
    proc=subprocess.run([sys.executable,'-B','-X','utf8',str(SKILL/'scripts'/script),*map(str,args)],capture_output=True,text=True,encoding='utf-8',cwd=OUT)
    actual={'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
    okay=proc.returncode==expected_rc
    parsed=None
    if proc.returncode==0:
        try: parsed=json.loads(proc.stdout)
        except json.JSONDecodeError: pass
    if expected is not None: okay=okay and expected(parsed)
    result={'id':label,'input':{'script':script,'args':list(map(str,args))},'expected':{'returncode':expected_rc},'actual':actual,'result':'Passed' if okay else 'Failed'}
    RESULTS.append(result); save(OUT/'results.json',RESULTS)
    if not okay: print('FAILED',label,actual,flush=True)
    return parsed,proc

def fork(carrier,name):
    dest=OUT/('case-'+name+'-'+carrier)
    shutil.copytree(OUT/('template-'+carrier),dest)
    return dest/('.project-governance/tasks/T-FULL' if carrier=='Full' else '.project-governance/tasks/T-MIN')

def entry(task,record,label,expected_rc=0,expected=None):
    path=OUT/'inputs'/(label+'.json'); save(path,record)
    return cli('adversarial_review.py',[task,'--entry-json-file',path,'--reason','AR03 synthetic protocol case','--basis','ar03://'+label],label,expected_rc,expected)

def offer(task,label):
    return entry(task,{'event':'Offer','recorded_at':stamp(),'prompt':'工程结果已保存。是否启动多轮对抗性审查？选择开始、不需要或稍后。','evidence_ref':'ar03://synthetic-offer'},label,expected=lambda p:p['status']=='AwaitingUser')
def decision(task,outcome,label):
    return entry(task,{'event':'Decision','recorded_at':stamp(),'outcome':outcome,'response':{'Accepted':'开始审查','Declined':'不需要','Deferred':'稍后决定','Stopped':'停止审查'}[outcome],'decided_by':'synthetic-fixture','evidence_ref':'ar03://synthetic-response'},label,expected=lambda p:p['status']==('InProgress' if outcome=='Accepted' else outcome))
def round_record(task,label,**kwargs):
    delivery=kwargs.pop('delivery',task)
    _,_,out,contract,events=task_parts(delivery)
    parent=task_parts(task)[3]
    report=task/'evidence'/(label+'.md'); report.parent.mkdir(exist_ok=True); report.write_text('AR03 synthetic report '+label+'\nInput: local label; observed: label=v1.\n',encoding='utf-8')
    result={'event':'Round','recorded_at':stamp(),'round_id':label,'started_at':stamp(),'reviewer':'AR03 synthetic protocol case','delivery_task_id':delivery.name,'subject_sha256':g.user_decision_subject_sha256(contract,events,out),'requirements_sha256':ar.requirements_subject(parent),'report_ref':str(report),'coverage':'Complete','unreviewed_items':[],'evidence_refs':['src/label.txt'],'findings':[],'resolutions':[]}
    result['recorded_at']=stamp(); result.update(kwargs)
    return result

def state(task,label,expected): return cli('adversarial_review.py',[task],label,expected=expected)[0]

def core():
    for carrier in ['Full','Minimal']:
        root,task=build_template(carrier)
        print('template ready',carrier,flush=True)
        state(task,carrier+'-initial',lambda p:p['status']=='NotOffered' and p['clean_streak']==0)
        # The acceptance field is independently Pending. No decision can silently opt in.
        entry(task,round_record(task,carrier+'-unauthorized'),carrier+'-unauthorized',2)
        entry(task,{'event':'Decision','recorded_at':stamp(),'outcome':'Accepted','response':'开始审查','decided_by':'synthetic-fixture','evidence_ref':'ar03://response'},carrier+'-no-offer-decision',2)
        offer(task,carrier+'-offer'); entry(task,round_record(task,carrier+'-awaiting-round'),carrier+'-awaiting-round',2)
        decision(task,'Declined',carrier+'-decline'); entry(task,round_record(task,carrier+'-declined-round'),carrier+'-declined-round',2)
        decision(task,'Deferred',carrier+'-defer'); entry(task,round_record(task,carrier+'-deferred-round'),carrier+'-deferred-round',2)
        decision(task,'Accepted',carrier+'-accept')
        r=round_record(task,carrier+'-bad-clock',started_at='2026-01-01T00:00:00Z'); entry(task,r,carrier+'-precompletion-round',2)
        r=round_record(task,carrier+'-wrong-hash',subject_sha256='0'*64); entry(task,r,carrier+'-wrong-delivery-hash',2)
        r=round_record(task,carrier+'-wrong-requirements',requirements_sha256='0'*64); entry(task,r,carrier+'-wrong-requirements-hash',2)
        r=round_record(task,carrier+'-incomplete',coverage='Incomplete',unreviewed_items=['timeout path']); entry(task,r,carrier+'-incomplete',expected=lambda p:p['clean_streak']==0 and p['status']=='InProgress')
        entry(task,round_record(task,carrier+'-one'),carrier+'-one',expected=lambda p:p['clean_streak']==1 and p['status']=='InProgress')
        # New independent failure perspective: complete coverage plus an explicit unchecked item must still reset.
        entry(task,round_record(task,carrier+'-unchecked',unreviewed_items=['alternate carrier']),carrier+'-unchecked',expected=lambda p:p['clean_streak']==0)
        entry(task,round_record(task,carrier+'-finding',findings=[{'id':'AR03-I1','summary':'synthetic fixture issue','evidence_refs':['ar03://issue']}]),carrier+'-finding',expected=lambda p:p['clean_streak']==0 and p['open_findings']==['AR03-I1'])
        entry(task,round_record(task,carrier+'-unresolved'),carrier+'-unresolved',expected=lambda p:p['clean_streak']==0 and p['open_findings']==['AR03-I1'])
        entry(task,round_record(task,carrier+'-same-version-fix',resolutions=[{'finding_id':'AR03-I1','disposition':'Fixed','reason':'same artifact claimed fixed','evidence_refs':['ar03://wrong-fix']}]),carrier+'-same-version-fix',2)
        entry(task,round_record(task,carrier+'-notissue',resolutions=[{'finding_id':'AR03-I1','disposition':'NotAnIssue','reason':'actual output demonstrates the assumed issue is absent','evidence_refs':['src/label.txt']}]),carrier+'-notissue',expected=lambda p:p['clean_streak']==1 and not p['open_findings'])
        entry(task,{'event':'Blocked','recorded_at':stamp(),'reason':'synthetic fixture environment gap','evidence_refs':['ar03://gap']},carrier+'-blocked',expected=lambda p:p['clean_streak']==0 and p['status']=='Blocked')
        decision(task,'Stopped',carrier+'-stop'); entry(task,round_record(task,carrier+'-stopped-round'),carrier+'-stopped-round',2)
        decision(task,'Accepted',carrier+'-restart')
        r=round_record(task,carrier+'-clean-1'); entry(task,r,carrier+'-clean-1',expected=lambda p:p['clean_streak']==1)
        duplicate=round_record(task,carrier+'-copied-report'); Path(duplicate['report_ref']).write_bytes(Path(r['report_ref']).read_bytes()); entry(task,duplicate,carrier+'-copied-report',2)
        alias=round_record(task,carrier+'-report-alias'); alias['report_ref']=str(Path(r['report_ref']).parent/'../evidence'/Path(r['report_ref']).name); entry(task,alias,carrier+'-report-alias',2)
        second=round_record(task,carrier+'-clean-2'); entry(task,second,carrier+'-clean-2',expected=lambda p:p['clean_streak']==2 and p['status']=='Passed')
        entry(task,round_record(task,carrier+'-after-pass'),carrier+'-after-pass',2)
        # Independent unchanged source evidence may be shared by two distinct reports.
        cli('get_approval_subject.py',[task],carrier+'-approval-subject')
        cli('signals.py',['--project-root',root],carrier+'-signals',expected=lambda p:any(x['adversarial_review']['status']=='Passed' for x in p['task_progress']))
        # A modified report invalidates both the previous pair and its count, without deleting history.
        Path(second['report_ref']).write_text('AR03 changed report evidence\n',encoding='utf-8')
        state(task,carrier+'-report-mutated',lambda p:p['status']=='Stale' and p['clean_streak']==0)
        # A fresh post-Passed decision is required by prose; Stale continuation is expressly permitted by docs.
        entry(task,{'event':'Blocked','recorded_at':stamp(),'reason':'Actual report changed; checking its source before continuing','evidence_refs':['ar03://changed-report']},carrier+'-stale-block',expected=lambda p:p['status']=='Blocked' and p['clean_streak']==0)
    print('core complete',len(RESULTS),flush=True)

if __name__=='__main__':
    save(OUT/'run-metadata.json',{'started_at':stamp(),'session_start':'2026-10-23T11:47:54.835315Z','scope_commit':'11ecd2a3d05f51268ff51ed15cb0ab3cd7990648'})
    try: core()
    except Exception:
        (OUT/'exception.txt').write_text(traceback.format_exc(),encoding='utf-8'); raise
    finally: save(OUT/'results.json',RESULTS)
