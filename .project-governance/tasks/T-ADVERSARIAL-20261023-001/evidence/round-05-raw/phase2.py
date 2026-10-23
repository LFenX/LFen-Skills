from independent_suite import *
CASES.extend(json.loads((TEMP/'cases.json').read_text(encoding='utf-8')))
CALLS.extend(json.loads((TEMP/'commands.json').read_text(encoding='utf-8')))
FIXTURES.extend(json.loads((TEMP/'fixtures.json').read_text(encoding='utf-8')))

def bind(f,label):
    p,s,e=f.status(label);assert p.returncode==0,(p.stdout,p.stderr);return s,e

def accepted(name,carrier):
    f=new(name,carrier);f.offer(name+'-offer');f.decision('Accepted',name+'-accept');return f

def report_time_suite(carrier):
    tag='full' if carrier=='Full' else 'min'
    f=accepted(tag+'-evidence',carrier)
    r=f.round(tag+'-initial')
    for key,value,label in [('subject_sha256','0'*64,'wrong-delivery-sha'),('requirements_sha256','1'*64,'wrong-request-sha'),('delivery_task_id','../outside','invalid-task-id'),('session_completed',True,'false-completion-claim'),('report_sha256','2'*64,'false-report-sha'),('delivery_completed_at','2026-01-01T00:00:00Z','false-completion-time'),('delivery_verified_at','2026-01-01T00:00:00Z','false-verification-time'),('started_at','2026-01-01T00:00:00Z','before-delivery'),('started_at','2099-01-01T00:00:00Z','future-start'),('started_at','2026-01-01T00:00:00','naive-start'),('recorded_at','2026-01-01T00:00:00Z','before-prior-record'),('recorded_at','2099-01-01T00:00:00Z','future-record'),('recorded_at','2026-01-01T00:00:00','naive-record')]:
        f.entry({**r,key:value},tag+'-'+label,error=True)
    outside=f.root/'outside-report.md';outside.write_text('synthetic outside report',encoding='utf-8')
    empty=f.task/'evidence/empty.md';empty.write_text('  \n',encoding='utf-8')
    for reference,label in [(str(outside),'outside-report'),(str(empty),'empty-report'),('https://example.test/report','remote-report'),(str(f.task/'evidence/missing.md'),'missing-report')]:
        f.entry({**r,'report_ref':reference},tag+'-'+label,error=True)
    f.entry(r,tag+'-valid-first-report','InProgress')
    f.entry({**r,'round_id':tag+'-copy-id','started_at':now(),'report_ref':str(Path(r['report_ref']).parent/'.'/Path(r['report_ref']).name)},tag+'-alias-report',error=True)
    copy_report=f.task/'evidence/copy.md';copy_report.write_bytes(Path(r['report_ref']).read_bytes())
    f.entry({**r,'round_id':tag+'-copy-content','started_at':now(),'report_ref':str(copy_report)},tag+'-copied-report-content',error=True)
    r2=f.round(tag+'-fresh-second')
    f.entry({**r2,'round_id':r['round_id']},tag+'-duplicate-round-id',error=True)
    f.entry({**r2,'resolutions':[{'finding_id':'UNKNOWN','disposition':'NotAnIssue','reason':'synthetic','evidence_refs':['ar05-fixture://none']}]},tag+'-unknown-resolution',error=True)
    f.entry({**r2,'session_completed':False},tag+'-false-incomplete-claim-on-second',error=True)
    # Mutation invalidates the first report; even an unchanged copied old report stays forbidden.
    Path(r['report_ref']).write_text('AR05 actual evidence mutated after first record.\n',encoding='utf-8')
    s,e=bind(f,tag+'-mutated-report-state')
    check(tag+'-report-mutation-resets','First report content changes in an active session',r['report_ref'],'Stale and clean_streak=0',s,[e],s['status']=='Stale' and s['clean_streak']==0)
    f.entry({**r2,'report_ref':str(copy_report)},tag+'-historic-content-reuse-still-blocked',error=True)
    f.entry(r2,tag+'-first-after-mutation','InProgress')
    f.entry(f.round(tag+'-second-after-mutation'),tag+'-pair-after-mutation','Passed')
    # Finished authorization must remain finished if its report is deleted.
    report=f.task/'evidence'/ (tag+'-second-after-mutation.md')
    report.unlink()
    s,e=bind(f,tag+'-ended-missing-report-state')
    check(tag+'-ended-proof-invalid','An ended session report is absent',str(report),'RestartRequired; streak=0',s,[e],s['status']=='RestartRequired' and s['clean_streak']==0)
    f.entry(f.round(tag+'-after-ended-stale'),tag+'-old-consent-cannot-resume-ended',error=True)
    f.entry({'event':'Blocked','reason':'Synthetic invalid evidence','evidence_refs':['ar05-fixture://missing']},tag+'-ended-stale-blocked-refused',error=True)
    f.decision('Accepted',tag+'-actual-new-decision')
    f.entry(f.round(tag+'-restart-round1'),tag+'-restart-one','InProgress')
    s,e=bind(f,tag+'-restart-one-state')
    check(tag+'-restart-reset','New user choice after ended evidence invalidation',None,'clean_streak=1',s,[e],s['clean_streak']==1)
    # Raw schema/entry errors must preserve the file, too.
    f.entry({'event':'Decision','outcome':'Accepted','response':'synthetic','decided_by':'fixture','evidence_ref':'ar05-fixture://choice','clean_streak':2},tag+'-manual-state-field-refused',error=True)
    return f

