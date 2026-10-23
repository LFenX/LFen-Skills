from independent_suite import *
import concurrent.futures
CASES.extend(json.loads((TEMP/'cases.json').read_text(encoding='utf-8')))
CALLS.extend(json.loads((TEMP/'commands.json').read_text(encoding='utf-8')))
FIXTURES.extend(json.loads((TEMP/'fixtures.json').read_text(encoding='utf-8')))

def direct_case(name,condition,inp,expected,fn,predicate):
    started=now()
    try: actual=fn();passed=predicate(actual)
    except Exception as exc: actual={'exception':type(exc).__name__,'message':str(exc)};passed=False
    p=LOG/(f'{len(CALLS)+1:03}-{name}.json');dump(p,{'started_at':started,'ended_at':now(),'actual':actual})
    CALLS.append({'label':name,'method':'independent assertion/minimal API','evidence':str(p)});save()
    return check(name,condition,inp,expected,actual,[str(p)],passed)

def persist(f,d):dump(f.path,d)
def historical_suite(carrier):
    tag='full' if carrier=='Full' else 'min'
    f=new(tag+'-legacy',carrier)
    d,o=f.data();o.pop('adversarial_review');persist(f,d)
    before=sha(f.path); p,s,e=f.status(tag+'-legacy-untracked')
    check(tag+'-legacy-no-enrollment','Previously saved outcome lacks review field',str(f.path),'LegacyUntracked; source bytes unchanged',s,[e],p.returncode==0 and s['status']=='LegacyUntracked' and before==sha(f.path))
    f.entry({'event':'Offer','prompt':'Synthetic unauthorized retroactive enrollment','evidence_ref':'ar05-fixture://question'},tag+'-legacy-not-auto-enrolled',error=True)
    # A legacy identity error must not become valid merely by lacking the new field.
    d,o=f.data();o['task_id']='T-MISMATCH' if carrier=='Full' else o.get('task_id','T-MISMATCH')
    if carrier=='Minimal': d['task_id']='T-MISMATCH'
    persist(f,d);p,s,e=f.status(tag+'-legacy-identity-invalid')
    check(tag+'-legacy-still-validates-identity','Legacy outcome identity differs from task directory',str(f.path),'Rejected',{'exit_code':p.returncode,'stderr':p.stderr},[e],p.returncode==2)
    # Existing old-protocol records are read as un-revalidated rather than counted as current.
    f=new(tag+'-old-protocol',carrier);f.offer(tag+'-old-protocol-offer');f.decision('Accepted',tag+'-old-protocol-accept')
    f.entry(f.round(tag+'-old-one'),tag+'-old-fixture-round1','InProgress')
    f.entry(f.round(tag+'-old-two'),tag+'-old-fixture-round2','Passed')
    d,o=f.data()
    for r in o['adversarial_review']:
        if r['event']=='Round':
            for field in ['review_contract_version','report_ref','report_sha256','delivery_completed_at','delivery_verified_at','session_completed']:r.pop(field,None)
            r['requirements_sha256']=ar._legacy_requirements_subject(f.contract())
    persist(f,d);before=sha(f.path);p,s,e=f.status(tag+'-old-protocol-state')
    check(tag+'-old-protocol-unrevalidated','Two historical unbound clean rounds',str(f.path),'LegacyNotRevalidated; clean_streak=0; no rewrite',s,[e],p.returncode==0 and s['status']=='LegacyNotRevalidated' and s['clean_streak']==0 and before==sha(f.path))
    f.entry(f.round(tag+'-legacy-resume'),tag+'-old-protocol-needs-new-choice',error=True)
    f.decision('Accepted',tag+'-old-protocol-new-choice')
    f.entry(f.round(tag+'-old-new-one'),tag+'-old-current-round-first','InProgress')
    # Historical engineering terminal: remove later proof signals and move all record times before policy cutover.
    f=new(tag+'-historical-engineering',carrier)
    d,o=f.data();contract=d if carrier=='Full' else d['task_contract']
    if carrier=='Full': contract=g.read_json(f.task/'before.json')
    for owner in [d,contract,o]: owner.pop('proof_contract_version',None)
    o.pop('scope_reconciliation',None);o.pop('user_decision',None);o.pop('adversarial_review',None)
    for req in contract['requirement_items']:req.pop('review',None)
    for decision in contract['decisions']:
        decision.pop('outcome',None);decision.pop('subject_sha256',None)
    def age(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k.endswith('_at') and isinstance(v,str):value[k]='2026-08-15T00:00:00Z'
                else:age(v)
        elif isinstance(value,list):
            for v in value:age(v)
    age(d);age(contract)
    if carrier=='Full':
        dump(f.task/'before.json',contract)
        events=g.read_jsonl(f.task/'run.jsonl');age(events)
        (f.task/'run.jsonl').write_text(''.join(json.dumps(ev,ensure_ascii=False)+'\n' for ev in events),encoding='utf-8')
    persist(f,d)
    before_hash={str(p):sha(p) for p in f.task.iterdir() if p.is_file()}
    p,s,e=f.status(tag+'-historical-query')
    after_hash={str(p):sha(p) for p in f.task.iterdir() if p.is_file()}
    check(tag+'-historical-engineering-query','Pre-cutover terminal with no modern proof signals',str(f.task),'LegacyUntracked; no source rewrite',{'exit_code':p.returncode,'state':s,'stderr':p.stderr},[e],p.returncode==0 and s['status']=='LegacyUntracked' and before_hash==after_hash)
    return f

def requirements_suite():
    f=new('requirement-binding','Full');f.offer('requirement-offer');f.decision('Accepted','requirement-accept')
    f.entry(f.round('requirement-first'),'requirement-first','InProgress')
    d,o=f.data();b=f.contract(); events=g.read_jsonl(f.task/'run.jsonl')
    original=ar.requirements_subject(b)
    modified=copy.deepcopy(b);modified['clarification']['basis']='Correction of explanation only';modified['clarification']['survey_refs']=['revised-survey.md'];modified['request_snapshot']['captured_at']='2026-01-01T00:00:00Z'
    direct_case('requirements-exclude-annotation','Only basis, survey references, or capture time changes',None,'Same requirement binding',lambda:{'before':original,'after':ar.requirements_subject(modified)},lambda x:x['before']==x['after'])
    changed=copy.deepcopy(b);changed['request_snapshot']['text']+=' Also require a second label.'
    direct_case('request-word-change-resets','Original user words change',None,'Stale, streak=0',lambda:ar.bound_review_state(f.task,o,changed,events),lambda x:x['status']=='Stale' and x['clean_streak']==0)
    # Questions/defaults/answers in complete source context each bind the requirements.
    example=copy.deepcopy(b);example['clarification']['rounds']=[{'ordinal':1,'exchanges':[{'question':'Which label?','changes':['scope'],'recommended_default':'label A','answer':'label B','answer_state':'Answered'}]}]
    h=ar.requirements_subject(example)
    for key,value in [('question','Which other label?'),('recommended_default','label C'),('answer','label D')]:
        altered=copy.deepcopy(example);altered['clarification']['rounds'][0]['exchanges'][0][key]=value
        direct_case('requirements-bind-'+key,'Clarification source context changes',key,'Different requirement binding',lambda alt=altered:{'before':h,'after':ar.requirements_subject(alt)},lambda x:x['before']!=x['after'])

def concurrency_suite(carrier):
    tag='full' if carrier=='Full' else 'min'
    f=new(tag+'-concurrent',carrier);p,s,e=f.status(tag+'-concurrent-binding')
    offer={'event':'Offer','recorded_at':now(),'prompt':'Synthetic post-completion question','evidence_ref':'ar05-fixture://question'}
    decision={'outcome':'Approved','presented':'Synthetic delivered fixture version '+s['subject_sha256'],'response':'Approve fixture (synthetic)','decided_by':'AR05 fixture actor','decided_at':now(),'evidence_ref':'ar05-fixture://human-acceptance','subject_sha256':s['subject_sha256']}
    inp=TEMP/'inputs'/(tag+'-concurrent-offer.json');dump(inp,offer)
    dec=TEMP/'inputs'/(tag+'-concurrent-acceptance.json');dump(dec,decision)
    args1=[str(f.task),'--entry-json-file',str(inp),'--reason','AR05 synthetic concurrency','--basis','ar05-fixture://synthetic']
    args2=([str(f.path),'--path','user_decision','--value-json-file',str(dec),'--reason','AR05 synthetic concurrency','--basis','ar05-fixture://synthetic'] if carrier=='Full' else ['record-review',str(f.task),'--user-decision-json-file',str(dec),'--reason','AR05 synthetic concurrency','--basis','ar05-fixture://synthetic'])
    script2='amend_record.py' if carrier=='Full' else 'manage_minimal_task.py'
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        a=pool.submit(cli,'adversarial_review.py',args1,tag+'-parallel-offer')
        b=pool.submit(cli,script2,args2,tag+'-parallel-acceptance')
        r1=a.result();r2=b.result()
    d,o=f.data(); p,s,e=f.status(tag+'-parallel-state')
    check(tag+'-concurrent-no-lost-update','Review append and ordinary user decision overlap',{'review':str(inp),'acceptance':str(dec)},'Both succeed; each update retained; AwaitingUser',{'codes':[r1[0].returncode,r2[0].returncode],'state':s,'decision':o['user_decision'],'review_records':len(o['adversarial_review'])},[r1[2],r2[2],e],r1[0].returncode==0 and r2[0].returncode==0 and s['status']=='AwaitingUser' and o['user_decision']==decision and len(o['adversarial_review'])==1)
    f.entry(f.round(tag+'-acceptance-only'),tag+'-acceptance-does-not-grant-review',error=True)
    # Generic amendment and completed Minimal review entry cannot erase protected history.
    if carrier=='Full':
        r,v,e=cli('amend_record.py',[f.path,'--path','adversarial_review','--value-json','[]','--reason','synthetic erase','--basis','ar05-fixture://attempt'],tag+'-erase-history')
        check(tag+'-generic-amendment-cannot-erase','Generic amendment targets review history',str(f.path),'Rejected',{'code':r.returncode,'stderr':r.stderr,'stdout':r.stdout},[e],r.returncode==2)
    else:
        r,v,e=cli('manage_minimal_task.py',['record-review',f.task,'--requirement-items-json-file',TEMP/'inputs'/'missing-items.json','--reason','synthetic invalid update','--basis','ar05-fixture://attempt'],tag+'-closed-contract-update')
        # This is an input-error smoke check only, not claimed as proof of protected history.
        check(tag+'-missing-input-error-preserves-state','A caller passes an absent fixture input file',str(f.path),'Rejected; review record retained',{'code':r.returncode,'stderr':r.stderr},[e],r.returncode==2 and len(f.data()[1]['adversarial_review'])==1)
    return f

try:
    historical_suite('Full');historical_suite('Minimal');requirements_suite();concurrency_suite('Full');concurrency_suite('Minimal')
    dump(TEMP/'phase3-complete.json',{'ended_at':now(),'cases':len(CASES),'failed':[c['id'] for c in CASES if c['result']=='Failed']})
except Exception:
    (TEMP/'phase3-error.txt').write_text(traceback.format_exc(),encoding='utf-8');print(traceback.format_exc());save();sys.exit(1)
