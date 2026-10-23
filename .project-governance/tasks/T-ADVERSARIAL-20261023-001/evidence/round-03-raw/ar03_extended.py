from ar03_audit import *
import time
from concurrent.futures import ThreadPoolExecutor
RESULTS.extend(json.loads((OUT/'results.json').read_text(encoding='utf-8')))

def record_case(label,inputs,expected,actual,okay):
    RESULTS.append({'id':label,'input':inputs,'expected':expected,'actual':actual,'result':'Passed' if okay else 'Failed'})
    save(OUT/'results.json',RESULTS)
    if not okay: print('FAILED',label,actual,flush=True)

def ready(carrier,name):
    root=OUT/name; root.mkdir(); (root/'src').mkdir(); (root/'src/label.txt').write_text('label=v1',encoding='utf-8')
    if carrier=='Full':
        task=new_task(root,'T-PARENT',1); finish_full(task)
    else:
        path=minimal_fixture_record(root,'T-PARENT'); task=path.parent; rec=g.read_json(path)
        m.record_minimal_review(task,requirement_items=source_review(rec['task_contract']),reason='AR03 synthetic source review',basis='src/label.txt')
        for event,status in [('run_started','started'),('verification','succeeded')]: m.append_minimal_event(task,event_type=event,summary='AR03 fixture verified local label',status=status,evidence_refs=['src/label.txt'])
        m.close_minimal_record(task,status='Implemented',established_facts=['AR03 label checked'],actual_changes=['AR03 local delivery'],verification=['Passed::Label checked::src/label.txt'])
    return root,task

def minimal_repair(root,project_id,parent):
    text='Repair one local label in the opted-in parent review.'
    path=m.create_minimal_record(root,project_id=project_id,work_item_id='W-MIN-REPAIR',task_id='T-MIN-REPAIR',ordinal=3,depends_on=[parent],supersedes=[],objective=text,request_snapshot={'language':'en','text':text,'captured_at':stamp()},requirement_items=[{'id':'R-01','source':'request_snapshot','quote':text,'reading':text,'state':'Covered','evidence_refs':['src/label.txt'],'acceptance_refs':[0]}],decisions=[{'id':'D-PROCEED','kind':'Proceed','presented':text,'response':'Proceed within the synthetic fixture only','decided_by':'synthetic-fixture','decided_at':stamp(),'outcome':'Approved','evidence_ref':'ar03://fixture-proceed'}],clarification={'mode':'Skipped','state':'Settled','notice':'Synthetic fixture local scope established; no unresolved questions.','survey_refs':['surveyed.md'],'rounds':[],'basis':'Independent isolated protocol fixture','reopened_by':[]},scope='Repair local label.',acceptance='Label is checked.',delivery_scenario='DS-03',development_type='DT-08',change_surface='UI/UX',selected_approach='Edit local label.',alternative_rejected='Leave issue open.',plan_steps=['Edit and verify label.'],verification='Exact local label check.',rollback='Restore prior label.',allowed_paths=['src/label.txt'],out_of_scope=['External systems'],forbidden_actions=['External mutation'],selection_source='automatic',basis=['Synthetic eligible local fixture'],authority_refs=['ar03://fixture-proceed'],eligibility_evidence_refs=['ar03://risk','ar03://reversible','ar03://scope','ar03://external','ar03://production'],facts=['Label is local.'],constraints=['Use only isolated Temp.'],assumptions=[],fundamentals=['One local value.'],causal_chain=['Local change addresses the fixture issue.'],decision_criteria=['Exact content checked.'])
    task=path.parent; rec=g.read_json(path)
    m.record_minimal_review(task,requirement_items=source_review(rec['task_contract']),reason='AR03 fixture independent original-word review',basis='src/label.txt')
    for event,status in [('run_started','started'),('verification','succeeded')]: m.append_minimal_event(task,event_type=event,summary='AR03 repaired local label checked',status=status,evidence_refs=['src/label.txt'])
    m.close_minimal_record(task,status='Implemented',established_facts=['AR03 repair checked'],actual_changes=['AR03 local repair'],verification=['Passed::Repaired label checked::src/label.txt'],review_parent_task_id=parent)
    return task

