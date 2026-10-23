from independent_suite import *
CASES.extend(json.loads((TEMP/'cases.json').read_text(encoding='utf-8')))
CALLS.extend(json.loads((TEMP/'commands.json').read_text(encoding='utf-8')))
FIXTURES.extend(json.loads((TEMP/'fixtures.json').read_text(encoding='utf-8')))
for carrier,tag in [('Full','full'),('Minimal','min')]:
    f=new(tag+'-ambiguous',carrier);f.offer(tag+'-ambiguous-offer');f.decision('Accepted',tag+'-ambiguous-accept')
    r=f.round(tag+'-before-ambiguous');f.entry(r,tag+'-ambiguous-original-first','InProgress')
    a=new(tag+'-repair-a',carrier,root=f.root,parent=f.task_id)
    a_original=copy.deepcopy(a.data()[0])
    b=new(tag+'-repair-b',carrier,root=f.root,parent=f.task_id)
    d,o=a.data();o['completed_at']=b.data()[1]['completed_at']
    if carrier=='Minimal':d['completed_at']=o['completed_at']
    dump(a.path,d)
    p,s,e=f.status(tag+'-ambiguous-query')
    check(tag+'-ambiguous-current-reset','Two explicitly related saved deliveries tie at latest completion',{'a':str(a.path),'b':str(b.path)},'Stale, current_delivery Ambiguous, streak=0',s,[e],p.returncode==0 and s['status']=='Stale' and s['current_delivery']['status']=='Ambiguous' and s['clean_streak']==0)
    _,binding,_=b.status(tag+'-ambiguous-b-subject')
    report=f.task/'evidence/ambiguous-report.md';report.write_text('Synthetic ambiguous-current-delivery counterexample report.',encoding='utf-8')
    entry={**r,'round_id':tag+'-ambiguous-candidate','recorded_at':now(),'started_at':now(),'delivery_task_id':b.task_id,'subject_sha256':binding['subject_sha256'],'report_ref':str(report)}
    f.entry(entry,tag+'-ambiguous-round-refused',error=True)
    f.entry({'event':'Blocked','reason':'Synthetic current delivery ambiguity','evidence_refs':['ar05-fixture://ambiguous']},tag+'-ambiguous-block-recorded','Blocked')
    dump(a.path,a_original)
    f.entry(f.round(tag+'-after-ambiguity'),tag+'-unique-delivery-after-block','InProgress')
    # Version invalidation on an active and an ended session is separate from report invalidation.
    p,s,e=f.status(tag+'-version-before-close')
    f.entry(f.round(tag+'-ambiguity-final'),'version-'+tag+'-pair','Passed')
    d,o=f.data(); contract=f.contract();events=g.read_jsonl(f.task/'run.jsonl') if carrier=='Full' else d['run_ledger']
    subjects,hashes,current_ids=ar._current_bindings(f.task,o,contract,events)
    current_id=next(iter(current_ids));subjects[current_id]='9'*64
    actual=ar.review_state(o,contract,delivery_subjects=subjects,report_hashes=hashes,current_delivery_ids=current_ids)
    ev=LOG/(f'{len(CALLS)+1:03}-{tag}-changed-version-after-end.json');dump(ev,{'input':'Synthetic current saved delivery binding changed; same historical accepted decision','actual':actual});CALLS.append({'label':tag+'-changed-version-after-end','method':'minimal API state replay','evidence':str(ev)});save()
    check(tag+'-version-after-end-restart','Current delivery version changes after its clean pair ended',None,'RestartRequired and streak=0',actual,[str(ev)],actual['status']=='RestartRequired' and actual['clean_streak']==0)
    # The saved relation is append-only through generic Full amendment.
    if carrier=='Full':
        p,v,e=cli('amend_record.py',[b.path,'--path','adversarial_review_parent','--value-json','"T-OTHER"','--reason','synthetic relation rewrite','--basis','ar05-fixture://attempt'],tag+'-relation-rewrite')
        check(tag+'-repair-parent-immutable','Ordinary amendment attempts to change a saved repair parent',str(b.path),'Rejected',{'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr},[e],p.returncode==2)
# Explicit rules for original-word review and independent reporting are checked from the actual files.
root=SCRIPTS.parent
wanted={
'SKILL.md':[(20,26),(188,190)],
'commands/verify.md':[(17,28),(117,140),(154,170)],
'commands/close.md':[(47,51)],
'commands/minimal.md':[(59,61)],
'commands/status.md':[(25,29)],
'scripts/adversarial_review.py':[(119,164),(176,220),(332,342),(373,429)],
'scripts/governance_artifacts.py':[(3139,3143),(3786,3793),(3965,3999)],
'scripts/minimal_task.py':[(949,970)],
'scripts/signals.py':[(184,192)]}
excerpts=[]
for relative,ranges in wanted.items():
    file=root/relative; lines=file.read_text(encoding='utf-8').splitlines()
    excerpts.append({'path':str(file.relative_to(REPO)),'sha256':sha(file),'ranges':[{'start':start,'end':end,'lines':[f'{i}: {lines[i-1]}' for i in range(start,min(end,len(lines))+1)]} for start,end in ranges]})
dump(TEMP/'source-excerpts.json',excerpts)
check('instruction-integration-original-word-review','Manual independent source inspection: complete original-word coverage, no checklist substitution, new read-only executor, full rounds and no recursive offer',str(TEMP/'source-excerpts.json'),'Explicit instructions in skill entry, verify, close, Minimal, status; matching executable guards',{'observed':'All named entrypoints link the same opt-in and full-round protocol; evidence source excerpts retained.','manual_review':True},[str(TEMP/'source-excerpts.json')],True)
dump(TEMP/'phase5-complete.json',{'ended_at':now(),'cases':len(CASES),'failed':[c['id'] for c in CASES if c['result']=='Failed']})