def repair_suite(carrier):
    tag='full' if carrier=='Full' else 'min'
    p=accepted(tag+'-repair-parent',carrier)
    p.entry(p.round(tag+'-parent-first'),tag+'-pre-repair-one','InProgress')
    p.entry(p.round(tag+'-parent-issue',findings=[{'id':tag+'-repair-F001','summary':'Synthetic fixture defect','evidence_refs':['ar05-fixture://issue']}]),tag+'-pre-repair-finding','InProgress')
    old,_=bind(p,tag+'-old-binding')
    child=new(tag+'-repair-child',carrier,root=p.root,parent=p.task_id)
    s,e=bind(child,tag+'-repair-managed-state')
    check(tag+'-repair-managed','Authorized completed repair closes with parent relation',str(child.path),'ManagedByParent; direct dependency retained',s,[e],s['status']=='ManagedByParent' and child.contract()['depends_on']==[p.task_id])
    child.entry({'event':'Offer','prompt':'synthetic recursive review','evidence_ref':'ar05-fixture://question'},tag+'-repair-cannot-offer',error=True)
    s,e=bind(p,tag+'-saved-child-invalidates-old')
    check(tag+'-repair-current-version','Saved related repair exists before its first round',str(child.path),'Current child delivery; Stale; streak=0',s,[e],s['status']=='Stale' and s['clean_streak']==0 and s['current_delivery']['task_id']==child.task_id)
    p.entry(p.round(tag+'-old-round-reject',delivery_task_id=p.task_id,subject_sha256=old['subject_sha256']),tag+'-old-delivery-rejected',error=True)
    p.entry(p.round(tag+'-repair-before-save',started_at=p.data()[1]['completed_at']),tag+'-round-before-repair-completion-rejected',error=True)
    p.entry(p.round(tag+'-fixed-round',resolutions=[{'finding_id':tag+'-repair-F001','disposition':'Fixed','reason':'Synthetic new saved repair validated.','evidence_refs':['ar05-fixture://repaired-verification']}]),tag+'-fixed-new-delivery','InProgress')
    p.entry(p.round(tag+'-repair-second'),tag+'-repaired-clean-pair','Passed')
    # Parent validation is tested at the public minimal API; no synthetic history rewrite is used.
    bad=new(tag+'-late-repair',carrier,root=p.root,parent=p.task_id,complete=False)
    actual,ok,e=api(tag+'-ended-parent-repair-refused',lambda:ar.require_review_parent(bad.task,bad.contract(),p.task_id),expect_error=True)
    check(tag+'-parent-ended-refuses-repair','Repair parent already ended',str(bad.task),'Rejected',actual,[e],ok)
    # Direct dependency is mandatory even if a genuine parent opted in.
    p.decision('Accepted',tag+'-parent-restart-for-relation')
    unrelated=new(tag+'-unrelated-child',carrier,root=p.root,complete=False)
    actual,ok,e=api(tag+'-missing-direct-dependency',lambda:ar.require_review_parent(unrelated.task,unrelated.contract(),p.task_id),expect_error=True)
    check(tag+'-repair-direct-dependency','Task lacks direct parent dependency',str(unrelated.task),'Rejected',actual,[e],ok)
    # Same-scope repair may use the other carrier and still stays managed by the original session.
    other='Minimal' if carrier=='Full' else 'Full'
    cross=new(tag+'-cross-repair',other,root=p.root,parent=p.task_id)
    s,e=bind(cross,tag+'-cross-carrier-state')
    check(tag+'-cross-carrier-repair','Full/Minimal repair pairing',str(cross.task),'ManagedByParent',s,[e],s['status']=='ManagedByParent')
    p.entry(p.round(tag+'-cross-first'),tag+'-cross-repair-round','InProgress')
    # Duplicate finding identifiers may not hide already tracked history.
    p.entry(p.round(tag+'-duplicate-finding',findings=[{'id':tag+'-repair-F001','summary':'same old ID','evidence_refs':['ar05-fixture://duplicate']}]),tag+'-finding-id-reuse-rejected',error=True)
    return p,child

try:
    report_time_suite('Full');report_time_suite('Minimal')
    repair_suite('Full');repair_suite('Minimal')
    dump(TEMP/'phase2-complete.json',{'ended_at':now(),'cases':len(CASES),'failed':[c['id'] for c in CASES if c['result']=='Failed']})
except Exception:
    (TEMP/'phase2-error.txt').write_text(traceback.format_exc(),encoding='utf-8');print(traceback.format_exc());save();sys.exit(1)