def repairs():
    for carrier in ['Full','Minimal']:
        root,parent=ready(carrier,'repairs-'+carrier)
        offer(parent,carrier+'-repair-offer'); decision(parent,'Accepted',carrier+'-repair-optin')
        entry(parent,round_record(parent,carrier+'-before-repair-clean'),carrier+'-before-repair-clean',expected=lambda p:p['clean_streak']==1)
        entry(parent,round_record(parent,carrier+'-repair-finding',findings=[{'id':'ISSUE-REPAIR','summary':'Synthetic fixture issue to exercise verified repair','evidence_refs':['ar03://repair-fixture']}]),carrier+'-repair-finding',expected=lambda p:p['open_findings']==['ISSUE-REPAIR'] and p['clean_streak']==0)
        # A legitimate saved Full repair must invalidate the older delivery even before any new review round.
        pid=task_parts(parent)[3]['project_id']
        child=new_task(root,'T-REPAIR',2,project_id=pid,depends_on=[parent.name]); finish_full(child,parent=parent.name)
        state(child,carrier+'-repair-managed',lambda p:p['status']=='ManagedByParent' and p['parent_task_id']==parent.name)
        state(parent,carrier+'-repair-stale-before-round',lambda p:p['status']=='Stale' and p['clean_streak']==0 and p['current_delivery']['task_id']==child.name)
        entry(parent,round_record(parent,carrier+'-old-delivery'),carrier+'-old-delivery',2)
        premature=round_record(parent,carrier+'-premature-repair',delivery=child,started_at=task_parts(parent)[2]['completed_at'])
        entry(parent,premature,carrier+'-premature-repair',2)
        fix={'finding_id':'ISSUE-REPAIR','disposition':'Fixed','reason':'A new dependent task delivered and verified the fixture correction','evidence_refs':['src/label.txt']}
        entry(parent,round_record(parent,carrier+'-repair-clean-1',delivery=child,resolutions=[fix]),carrier+'-repair-clean-1',expected=lambda p:p['clean_streak']==1 and not p['open_findings'] and p['reviewed_delivery']['task_id']==child.name)
        # A later Minimal repair also changes the current delivery and prevents parent recursion.
        mchild=minimal_repair(root,pid,parent.name)
        state(mchild,carrier+'-minimal-repair-managed',lambda p:p['status']=='ManagedByParent')
        offer_entry={'event':'Offer','recorded_at':stamp(),'prompt':'Synthetic recursive review offer','evidence_ref':'ar03://recursive'}
        entry(mchild,offer_entry,carrier+'-repair-no-recursion',2)
        state(parent,carrier+'-second-repair-stale',lambda p:p['status']=='Stale' and p['clean_streak']==0 and p['current_delivery']['task_id']==mchild.name)
        entry(parent,round_record(parent,carrier+'-minimal-repair-clean-1',delivery=mchild),carrier+'-minimal-repair-clean-1',expected=lambda p:p['clean_streak']==1)
        entry(parent,round_record(parent,carrier+'-minimal-repair-clean-2',delivery=mchild),carrier+'-minimal-repair-clean-2',expected=lambda p:p['status']=='Passed' and p['clean_streak']==2)
        # A new child cannot suppress the post-completion offer when the purported parent is closed.
        blocked_child=new_task(root,'T-AFTER-PASS',4,project_id=pid,depends_on=[parent.name])
        try:
            finish_full(blocked_child,parent=parent.name); observed='accepted'
        except g.GovernanceError as exc: observed=str(exc)
        record_case(carrier+'-repair-after-parent-pass',{'parent':str(parent),'child':str(blocked_child)},'reject closed parent and do not save child outcome',{'message':observed,'after_exists':(blocked_child/'after.json').exists()},observed!='accepted' and not (blocked_child/'after.json').exists())
        # Ordinary amendments may correct explanatory prose without resetting a version, but may not rewrite review history/parent.
        before_state=state(parent,carrier+'-metadata-before',lambda p:p['status']=='Passed')
        if carrier=='Full':
            cli('amend_record.py',[parent/'after.json','--path','established_facts','--value-json','["Corrected explanatory wording for the same fixture delivery"]','--reason','AR03 prose correction','--basis','src/label.txt'],carrier+'-prose-amend')
            state(parent,carrier+'-metadata-after',lambda p:p['status']=='Passed' and p['reviewed_delivery']==before_state['reviewed_delivery'])
            cli('amend_record.py',[parent/'after.json','--path','adversarial_review','--value-json','[]','--reason','AR03 negative rewrite test','--basis','ar03://negative'],carrier+'-history-rewrite',2)
            cli('amend_record.py',[child/'after.json','--path','adversarial_review_parent','--value-json','"OTHER"','--reason','AR03 negative parent rewrite','--basis','ar03://negative'],carrier+'-parent-rewrite',2)
        else:
            rec=g.read_json(parent/'task-record.json'); out=rec['task_outcome']; con=m.minimal_approval_contract(rec)
            d={'outcome':'Approved','presented':'The synthetic fixture delivery and completed review','response':'Synthetic approval for fixture only','decided_by':'synthetic-fixture','decided_at':stamp(),'evidence_ref':'ar03://fixture-user-decision','subject_sha256':g.user_decision_subject_sha256(con,rec['run_ledger'],out)}
            p=OUT/'inputs/Minimal-user-decision.json'; save(p,d)
            cli('manage_minimal_task.py',['record-review',parent,'--user-decision-json-file',p,'--reason','AR03 separate user decision','--basis','ar03://fixture-user-decision'],carrier+'-independent-user-decision')
            state(parent,carrier+'-metadata-after',lambda p:p['status']=='Passed' and p['reviewed_delivery']==before_state['reviewed_delivery'])
        # Repair parent itself remains the original task, never its prior repair.
        badchild=new_task(root,'T-WRONG-PARENT',5,project_id=pid,depends_on=[child.name])
        try: finish_full(badchild,parent=child.name); observed='accepted'
        except g.GovernanceError as exc: observed=str(exc)
        record_case(carrier+'-recursive-repair-parent',{'child':str(badchild),'parent':str(child)},'reject ManagedByParent as new parent',observed,observed!='accepted')
    print('repair suite complete',len(RESULTS),flush=True)

