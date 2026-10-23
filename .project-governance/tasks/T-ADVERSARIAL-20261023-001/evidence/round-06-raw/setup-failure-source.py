from __future__ import annotations
import sys, os, json, hashlib, copy, traceback, subprocess, inspect, shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta
sys.dont_write_bytecode=True
REPO=Path(r'D:/LFEN_project/dev_project/LFen-Skills')
SKILL=REPO/'skills/product-engineering/run-governed-product-workflow'
ARCHIVE=Path(__file__).resolve().parent
sys.path.insert(0,str(SKILL/'scripts'))
import governance_artifacts as ga
import minimal_task as mt
import adversarial_review as ar
import signals
CASES=[]
RAW=ARCHIVE/'raw'
RAW.mkdir(exist_ok=True)
SYN='synthetic-ar06://temp-only'

def jwrite(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')

def stamp(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')

def saved(task):
    if (task/'before.json').exists():
        p=task/'after.json'; o=ga.read_json(p); return p,o,ga.read_json(task/'before.json'),ga.read_jsonl(task/'run.jsonl')
    p=task/'task-record.json'; d=ga.read_json(p); return p,d['task_outcome'],mt.minimal_approval_contract(d),d['run_ledger']

def snapshot(task):
    return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in task.iterdir() if p.is_file()}

def calllog(kind,args,result):
    with (RAW/'api-events.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps({'at':stamp(),'kind':kind,'input':args,'output':result},ensure_ascii=False,default=str)+'\n')

def discharge(text):
    return [{'id':'R01','source':'request_snapshot','quote':text,'reading':'Synthetic isolated protocol fixture.','state':'Covered','evidence_refs':[SYN+'/requirement'],'acceptance_refs':[0], 'review':{'source_sha256':hashlib.sha256(text.encode()).hexdigest(),'conditions':[],'cases':[{'condition':None,'branch':'Unconditional','input':'Synthetic local label','expected':'Synthetic local label validated','actual':'Synthetic local label validated','result':'Passed','evidence_refs':[SYN+'/requirement-case']}]}}]

def create(root,tid,carrier='Full',parent=None,finish=True,project='P-AR06'):
    root.mkdir(parents=True,exist_ok=True)
    (root/'survey.md').write_text('Synthetic AR-06 Temp fixture, no real human authorization.\n',encoding='utf-8')
    text='Update the synthetic local label.'
    clarification={'state':'Settled','mode':'Skipped','notice':'Synthetic fixture is explicit; question round skipped.','survey_refs':['survey.md'],'rounds':[],'basis':'Synthetic isolated local fixture.','reopened_by':[]}
    decisions=[{'id':'D01','kind':'Proceed','presented':'Synthetic Temp-only label scope','response':'SYNTHETIC proceed','decided_by':'synthetic-test-actor','decided_at':stamp(),'outcome':'Approved','evidence_ref':SYN+'/proceed'}]
    common={'project_id':project,'work_item_id':'W-'+tid,'task_id':tid,'ordinal':1,'objective':text,'request_snapshot':{'language':'en','text':text,'captured_at':stamp(),'source':SYN+'/request'},'clarification':clarification,'requirement_items':discharge(text),'decisions':decisions,'depends_on':[parent] if parent else []}
    if carrier=='Minimal':
        path=mt.create_minimal_record(root,**common,supersedes=[],scope='Synthetic local label',acceptance='Synthetic label check passes',delivery_scenario='DS-03',development_type='DT-08',change_surface='UI/UX',selected_approach='Edit synthetic label',alternative_rejected='Leave synthetic label unchanged',plan_steps=['Edit synthetic label'],verification='Run synthetic check',rollback='Restore synthetic label',allowed_paths=['label.txt'],out_of_scope=['All real files'],forbidden_actions=['External side effects'],selection_source='automatic',basis=['Synthetic isolated fixture'],authority_refs=[SYN+'/authority'],eligibility_evidence_refs=[SYN+'/'+x for x in ['low','reversible','single','noexternal','noprod','nosecurity','noextension']],facts=['Synthetic label exists'],constraints=['Temp only'],assumptions=['Synthetic input only'],fundamentals=['A label is a value','The edit is reversible'],causal_chain=['Changing label enables synthetic check'],decision_criteria=['Synthetic check passes'])
        task=path.parent
        mt.append_minimal_event(task,event_type='run_started',summary='Synthetic fixture starts',status='started')
        mt.append_minimal_event(task,event_type='verification',summary='Synthetic fixture verified',status='succeeded',evidence_refs=[SYN+'/verified/'+tid])
        if finish:
            mt.close_minimal_record(task,status='Implemented',established_facts=['Synthetic verified fixture'],actual_changes=['Synthetic label'],verification=['Passed::Synthetic fixture check::'+SYN+'/verified/'+tid],review_parent_task_id=parent)
    else:
        facts={key:'No' for key in ['product_intent_change','initiative_scope_change','requirement_change','external_behavior_change','design_change','architecture_impact','security_privacy_impact','data_ai_impact','formal_knowledge_records','operations_impact','production_release','irreversible_change','migration_retirement','external_system_effect','formal_review_or_gate']}
        facts.update(actual_execution='Yes',authority_available='Yes')
        task=ga.initialize_task(root,**common,acceptance=['Synthetic label check passes'],development_types=['DT-08'],primary_development_type='DT-08',change_surfaces=['UI/UX'],delivery_scenario='DS-03',risk_level='Low',baseline_inheritance=['New'],in_scope=['Synthetic local label'],out_of_scope=['All real files'],allowed_paths=[str(root)],forbidden_actions=['External side effects'],extension_triggers={k:'Inactive' for k in ['E01','E02','E03','E04','E05']},extension_evidence_refs={k:[] for k in ['E01','E02','E03','E04','E05']},applicability_facts=facts,tailoring_stage='S4',required_gates=[],authority_references=[SYN+'/authority'],authority_assessments=[{'reference':SYN+'/authority','source_kind':'Policy','status':'Valid','scope_refs':['Synthetic local label'],'evidence_refs':[SYN+'/authority-source'],'verified_at':stamp(),'expires_at':None}],basis=['Synthetic isolated fixture'],source_snapshot={'kind':'synthetic-ar06','version':tid})
        for kind,status in [('run_started','started'),('verification','succeeded')]:
            ga.append_run_event(task,run_id=tid+'-run',attempt_id='A01',event_type=kind,status=status,summary='Synthetic fixture '+kind,evidence_refs=[SYN+'/verified/'+tid] if kind=='verification' else [])
        if finish:
            ga.append_run_event(task,run_id=tid+'-run',attempt_id='A01',event_type='run_finished',status='succeeded',summary='Synthetic fixture complete')
            ga.close_task(task,status='Implemented',established_facts=['Synthetic verified fixture'],actual_changes=['Synthetic label'],verification=[{'result':'Passed','summary':'Synthetic fixture check','evidence_refs':[SYN+'/verified/'+tid]}],review_parent_task_id=parent)
    calllog('create',{'root':root,'task':tid,'carrier':carrier,'parent':parent,'finish':finish},str(task))
    return task

def write_entry(task,entry):
    calllog('append_review',{'task':str(task),'entry':entry},'attempt')
    return str(ar.append_review(task,entry,reason='Synthetic independent AR-06 case',basis=SYN+'/case'))

def offer(task): return {'event':'Offer','recorded_at':stamp(),'prompt':'SYNTHETIC: engineering verified and saved. Start review?','evidence_ref':SYN+'/offer'}
def decision(outcome='Accepted'): return {'event':'Decision','recorded_at':stamp(),'outcome':outcome,'response':'SYNTHETIC '+outcome,'decided_by':'synthetic-test-actor','evidence_ref':SYN+'/decision'}
def authorize(task):
    write_entry(task,offer(task)); write_entry(task,decision())

def roundentry(task,rid,*,delivery=None,coverage='Complete',unreviewed=None,findings=None,resolutions=None,report_content=None):
    delivery=delivery or task
    _,out,contract,events=saved(delivery)
    _,_,original,_=saved(task)
    start=stamp()
    rp=task/'evidence'/('synthetic-'+rid+'.md'); rp.parent.mkdir(exist_ok=True)
    rp.write_text(report_content or f'Synthetic independent AR-06 report {task.name} {rid}; Temp-only fixture.\n',encoding='utf-8')
    return {'event':'Round','round_id':rid,'recorded_at':stamp(),'started_at':start,'reviewer':'synthetic-ar06-reviewer','delivery_task_id':delivery.name,'subject_sha256':ga.user_decision_subject_sha256(contract,events,out),'requirements_sha256':ar.requirements_subject(original),'report_ref':str(rp),'coverage':coverage,'unreviewed_items':unreviewed or [],'evidence_refs':[SYN+'/round/'+rid],'findings':findings or [],'resolutions':resolutions or []}

def case(cid,condition,inputs,expected,operation,check):
    try:
        value=operation()
        actual={'accepted':True,'value':value}
    except Exception as e:
        actual={'accepted':False,'exception':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
    try: passed=bool(check(actual))
    except Exception: passed=False
    data={'id':cid,'condition':condition,'input':inputs,'expected':expected,'actual':actual,'result':'Passed' if passed else 'Failed','evidence_refs':['raw/'+cid+'.json']}
    jwrite(RAW/(cid+'.json'),data)
    CASES.append(data)
    jwrite(ARCHIVE/'cases.json',CASES)
    print(cid,data['result'],json.dumps(actual,ensure_ascii=False,default=str)[:500],flush=True)
    return actual

reject=lambda a: not a['accepted'] and a.get('exception')=='GovernanceError'
accept=lambda a:a['accepted']

if __name__=='__main__':
    full=create(ARCHIVE/'fixtures'/'full','T-FULL')
    mini=create(ARCHIVE/'fixtures'/'minimal','T-MIN','Minimal')
    print('setup',ga.validate_task_directory(full),ga.validate_task_directory(mini))
    print('state',ar.review_status(full),ar.review_status(mini))
