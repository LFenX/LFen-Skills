import review_harness as h
import json, pathlib, copy, ast, concurrent.futures, time
from datetime import datetime, timezone, timedelta
from jsonschema import Draft202012Validator
import deploy_console as dc
h.CASES=json.loads((h.BASE/'cases.json').read_text(encoding='utf-8')); h.COUNTER=len(list(h.RAW.glob('*.json')))

def record_check(name,expected,actual,ok,inp=None):
    p=h.write(h.RAW/(name+'.json'),{'input':inp,'expected':expected,'actual':actual,'at':h.now()})
    h.check(name,None,expected,actual,ok,inp,p)

# Schema definitions and import closure must agree in the distributed installation.
full=json.loads((h.SKILL/'assets/runtime/schemas/task-after.schema.json').read_text(encoding='utf-8'))
mini=json.loads((h.SKILL/'assets/runtime/schemas/minimal-task-record.schema.json').read_text(encoding='utf-8'))
record_check('full-single-review-schema',True,full['properties']['adversarial_review']==h.a.review_schema(),full['properties']['adversarial_review']==h.a.review_schema())
record_check('minimal-single-review-schema',True,mini['properties']['task_outcome']['oneOf'][1]['properties']['adversarial_review']==h.a.review_schema(),mini['properties']['task_outcome']['oneOf'][1]['properties']['adversarial_review']==h.a.review_schema())
schemas=list((h.SKILL/'assets/runtime/schemas').glob('*.json')); schema_errors=[]
for p in schemas:
    try: Draft202012Validator.check_schema(json.loads(p.read_text(encoding='utf-8')))
    except Exception as e: schema_errors.append({'path':str(p),'error':str(e)})
record_check('all-runtime-schema-valid',{'errors':[]},{'count':len(schemas),'errors':schema_errors},not schema_errors)
pyfiles=list(h.SKILL.rglob('*.py')); compile_errors=[]
for p in pyfiles:
    try: compile(p.read_bytes(),str(p),'exec')
    except Exception as e: compile_errors.append({'path':str(p),'error':str(e)})
record_check('python-source-compiles',{'errors':[]},{'count':len(pyfiles),'errors':compile_errors},not compile_errors)
actual=dc.computed_closure(h.SCRIPTS)
record_check('console-distribution-import-closure',list(dc.SNAPSHOT_MODULES),list(actual),set(actual)==set(dc.SNAPSHOT_MODULES))
root=h.BASE/'deployed-console'; root.mkdir(exist_ok=True)
raw,res,p=h.cli('deploy_console.py',['--project-root',root],'deploy-console-temp'); h.check('deploy-console-temp',raw,{'exit_code':0},raw,raw['exit_code']==0,{'root':str(root)},p)
raw,res,p=h.cli('deploy_console.py',['--project-root',root,'--check'],'deployment-check-temp'); h.check('deployment-check-temp',raw,{'exit_code':0},raw,raw['exit_code']==0,{'root':str(root)},p)
# Every field carrying original question/default/answer context changes the requirement digest;
# explanatory metadata corrections do not.
base={'request_snapshot':{'text':'Synthetic original instruction','captured_at':'2020-01-01T00:00:00Z','source':'ar04://original'},'clarification':{'basis':'synthetic basis','notice':'synthetic notice','survey_refs':['survey.md'],'rounds':[{'ordinal':1,'exchanges':[{'question':'Synthetic question','changes':['Acceptance'],'recommended_default':'Synthetic default','answer':'Synthetic explicit answer','answer_state':'Answered'}]}]}}
digest=h.a.requirements_subject(base)
for key,val in [('basis','corrected explanation'),('notice','corrected notice'),('survey_refs',['another-survey.md'])]:
    c=copy.deepcopy(base); c['clarification'][key]=val; actual=h.a.requirements_subject(c)
    record_check('requirement-metadata-'+key,{'digest_unchanged':True},{'old':digest,'new':actual},digest==actual,{'field':key,'value':val})
c=copy.deepcopy(base); c['request_snapshot']['captured_at']='2021-01-01T00:00:00Z'; actual=h.a.requirements_subject(c); record_check('requirement-capture-metadata',True,actual==digest,actual==digest)
for key in ['question','recommended_default','answer','changes','answer_state']:
    c=copy.deepcopy(base); c['clarification']['rounds'][0]['exchanges'][0][key]=['Scope'] if key=='changes' else 'Changed original context '+key; actual=h.a.requirements_subject(c)
    record_check('requirement-context-'+key,{'digest_changed':True},{'old':digest,'new':actual},actual!=digest,{'field':key,'value':c['clarification']['rounds'][0]['exchanges'][0][key]})
