from __future__ import annotations
import sys, os, json, copy, hashlib, subprocess, traceback, inspect
from pathlib import Path
from datetime import datetime, timezone, timedelta
sys.dont_write_bytecode = True
REPO = Path(r'D:/LFEN_project/dev_project/LFen-Skills')
TEMP = Path(__file__).parent
SCRIPTS = REPO/'skills/product-engineering/run-governed-product-workflow/scripts'
sys.path.insert(0,str(SCRIPTS))
import governance_artifacts as g
import minimal_task as m
import adversarial_review as ar
import signals
LOG = TEMP/'raw-phase1'; LOG.mkdir(exist_ok=True)
CASES=[]; CALLS=[]; FIXTURES=[]
def now(): return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def dump(path,value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save():
    dump(TEMP/'cases.json',CASES); dump(TEMP/'commands.json',CALLS); dump(TEMP/'fixtures.json',FIXTURES)
def check(name,condition,input_value,expected,actual,evidence,passed):
    value={'id':f'AR05-C{len(CASES)+1:03}','name':name,'condition':condition,'input':input_value,'expected':expected,'actual':actual,'evidence':evidence,'result':'Passed' if passed else 'Failed'}
    CASES.append(value); save(); print(value['id'],value['result'],name,flush=True); return value

def api(label, fn, *, expect_error=False):
    stem=f'{len(CALLS)+1:03}-{label}'; started=now()
    try:
        value=fn(); actual={'return':str(value)}; ok=not expect_error
    except Exception as exc:
        actual={'exception':type(exc).__name__,'message':str(exc),'traceback':traceback.format_exc()}; ok=expect_error
    p=LOG/(stem+'.json'); dump(p,{'method':'minimal API call','label':label,'started_at':started,'ended_at':now(),'actual':actual})
    CALLS.append({'label':label,'method':'API','evidence':str(p)}); save()
    return actual,ok,str(p)

def cli(script,args,label):
    stem=f'{len(CALLS)+1:03}-{label}'; command=[sys.executable,'-B','-X','utf8',str(SCRIPTS/script),*map(str,args)]
    started=now(); proc=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    p=LOG/(stem+'.json'); dump(p,{'command':command,'cwd':str(TEMP),'started_at':started,'ended_at':now(),'exit_code':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
    CALLS.append({'label':label,'method':'CLI','evidence':str(p)});save()
    try: value=json.loads(proc.stdout)
    except: value=None
    return proc,value,str(p)

FACT_KEYS=('product_intent_change','initiative_scope_change','requirement_change','external_behavior_change','design_change','architecture_impact','security_privacy_impact','data_ai_impact','formal_knowledge_records','operations_impact','production_release','irreversible_change','migration_retirement','external_system_effect','formal_review_or_gate')

class Fixture:
    def __init__(self,name,carrier,*,root=None,parent=None,complete=True):
        self.carrier=carrier; self.root=root or TEMP/'fixtures'/'attempt5'/name; self.root.mkdir(parents=True,exist_ok=True)
        self.task_id='T-'+name.upper(); self.task=self.root/'.project-governance/tasks'/self.task_id
        request=f'Change the local label for synthetic {name}.'
        (self.root/'surveyed.md').write_text('AR05 synthetic fixture survey: local reversible label only.\n',encoding='utf-8')
        self.request=request
        review={'source_sha256':hashlib.sha256(request.encode()).hexdigest(),'conditions':[],'cases':[{'condition':None,'branch':'Unconditional','input':'AR05 synthetic fixture only','expected':'label exists','actual':'label exists','result':'Passed','evidence_refs':['ar05-fixture://synthetic-label-check']}]}
        requirements=[{'id':'R-01','source':'request_snapshot','quote':request,'reading':'Update this one local fixture label.','state':'Covered','evidence_refs':['ar05-fixture://synthetic-label-check'],'acceptance_refs':[0],'review':review}]
        clarification={'state':'Settled','mode':'Skipped','notice':'This synthetic fixture has one declared local label.','survey_refs':['surveyed.md'],'rounds':[],'basis':'AR05 synthetic test data, not a human decision on the actual task.','reopened_by':[]}
        decisions=[{'id':'D-PROCEED','kind':'Proceed','presented':'AR05 synthetic fixture scope and acceptance','response':'Proceed (synthetic)','decided_by':'AR05 fixture actor','decided_at':now(),'outcome':'Approved','evidence_ref':'ar05-fixture://synthetic-proceed'}]
        common={'project_id':'P-AR05','work_item_id':'W-'+self.task_id,'task_id':self.task_id,'ordinal':1,'objective':request,'request_snapshot':{'language':'en','text':request,'captured_at':now()},'requirement_items':requirements,'decisions':decisions,'clarification':clarification,'depends_on':[parent] if parent else [],'allowed_paths':[str(self.root)],'out_of_scope':['External services'],'forbidden_actions':['external mutation'],'basis':['AR05 synthetic fixture only']}
        if carrier=='Full':
            self.path=g.initialize_task(self.root,**common,acceptance=['The fixture label is valid.'],development_types=['DT-08'],development_type_scopes={'DT-08':['One local label.']},in_scope=['One local label.'],change_surfaces=['UI/UX'],baseline_inheritance=['New'],extension_triggers={f'E{i:02}':'Inactive' for i in range(1,6)},extension_evidence_refs={f'E{i:02}':[] for i in range(1,6)},applicability_facts={**{k:'No' for k in FACT_KEYS},'actual_execution':'Yes','authority_available':'Yes'},tailoring_stage='S4',required_gates=[],authority_references=['ar05-fixture://authority'],authority_assessments=[{'reference':'ar05-fixture://authority','source_kind':'Policy','status':'Valid','scope_refs':['One local label.'],'evidence_refs':['ar05-fixture://authority'],'verified_at':now(),'expires_at':None}],source_snapshot={'kind':'AR05 fixture','name':name})
            self.path=self.task/'after.json'
        else:
            m.create_minimal_record(self.root,**common,supersedes=[],scope='One local label.',acceptance='The fixture label is valid.',delivery_scenario='DS-03',development_type='DT-08',change_surface='UI/UX',selected_approach='Edit the label.',alternative_rejected='Keep the prior value.',plan_steps=['Edit one label.'],verification='Check the label.',rollback='Restore the label.',selection_source='automatic',authority_refs=['ar05-fixture://authority'],eligibility_evidence_refs=[f'ar05-fixture://{v}' for v in ['low','reversible','single','local','no-production','no-security','no-extensions']],facts=['One local text file.'],constraints=['Local temporary fixture only.'],assumptions=[],fundamentals=['The label is local.','The edit is reversible.'],causal_chain=['One edit updates one label.'],decision_criteria=['The label check passes.'])
            self.path=self.task/'task-record.json'
        FIXTURES.append({'name':name,'carrier':carrier,'root':str(self.root),'task_dir':str(self.task),'synthetic_human_decisions':True});save()
        if complete: self.finish(parent)
    def finish(self,parent=None):
        if self.carrier=='Full':
            for kind,status in [('run_started','started'),('verification','succeeded'),('run_finished','succeeded')]:
                g.append_run_event(self.task,run_id='RUN-AR05',attempt_id='A01',event_type=kind,status=status,summary='AR05 synthetic '+kind,evidence_refs=['ar05-fixture://verification'] if kind=='verification' else [])
            g.close_task(self.task,status='Implemented',established_facts=['Synthetic fixture complete.'],actual_changes=['Synthetic label edit.'],verification=[{'result':'Passed','summary':'AR05 synthetic label check','evidence_refs':['ar05-fixture://verification']}],review_parent_task_id=parent)
        else:
            for kind,status in [('run_started','started'),('verification','succeeded')]:
                m.append_minimal_event(self.task,event_type=kind,status=status,summary='AR05 synthetic '+kind,evidence_refs=['ar05-fixture://verification'] if kind=='verification' else [])
            m.close_minimal_record(self.task,status='Implemented',established_facts=['Synthetic fixture complete.'],actual_changes=['Synthetic label edit.'],verification=['Passed::AR05 synthetic label check::ar05-fixture://verification'],review_parent_task_id=parent)
    def data(self):
        d=g.read_json(self.path)
        return d, d if self.carrier=='Full' else d['task_outcome']
    def contract(self):
        return g.read_json(self.task/'before.json') if self.carrier=='Full' else m.minimal_approval_contract(self.data()[0])
    def status(self,label=None):
        p,v,e=cli('adversarial_review.py',[self.task],label or self.task_id+'-status')
        return p,v,e
    def entry(self,entry,label,expected_status=None,error=False):
        e=copy.deepcopy(entry);e.setdefault('recorded_at',now())
        inp=TEMP/'inputs'/(f'{len(CALLS)+1:03}-{label}.json');dump(inp,e)
        before=sha(self.path) if self.path.exists() else None
        p,v,ev=cli('adversarial_review.py',[self.task,'--entry-json-file',inp,'--reason','AR05 synthetic protocol test','--basis','ar05-fixture://synthetic-user-and-review'],label)
        after=sha(self.path) if self.path.exists() else None
        ok=(p.returncode==2 and before==after) if error else p.returncode==0 and (expected_status is None or v.get('status')==expected_status)
        return check(label,'Synthetic '+self.carrier+' protocol fixture',str(inp),('Rejected and result unchanged' if error else expected_status or 'Accepted'),{'exit_code':p.returncode,'state':v,'stderr':p.stderr,'unchanged':before==after},[ev,str(inp)],ok)
    def offer(self,label):
        return self.entry({'event':'Offer','prompt':'Engineering result saved. Start multi-round adversarial review? (synthetic question)','evidence_ref':'ar05-fixture://post-completion-question'},label,'AwaitingUser')
    def decision(self,outcome,label):
        return self.entry({'event':'Decision','outcome':outcome,'response':outcome+' (synthetic human fixture)','decided_by':'AR05 fixture actor','evidence_ref':'ar05-fixture://human-choice'},label,'InProgress' if outcome=='Accepted' else outcome)
    def round(self,label,**overrides):
        p,s,e=self.status(label+'-binding')
        current=s['current_delivery']['task_id']
        delivery=self if current==self.task_id else OBJECTS[current]
        _,ds,_=delivery.status(label+'-delivery-binding')
        report=self.task/'evidence'/(label+'.md'); report.parent.mkdir(exist_ok=True)
        report.write_text(f'# {label}\nSynthetic protocol fixture report; not an actual review of the product.\nUnique run context: {now()}\n',encoding='utf-8')
        entry={'event':'Round','round_id':label,'started_at':now(),'reviewer':'AR05 synthetic fixture reviewer','delivery_task_id':current,'subject_sha256':ds['subject_sha256'],'requirements_sha256':s['requirements_sha256'],'report_ref':str(report),'coverage':'Complete','unreviewed_items':[],'evidence_refs':['ar05-fixture://coverage-and-tests'],'findings':[],'resolutions':[]}
        entry.update(overrides)
        return entry

OBJECTS={}
def new(name,carrier,**kw):
    f=Fixture(name,carrier,**kw);OBJECTS[f.task_id]=f;return f

def basic_suite(carrier):
    tag='full' if carrier=='Full' else 'min'
    f=new(tag+'-basic',carrier,complete=False)
    f.entry({'event':'Offer','prompt':'Synthetic early question','evidence_ref':'ar05-fixture://question'},tag+'-before-completion',error=True)
    # Correct the expected result for this intentionally invalid transition.
    CASES[-1]['expected']='Rejected before a saved engineering result';CASES[-1]['result']='Passed' if CASES[-1]['actual']['exit_code']==2 else 'Failed';save()
    f.finish()
    p,s,e=f.status(tag+'-not-offered')
    check(tag+'-pending-independent','Saved engineering result without actual user decision',str(f.task),'NotOffered; user_decision Pending',{'status':s,'user_decision':f.data()[1].get('user_decision')},[e],p.returncode==0 and s['status']=='NotOffered' and f.data()[1]['user_decision']=={'outcome':'Pending'})
    dummy=f.round(tag+'-dummy-before-offer')
    f.entry(dummy,tag+'-round-without-offer',error=True)
    f.entry({'event':'Decision','outcome':'Accepted','response':'synthetic','decided_by':'fixture','evidence_ref':'ar05-fixture://choice'},tag+'-decision-without-question',error=True)
    f.offer(tag+'-offer')
    f.entry(f.round(tag+'-awaiting'),tag+'-silence-is-not-consent',error=True)
    f.decision('Declined',tag+'-decline')
    f.entry(f.round(tag+'-declined'),tag+'-decline-blocks-review',error=True)
    f.decision('Deferred',tag+'-defer')
    f.entry(f.round(tag+'-deferred'),tag+'-defer-blocks-review',error=True)
    f.decision('Accepted',tag+'-late-explicit-start')
    f.entry({'event':'Offer','prompt':'synthetic repeated offer','evidence_ref':'ar05-fixture://question'},tag+'-no-recursive-offer',error=True)
    for bad in ['Declined','Deferred','Accepted']:
        f.entry({'event':'Decision','outcome':bad,'response':'synthetic','decided_by':'fixture','evidence_ref':'ar05-fixture://choice'},tag+'-active-'+bad.lower(),error=True)
    f.entry(f.round(tag+'-one'),tag+'-first-clean','InProgress')
    _,s,e=f.status(tag+'-first-count')
    check(tag+'-count-one','First full clean review',None,'clean_streak=1',s,[e],s['clean_streak']==1)
    f.entry({'event':'Blocked','reason':'Synthetic unavailable environment','evidence_refs':['ar05-fixture://missing-env']},tag+'-blocked-resets','Blocked')
    f.entry(f.round(tag+'-after-block'),tag+'-after-block-first','InProgress')
    f.decision('Stopped',tag+'-stop')
    f.entry(f.round(tag+'-stopped'),tag+'-stop-blocks-review',error=True)
    f.decision('Accepted',tag+'-restart-after-stop')
    f.entry(f.round(tag+'-incomplete',coverage='Incomplete',unreviewed_items=['Synthetic compatibility path']),tag+'-incomplete','InProgress')
    _,s,e=f.status(tag+'-incomplete-count')
    check(tag+'-count-incomplete','Coverage incomplete',None,'clean_streak=0',s,[e],s['clean_streak']==0)
    f.entry(f.round(tag+'-declared-complete-unreviewed',unreviewed_items=['Synthetic missed branch']),tag+'-unreviewed-resets','InProgress')
    f.entry(f.round(tag+'-finding',findings=[{'id':tag+'-F001','summary':'Synthetic issue for state test','evidence_refs':['ar05-fixture://issue']}]),tag+'-finding-resets','InProgress')
    f.entry(f.round(tag+'-unresolved'),tag+'-unresolved-not-clean','InProgress')
    _,s,e=f.status(tag+'-open-count')
    check(tag+'-open-findings-count','Unresolved issue remains open',None,'clean_streak=0 and F001 open',s,[e],s['clean_streak']==0 and s['open_findings']==[tag+'-F001'])
    f.entry(f.round(tag+'-false-fixed',resolutions=[{'finding_id':tag+'-F001','disposition':'Fixed','reason':'synthetic attempted same-version fix','evidence_refs':['ar05-fixture://resolution']}]),tag+'-same-version-fixed-rejected',error=True)
    f.entry(f.round(tag+'-false-positive',resolutions=[{'finding_id':tag+'-F001','disposition':'NotAnIssue','reason':'Synthetic documented false positive','evidence_refs':['ar05-fixture://false-positive-proof']}]),tag+'-evidenced-false-positive','InProgress')
    f.entry(f.round(tag+'-second-clean'),tag+'-second-clean-passes','Passed')
    p,s,e=f.status(tag+'-passed')
    check(tag+'-acceptance-still-pending','Two clean rounds reached while human acceptance remains undecided',None,'Passed; clean_streak=2; user_decision Pending',{'state':s,'user_decision':f.data()[1]['user_decision']},[e],s['clean_streak']==2 and f.data()[1]['user_decision']=={'outcome':'Pending'})
    f.entry(f.round(tag+'-third'),tag+'-ended-blocks-third',error=True)
    f.entry({'event':'Blocked','reason':'synthetic','evidence_refs':['ar05-fixture://blocked']},tag+'-ended-blocks-blocked',error=True)
    f.decision('Accepted',tag+'-new-session-explicit')
    f.entry(f.round(tag+'-new-session-one'),tag+'-new-session-counts-from-zero','InProgress')
    return f

if __name__=='__main__':
    try:
        g.ensure_skill_integrity()
        basic_suite('Full');basic_suite('Minimal')
        dump(TEMP/'phase1-complete.json',{'ended_at':now(),'cases':len(CASES),'failed':[c['id'] for c in CASES if c['result']=='Failed']})
    except Exception:
        (TEMP/'harness-error.txt').write_text(traceback.format_exc(),encoding='utf-8'); print(traceback.format_exc());save();sys.exit(1)




