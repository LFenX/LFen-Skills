from __future__ import annotations
import sys, os, pathlib, json, hashlib, subprocess, copy, traceback, time
from datetime import datetime, timezone, timedelta
BASE=pathlib.Path(r'C:\Users\Administrator\AppData\Local\Temp\lfen_ar04_27cb1b45821e4e74b8ab7bd882dd0857')
REPO=pathlib.Path(r'D:\LFEN_project\dev_project\LFen-Skills')
SKILL=REPO/'skills/product-engineering/run-governed-product-workflow'
SCRIPTS=SKILL/'scripts'
sys.path.insert(0,str(SCRIPTS)); sys.dont_write_bytecode=True
import governance_artifacts as g
import minimal_task as m
import adversarial_review as a
from self_test import new_task, minimal_fixture_record
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','GIT_OPTIONAL_LOCKS':'0'}
CASES=[]; RAW=BASE/'raw'; RAW.mkdir(exist_ok=True)
FIX=BASE/'fixtures'; FIX.mkdir(exist_ok=True)
COUNTER=0

def now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def write(p,x): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); return p
def cli(script,args,label,*,skill=SKILL):
    global COUNTER
    COUNTER+=1
    cmd=[sys.executable,'-B','-X','utf8',str(skill/'scripts'/script),*map(str,args)]
    r=subprocess.run(cmd,cwd=BASE,capture_output=True,text=True,encoding='utf-8',env=ENV,timeout=45)
    path=RAW/f'{COUNTER:04d}-{label}.json'
    raw={'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'finished_at':now()}
    write(path,raw)
    try: result=json.loads(r.stdout)
    except ValueError: result=None
    return raw,result,path

def check(label,raw,expected,actual,ok,input_value=None,ref=None):
    c={'id':f'C{len(CASES)+1:03d}','name':label,'input':input_value,'expected':expected,'actual':actual,'result':'Passed' if ok else 'Failed','evidence_refs':[str(ref)] if ref else []}
    CASES.append(c); write(BASE/'cases.json',CASES)
    if not ok: print(json.dumps(c,ensure_ascii=False),flush=True)
    return c

def outcome_path(t): return t/('after.json' if (t/'before.json').exists() else 'task-record.json')
def read_outcome(t):
    d=g.read_json(outcome_path(t)); return d if (t/'before.json').exists() else d['task_outcome']

def state(t,label='binding',skill=SKILL):
    raw,res,p=cli('adversarial_review.py',[t],label,skill=skill)
    return raw,res,p

def query(t,label,expected,skill=SKILL):
    raw,res,p=state(t,label,skill)
    ok=raw['exit_code']==0 and res is not None and all(res.get(k)==v for k,v in expected.items())
    check(label,raw,{'exit_code':0,**expected},res if res is not None else raw,ok,{'task':str(t),'operation':'status'},p)
    return res

def entry(t,label,value,expected_rc=0,expected=None,skill=SKILL):
    ip=write(BASE/'inputs'/f'{label}.json',value)
    pth=outcome_path(t); before=pth.read_bytes() if pth.exists() else None
    raw,res,p=cli('adversarial_review.py',[t,'--entry-json-file',ip,'--reason','Independent synthetic protocol check','--basis','ar04://isolated-fixture'],label,skill=skill)
    unchanged=not pth.exists() if before is None else pth.read_bytes()==before
    ok=raw['exit_code']==expected_rc and (expected_rc==0 or unchanged)
    if expected is not None: ok=ok and res is not None and all(res.get(k)==v for k,v in expected.items())
    check(label,raw,{'exit_code':expected_rc,**(expected or {}),**({'unchanged_after_rejection':True} if expected_rc else {})}, {'exit_code':raw['exit_code'],'state':res,'stderr':raw['stderr'],'unchanged':unchanged},ok,value,p)
    return res

def offer(t,label,**kw): return entry(t,label,{'event':'Offer','recorded_at':now(),'prompt':'Synthetic: completed delivery saved. Start multi-round adversarial review?','evidence_ref':'ar04://synthetic-post-completion-offer'},**kw)
def decision(t,label,outcome='Accepted',**kw): return entry(t,label,{'event':'Decision','recorded_at':now(),'outcome':outcome,'response':'Synthetic explicit '+outcome,'decided_by':'synthetic-user','evidence_ref':'ar04://synthetic-answer'},**kw)
def round_value(t,label,delivery=None,**changes):
    delivery=delivery or t
    _,ds,_=state(delivery,label+'-delivery-bind'); _,ps,_=state(t,label+'-requirements-bind')
    report=t/'evidence'/f'{label}.md'; report.parent.mkdir(exist_ok=True); report.write_text('# Independent synthetic protocol report\n'+label+'\n',encoding='utf-8')
    v={'event':'Round','recorded_at':now(),'round_id':label,'started_at':now(),'reviewer':'ar04-synthetic-'+label,'delivery_task_id':delivery.name,'subject_sha256':ds['subject_sha256'],'requirements_sha256':ps['requirements_sha256'],'report_ref':str(report),'coverage':'Complete','unreviewed_items':[],'evidence_refs':['ar04://case-'+label],'findings':[],'resolutions':[]}
    v['recorded_at']=now(); v.update(changes); return v

def discharge(contract):
    items=copy.deepcopy(contract['requirement_items'])
    for x in items:
        x['review']={'source_sha256':hashlib.sha256(contract['request_snapshot']['text'].encode()).hexdigest(),'conditions':[],'cases':[{'condition':None,'branch':'Unconditional','input':'Synthetic lifecycle plumbing','expected':'Synthetic fixture initialized','actual':'Synthetic fixture initialized','result':'Passed','evidence_refs':['ar04://synthetic-fixture']} ]}
    return items

def fresh(carrier,name,root=None,complete=True,parent=None,status='Implemented'):
    root=root or FIX/name; root.mkdir(exist_ok=True,parents=True); tid='T-'+name.upper().replace('_','-')
    t=root/'.project-governance/tasks'/tid
    if carrier=='Full':
        new_task(root,tid,1,depends_on=[parent.name] if parent else [])
        b=g.read_json(t/'before.json'); b['authority']['required_gates']=[]; b['decisions']=[x for x in b['decisions'] if x['kind']=='Proceed']; b['requirement_items']=discharge(b); g.atomic_write_json(t/'before.json',b)
    else:
        p=minimal_fixture_record(root,tid); b=g.read_json(p); b['depends_on']=[parent.name] if parent else []; b['task_contract']['decisions']=[x for x in b['task_contract']['decisions'] if x['kind']=='Proceed']; b['task_contract']['requirement_items']=discharge(b['task_contract']); g.atomic_write_json(p,b)
    if complete: finish(carrier,t,parent=parent,status=status)
    return t

def finish(carrier,t,parent=None,status='Implemented',expected_rc=0,label=None):
    if carrier=='Full':
        g.append_run_event(t,run_id='RUN-AR04',attempt_id='A01',event_type='run_started',summary='Synthetic work',status='started')
        g.append_run_event(t,run_id='RUN-AR04',attempt_id='A01',event_type='verification',summary='Synthetic verified current delivery',status='succeeded',evidence_refs=['ar04://verified-'+t.name])
        g.append_run_event(t,run_id='RUN-AR04',attempt_id='A01',event_type='run_finished',summary='Synthetic finish',status='succeeded')
        args=[t,'--status',status,'--fact','Synthetic complete','--change','Synthetic local change','--verification','Passed::Synthetic check::ar04://verified-'+t.name]
        script='close_task.py'
    else:
        m.append_minimal_event(t,event_type='run_started',summary='Synthetic work',status='started'); m.append_minimal_event(t,event_type='verification',summary='Synthetic verified current delivery',status='succeeded',evidence_refs=['ar04://verified-'+t.name])
        args=['close',t,'--status',status,'--fact','Synthetic complete','--change','Synthetic local change','--verification','Passed::Synthetic check::ar04://verified-'+t.name]; script='manage_minimal_task.py'
    if parent: args+=['--review-parent-task-id',parent.name]
    raw,res,p=cli(script,args,label or t.name+'-close')
    if label: check(label,raw,{'exit_code':expected_rc},{'exit_code':raw['exit_code'],'stdout':raw['stdout'],'stderr':raw['stderr']},raw['exit_code']==expected_rc,{'task':str(t),'parent':str(parent) if parent else None,'status':status},p)
    elif raw['exit_code']!=0: raise RuntimeError(raw)
    return raw

def suite(carrier):
    tag=carrier.lower()
    t=fresh(carrier,tag+'_unsaved',complete=False)
    offer(t,tag+'-offer-before-save',expected_rc=2)
    t=fresh(carrier,tag+'_basic')
    query(t,tag+'-new-state',{'status':'NotOffered','clean_streak':0})
    o=read_outcome(t)
    check(tag+'-user-decision-pending',None,{'outcome':'Pending'},o['user_decision'],o['user_decision']=={'outcome':'Pending'},ref=outcome_path(t))
    decision(t,tag+'-decision-without-question',expected_rc=2)
    entry(t,tag+'-round-without-optin',round_value(t,tag+'-round-no-auth'),expected_rc=2)
    offer(t,tag+'-offer',expected={'status':'AwaitingUser'})
    entry(t,tag+'-round-awaiting-answer',round_value(t,tag+'-awaiting'),expected_rc=2)
    decision(t,tag+'-decline',outcome='Declined',expected={'status':'Declined'})
    entry(t,tag+'-round-declined',round_value(t,tag+'-declined-round'),expected_rc=2)
    decision(t,tag+'-defer',outcome='Deferred',expected={'status':'Deferred'})
    entry(t,tag+'-round-deferred',round_value(t,tag+'-deferred-round'),expected_rc=2)
    decision(t,tag+'-late-start',expected={'status':'InProgress'})
    offer(t,tag+'-offer-while-active',expected_rc=2)
    decision(t,tag+'-reaccept-while-active',expected_rc=2)
    v=round_value(t,tag+'-first-clean'); entry(t,tag+'-first-clean',v,expected={'status':'InProgress','clean_streak':1})
    duplicate=round_value(t,tag+'-id-reuse',round_id=v['round_id']); entry(t,tag+'-duplicate-id',duplicate,expected_rc=2)
    copied=round_value(t,tag+'-copied-report'); pathlib.Path(copied['report_ref']).write_bytes(pathlib.Path(v['report_ref']).read_bytes()); entry(t,tag+'-same-report-copy',copied,expected_rc=2)
    alias=round_value(t,tag+'-alias',report_ref=str(t/'evidence'/'..'/'evidence'/pathlib.Path(v['report_ref']).name)); entry(t,tag+'-same-report-alias',alias,expected_rc=2)
    oldreport=pathlib.Path(v['report_ref']); oldbytes=oldreport.read_bytes(); oldreport.write_text('changed old report content\n',encoding='utf-8')
    query(t,tag+'-report-edited-stale',{'status':'Stale','clean_streak':0})
    oldreport.unlink(); query(t,tag+'-report-deleted-stale',{'status':'Stale','clean_streak':0})
    resurrect=round_value(t,tag+'-old-content-resurrect'); pathlib.Path(resurrect['report_ref']).write_bytes(oldbytes); entry(t,tag+'-historic-report-copy-rejected',resurrect,expected_rc=2)
    entry(t,tag+'-clean-after-stale',round_value(t,tag+'-poststale-one'),expected={'status':'InProgress','clean_streak':1})
    entry(t,tag+'-second-clean',round_value(t,tag+'-poststale-two'),expected={'status':'Passed','clean_streak':2})
    entry(t,tag+'-round-after-passed',round_value(t,tag+'-extra-round'),expected_rc=2)
    # Explicit new decision, including after a completed session, is required.
    decision(t,tag+'-restart-after-passed',expected={'status':'InProgress','clean_streak':0})
    decision(t,tag+'-stop',outcome='Stopped',expected={'status':'Stopped','clean_streak':0})
    entry(t,tag+'-round-after-stopped',round_value(t,tag+'-stopped-round'),expected_rc=2)
    decision(t,tag+'-restart-after-stop',expected={'status':'InProgress','clean_streak':0})
    query(t,tag+'-decision-independent',{'status':'InProgress'})
    # Findings, coverage and blocking all interrupt consecutive clean rounds.
    t=fresh(carrier,tag+'_findings'); offer(t,tag+'-find-offer'); decision(t,tag+'-find-start')
    entry(t,tag+'-find-clean-one',round_value(t,tag+'-find-clean-one'),expected={'clean_streak':1})
    finding={'id':'AR04-'+tag+'-F1','summary':'Synthetic confirmed finding','evidence_refs':['ar04://finding']}
    entry(t,tag+'-finding-resets',round_value(t,tag+'-finding',findings=[finding]),expected={'clean_streak':0,'open_findings':[finding['id']]})
    entry(t,tag+'-unresolved-prevents-clean',round_value(t,tag+'-open-finding'),expected={'clean_streak':0})
    resolution={'finding_id':finding['id'],'disposition':'Fixed','reason':'Synthetic same version is not a fix','evidence_refs':['ar04://resolution']}
    entry(t,tag+'-same-version-fix-rejected',round_value(t,tag+'-samefix',resolutions=[resolution]),expected_rc=2)
    entry(t,tag+'-finding-id-not-reusable',round_value(t,tag+'-dupfind',findings=[finding]),expected_rc=2)
    unknown={**resolution,'finding_id':'absent'}; entry(t,tag+'-unknown-resolution',round_value(t,tag+'-unknown',resolutions=[unknown]),expected_rc=2)
    resolution={**resolution,'disposition':'NotAnIssue','reason':'Synthetic evidence disproves finding'}
    entry(t,tag+'-evidenced-false-positive',round_value(t,tag+'-notanissue',resolutions=[resolution]),expected={'clean_streak':1,'open_findings':[]})
    entry(t,tag+'-unreviewed-resets',round_value(t,tag+'-unreviewed',unreviewed_items=['condition not checked']),expected={'clean_streak':0})
    entry(t,tag+'-incomplete-resets',round_value(t,tag+'-incomplete',coverage='Incomplete'),expected={'clean_streak':0})
    entry(t,tag+'-blocked-resets',{'event':'Blocked','recorded_at':now(),'reason':'Synthetic missing environment','evidence_refs':['ar04://blocked']},expected={'status':'Blocked','clean_streak':0})
    entry(t,tag+'-resume-one',round_value(t,tag+'-resume-one'),expected={'clean_streak':1})
    entry(t,tag+'-resume-two',round_value(t,tag+'-resume-two'),expected={'status':'Passed','clean_streak':2})
    # Malformed, wrong version and chronology inputs must be rejected unchanged.
    t=fresh(carrier,tag+'_validation'); offer(t,tag+'-val-offer'); decision(t,tag+'-val-start')
    for name,change in [('wrong-subject',{'subject_sha256':'0'*64}),('wrong-original',{'requirements_sha256':'0'*64}),('future-start',{'started_at':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}),('before-delivery',{'started_at':'2020-01-01T00:00:00Z'}),('naive-record',{'recorded_at':'2026-10-23T10:00:00'}),('claim-passed',{'status':'Passed'}),('claim-streak',{'clean_streak':2})]:
        entry(t,tag+'-'+name,round_value(t,tag+'-'+name,**change),expected_rc=2)
    out=BASE/'outside-report.md'; out.write_text('outside',encoding='utf-8'); entry(t,tag+'-outside-report',round_value(t,tag+'-outside',report_ref=str(out)),expected_rc=2)
    v=round_value(t,tag+'-empty-report'); pathlib.Path(v['report_ref']).write_text(' \n',encoding='utf-8'); entry(t,tag+'-empty-report',v,expected_rc=2)
    # Repair lineage, new verified deliveries and resumed review.
    root=FIX/(tag+'_repairs'); p=fresh(carrier,tag+'_parent',root=root); offer(p,tag+'-parent-offer'); decision(p,tag+'-parent-start')
    finding={'id':'AR04-'+tag+'-REPAIR','summary':'Synthetic issue needs repair','evidence_refs':['ar04://repair']}
    entry(p,tag+'-parent-finding',round_value(p,tag+'-parent-finding',findings=[finding]),expected={'clean_streak':0})
    child=fresh(carrier,tag+'_repair',root=root,parent=p)
    query(child,tag+'-repair-managed',{'status':'ManagedByParent','parent_task_id':p.name})
    query(p,tag+'-repair-invalidates-parent',{'status':'Stale','clean_streak':0})
    offer(child,tag+'-no-recursive-repair-offer',expected_rc=2)
    entry(p,tag+'-old-delivery-after-repair',round_value(p,tag+'-old-delivery-after-repair'),expected_rc=2)
    entry(p,tag+'-repair-preclose-time',round_value(p,tag+'-repair-early',delivery=child,started_at=read_outcome(p)['completed_at']),expected_rc=2)
    fix={'finding_id':finding['id'],'disposition':'Fixed','reason':'Synthetic repair verified on new saved delivery','evidence_refs':['ar04://reverified']}
    entry(p,tag+'-repair-round-one',round_value(p,tag+'-repair-one',delivery=child,resolutions=[fix]),expected={'status':'InProgress','clean_streak':1,'open_findings':[]})
    entry(p,tag+'-repair-round-two',round_value(p,tag+'-repair-two',delivery=child),expected={'status':'Passed','clean_streak':2})
    c=fresh(carrier,tag+'_postpass_child',root=root,complete=False,parent=p); finish(carrier,c,parent=p,expected_rc=2,label=tag+'-repair-rejected-after-pass')
    # A stop revokes repair association until a real new Accepted decision.
    root=FIX/(tag+'_stops'); p=fresh(carrier,tag+'_stop_parent',root=root); offer(p,tag+'-stop-parent-offer'); decision(p,tag+'-stop-parent-start'); decision(p,tag+'-stop-parent-stop',outcome='Stopped')
    c=fresh(carrier,tag+'_stop_child',root=root,complete=False,parent=p); finish(carrier,c,parent=p,expected_rc=2,label=tag+'-repair-rejected-after-stop')
    # Signals and generated review Markdown consume the actual computed state.
    raw,res,rp=cli('signals.py',['--project-root',t.parents[2]],tag+'-signals')
    prog=next((x for x in (res or {}).get('task_progress',[]) if x['task_id']==t.name),{})
    check(tag+'-signals-computed',raw,{'status':'InProgress'},prog,raw['exit_code']==0 and prog.get('adversarial_review',{}).get('status')=='InProgress',{'task':str(t)},rp)
    pid='P-TEST' if carrier=='Full' else 'P-MIN'
    raw,res,rp=cli('generate_review_views.py',['--project-root',t.parents[2],'--project-id',pid],tag+'-generate-views')
    candidates=list((t.parents[2]/'.project-governance/generated').rglob('*.md'))
    matching=[str(x) for x in candidates if 'Adversarial review:' in x.read_text(encoding='utf-8') and 'InProgress' in x.read_text(encoding='utf-8')]
    check(tag+'-review-markdown',raw,{'exit_code':0,'contains_computed_review':True},{'exit_code':raw['exit_code'],'matching_files':matching,'stderr':raw['stderr']},raw['exit_code']==0 and bool(matching),{'root':str(t.parents[2])},rp)
    return t

if __name__=='__main__':
    write(BASE/'harness-start.json',{'at':now(),'note':'All fixtures are synthetic. No actual reviews or human decisions are asserted by fixture data.'})
    for carrier in ['Full','Minimal']:
        try: suite(carrier)
        except Exception: write(BASE/f'{carrier}-harness-error.json',{'error':traceback.format_exc()}); print(traceback.format_exc(),flush=True)
    write(BASE/'harness-summary.json',{'at':now(),'case_count':len(CASES),'passed':sum(x['result']=='Passed' for x in CASES),'failed':[x for x in CASES if x['result']=='Failed']})
    print(json.dumps({'case_count':len(CASES),'passed':sum(x['result']=='Passed' for x in CASES),'failed':sum(x['result']=='Failed' for x in CASES)},ensure_ascii=False))