c=copy.deepcopy(base); c['request_snapshot']['text']='New original instruction'; actual=h.a.requirements_subject(c); record_check('requirement-text-bound',True,actual!=digest,actual!=digest)
# Public mutation operations serialize with review append and preserve both changes.
for carrier in ['Full','Minimal']:
    tag=carrier.lower(); t=h.fresh(carrier,tag+'_concurrency'); h.offer(t,tag+'-con-offer'); h.decision(t,tag+'-con-start')
    path=h.outcome_path(t); before=h.g.read_json(path); original_ledger=(t/'run.jsonl').read_bytes() if carrier=='Full' else json.dumps(before['run_ledger'],sort_keys=True)
    v=h.round_value(t,tag+'-con-round'); ip=h.write(h.BASE/'inputs'/(tag+'-con-round.json'),v)
    review_args=[t,'--entry-json-file',ip,'--reason','Concurrent review append','--basis','ar04://concurrency']
    if carrier=='Full':
        value=h.write(h.BASE/'inputs'/'con-actual-changes.json',['Synthetic local change','Concurrent explanatory amendment'])
        script='amend_record.py'; args=[path,'--path','actual_changes','--value-json-file',value,'--reason','Concurrent ordinary amendment','--basis','ar04://concurrency']
    else:
        _,st,_=h.state(t,tag+'-con-subject')
        value=h.write(h.BASE/'inputs'/'con-user-decision.json',{'outcome':'Approved','presented':'Synthetic saved engineering result','response':'Synthetic explicit approval','decided_by':'synthetic-user','decided_at':h.now(),'evidence_ref':'ar04://synthetic-user-decision','subject_sha256':st['subject_sha256']})
        script='manage_minimal_task.py'; args=['record-review',t,'--user-decision-json-file',value,'--reason','Concurrent user decision','--basis','ar04://concurrency']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        with h.g.ledger_lock(path):
            f1=pool.submit(h.cli,script,args,tag+'-con-amend')
            f2=pool.submit(h.cli,'adversarial_review.py',review_args,tag+'-con-append')
            time.sleep(0.2)
        r1,s1,p1=f1.result(); r2,s2,p2=f2.result()
    after=h.g.read_json(path); out=after if carrier=='Full' else after['task_outcome']
    changed=after['actual_changes']==['Synthetic local change','Concurrent explanatory amendment'] if carrier=='Full' else out['user_decision']['outcome']=='Approved'
    ledger_same=(t/'run.jsonl').read_bytes()==original_ledger if carrier=='Full' else json.dumps(after['run_ledger'],sort_keys=True)==original_ledger
    actual={'amend_rc':r1['exit_code'],'review_rc':r2['exit_code'],'revision_delta':after['revision']-before['revision'],'amendment_delta':len(after['amendments'])-len(before['amendments']),'new_round_retained':out['adversarial_review'][-1]['round_id']==v['round_id'],'ordinary_change_retained':changed,'ledger_unchanged':ledger_same}
    record_check(tag+'-concurrent-no-lost-update',{'both_rc':0,'revision_delta':2,'amendment_delta':2,'both_changes_retained':True,'ledger_unchanged':True},actual,r1['exit_code']==r2['exit_code']==0 and actual['revision_delta']==2 and actual['amendment_delta']==2 and actual['new_round_retained'] and changed and ledger_same,{'review':v,'ordinary_command':r1['command'],'raw_refs':[str(p1),str(p2)]})
    # Public ordinary amendment cannot erase review history or parent affiliation.
    if carrier=='Full':
        for field,value in [('adversarial_review',[]),('adversarial_review_parent','T-OTHER')]:
            ip=h.write(h.BASE/'inputs'/(field+'.json'),value); raw,res,p=h.cli('amend_record.py',[path,'--path',field,'--value-json-file',ip,'--allow-add','--reason','Synthetic attempted history edit','--basis','ar04://negative'],tag+'-protect-'+field)
            record_check(tag+'-protect-'+field,{'exit_code':2},{'exit_code':raw['exit_code'],'output':raw['stdout']+raw['stderr']},raw['exit_code']==2,{'path':field,'value':value})
    # Same fixture is compatible with the actual installed script and subject CLI.
    installed=pathlib.Path(r'C:\Users\Administrator\.lfenskills\skills\product-engineering\run-governed-product-workflow')
    istt=h.query(t,tag+'-installed-state',{'status':'InProgress','clean_streak':1},skill=installed)
    raw,res,p=h.cli('get_approval_subject.py',[t],tag+'-installed-approval-digest',skill=installed)
    record_check(tag+'-installed-digest-matches-review',{'digest':istt['subject_sha256']},{'exit_code':raw['exit_code'],'digest':raw['stdout'].strip()},raw['exit_code']==0 and raw['stdout'].strip()==istt['subject_sha256'])
    # Declined/Deferred/AwaitingUser keep the saved result and have no recommendation to continue.
    for choice in ['AwaitingUser','Declined','Deferred','Stopped']:
        q=h.fresh(carrier,tag+'_signal_'+choice.lower()); h.offer(q,tag+'-signal-offer-'+choice)
        if choice=='Stopped': h.decision(q,tag+'-signal-start-'+choice)
        if choice!='AwaitingUser': h.decision(q,tag+'-signal-answer-'+choice,outcome=choice)
        raw,res,p=h.cli('signals.py',['--project-root',q.parents[2]],tag+'-signal-final-'+choice)
        rec=(res or {}).get('recommended_commands',[])
        bad=any('先处理未解决' in x.get('reason','') or '主动询问是否' in x.get('reason','') for x in rec)
        record_check(tag+'-signal-no-auto-start-'+choice,{'no_review_start_or_continue_recommendation':True},{'exit_code':raw['exit_code'],'recommendations':rec},raw['exit_code']==0 and not bad,{'choice':choice})
# Preserve the separate failed helper attempts; they are not product findings.
h.write(h.BASE/'tooling-notes.json',{'incidents':[{'command':'Auxiliary schema audit attempt','observed':'AttributeError: governance_artifacts has no load_schema','reason':'Review script referenced an absent helper; replaced with direct JSON file loading. This boundary script executes corrected schema assertions.'},{'command':'Auxiliary one-line code read','observed':'SyntaxError: unterminated string literal','reason':'PowerShell quoting in the read command; retried with a single quoted here-string.'}]})
h.write(h.BASE/'final-case-summary.json',{'at':h.now(),'case_count':len(h.CASES),'passed':sum(c['result']=='Passed' for c in h.CASES),'failed':[c for c in h.CASES if c['result']=='Failed']})
print(json.dumps({'case_count':len(h.CASES),'passed':sum(c['result']=='Passed' for c in h.CASES),'failed':sum(c['result']=='Failed' for c in h.CASES)},ensure_ascii=False))