def schema_install_freeze():
    freeze=json.loads((REPO/'.project-governance/tasks/T-ADVERSARIAL-20261023-003/evidence/source-files-3ef1adf1ff23fb1f.json').read_text(encoding='utf-8-sig'))
    differences=[]
    for item in freeze['source_files']:
        actual=hashlib.sha256((REPO/item['path']).read_bytes()).hexdigest()
        if actual!=item['sha256']: differences.append({'path':item['path'],'actual':actual,'expected':item['sha256']})
    record_case('source-freeze-96-files',{'freeze_count':freeze['count'],'freeze_sha256':freeze['source_sha256']},'all 96 file hashes match',{'differences':differences},len(freeze['source_files'])==96 and not differences)
    full=json.loads((SKILL/'assets/runtime/schemas/task-after.schema.json').read_text(encoding='utf-8')); mini=json.loads((SKILL/'assets/runtime/schemas/minimal-task-record.schema.json').read_text(encoding='utf-8'))
    # Locate the nested task_outcome review schema by structure, not line offsets.
    def seek(value):
        if isinstance(value,dict):
            if 'adversarial_review' in value.get('properties',{}): return value['properties']['adversarial_review']
            for v in value.values():
                got=seek(v)
                if got is not None:return got
        elif isinstance(value,list):
            for v in value:
                got=seek(v)
                if got is not None:return got
        return None
    versions=[seek(full),seek(mini),ar.review_schema()]
    record_case('schema-parity',{'schemas':['task-after.schema.json','minimal-task-record.schema.json','review_schema()']},'identical full/minimal/runtime review schema',{'equal':versions[0]==versions[1]==versions[2]},versions[0]==versions[1]==versions[2])
    import deploy_console
    actual=deploy_console.computed_closure(SKILL/'scripts')
    record_case('distribution-import-closure',{'declared':deploy_console.SNAPSHOT_MODULES},'declared import closure is complete',{'actual':actual},set(actual)==set(deploy_console.SNAPSHOT_MODULES))
    install=Path(r'C:\Users\Administrator\.codex\skills\run-governed-product-workflow')
    changes=[]
    for item in freeze['source_files']:
        rel=Path(item['path']).relative_to(Path('skills/product-engineering/run-governed-product-workflow'))
        h=hashlib.sha256((install/rel).read_bytes()).hexdigest()
        if h!=item['sha256']: changes.append({'path':str(rel),'sha256':h})
    record_case('installation-known-difference',{'junction':str(install),'resolved':str(install.resolve())},'only explained governance_artifacts.py difference',changes,len(changes)==1 and changes[0]['path']=='scripts\\governance_artifacts.py' and changes[0]['sha256']=='ff8124ccd76fcc76527ac2ea1ee2c848aff0604f2a15319e6bf193066bee4bd3')
    original_cli=globals()['SKILL']
    globals()['SKILL']=install
    # ar03_audit.cli resolves its defining module global, so pass an absolute path as script argument.
    for carrier in ['Full','Minimal']:
        root,task=ready(carrier,'installed-'+carrier)
        cli(str(install/'scripts/adversarial_review.py'),[task],carrier+'-installed-status',expected=lambda p:p['status']=='NotOffered')
        offer_obj={'event':'Offer','recorded_at':stamp(),'prompt':'Synthetic installed-entry opt-in question','evidence_ref':'ar03://installed-offer'}
        path=OUT/'inputs'/(carrier+'-installed-offer.json');save(path,offer_obj)
        cli(str(install/'scripts/adversarial_review.py'),[task,'--entry-json-file',path,'--reason','AR03 installed entry case','--basis','ar03://installed-offer'],carrier+'-installed-write',expected=lambda p:p['status']=='AwaitingUser')
        decision(task,'Accepted',carrier+'-installed-accept')
        for no in [1,2]:
            rec=round_record(task,carrier+'-installed-round-'+str(no)); p=OUT/'inputs'/(carrier+'-installed-round-'+str(no)+'.json');save(p,rec)
            cli(str(install/'scripts/adversarial_review.py'),[task,'--entry-json-file',p,'--reason','AR03 installed round case','--basis','ar03://installed-round'],carrier+'-installed-round-'+str(no),expected=lambda q,n=no:q['clean_streak']==n)
    globals()['SKILL']=original_cli
    print('schema/install complete',len(RESULTS),flush=True)

def concurrency():
    for carrier in ['Full','Minimal']:
        root,task=ready(carrier,'concurrency-'+carrier)
        path,doc,out,con,events=task_parts(task);rev=doc['revision']
        offer_file=OUT/'inputs'/(carrier+'-concurrent-offer.json');save(offer_file,{'event':'Offer','recorded_at':stamp(),'prompt':'Synthetic concurrent offer','evidence_ref':'ar03://concurrent-offer'})
        cmd1=[sys.executable,'-B','-X','utf8',str(SKILL/'scripts/adversarial_review.py'),str(task),'--entry-json-file',str(offer_file),'--reason','AR03 concurrent append','--basis','ar03://concurrent-offer']
        if carrier=='Full':
            cmd2=[sys.executable,'-B','-X','utf8',str(SKILL/'scripts/amend_record.py'),str(path),'--path','established_facts','--value-json','["Concurrent explanatory correction"]','--reason','AR03 concurrent amendment','--basis','ar03://concurrent-amend']
        else:
            d={'outcome':'Approved','presented':'Synthetic delivery under concurrent append','response':'Fixture only approval','decided_by':'synthetic-fixture','decided_at':stamp(),'evidence_ref':'ar03://concurrent-decision','subject_sha256':g.user_decision_subject_sha256(con,events,out)}
            dfile=OUT/'inputs/Minimal-concurrent-user-decision.json';save(dfile,d)
            cmd2=[sys.executable,'-B','-X','utf8',str(SKILL/'scripts/manage_minimal_task.py'),'record-review',str(task),'--user-decision-json-file',str(dfile),'--reason','AR03 concurrent user decision','--basis','ar03://concurrent-decision']
        procs=[subprocess.Popen(cmd,cwd=OUT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8') for cmd in [cmd1,cmd2]]
        actual=[]
        for proc in procs:
            stdout,stderr=proc.communicate(timeout=30);actual.append({'returncode':proc.returncode,'stdout':stdout,'stderr':stderr})
        _,after,afterout,_,_=task_parts(task)
        okay=all(x['returncode']==0 for x in actual) and after['revision']==rev+2 and len(afterout['adversarial_review'])==1
        okay=okay and (afterout.get('established_facts')==['Concurrent explanatory correction'] if carrier=='Full' else afterout['user_decision']['outcome']=='Approved')
        record_case(carrier+'-concurrent-append-and-amend',{'commands':[cmd1,cmd2],'initial_revision':rev},'both succeed and both changes retained; revision advances by two',{'processes':actual,'final_revision':after['revision'],'review_records':afterout['adversarial_review'],'user_decision':afterout['user_decision']},okay)
        state(task,carrier+'-concurrency-final-valid',lambda p:p['status']=='AwaitingUser')
    print('concurrency complete',len(RESULTS),flush=True)

if __name__=='__main__':
    try:
        repairs();schema_install_freeze();concurrency()
    except Exception:
        (OUT/'extension-exception.txt').write_text(traceback.format_exc(),encoding='utf-8');raise
    finally:save(OUT/'results.json',RESULTS)
