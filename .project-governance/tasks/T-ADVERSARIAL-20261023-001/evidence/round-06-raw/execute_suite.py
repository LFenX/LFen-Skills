from review_cases import *
BASE=ARCHIVE/'executed-fixtures'

def query(task):return ar.review_status(task)
def recase(cid,cond,entry,task,expected='Reject invalid append'):
    before=snapshot(task)
    def op():
        try:return write_entry(task,entry)
        finally:calllog('append_snapshot',{'case':cid,'before':before},snapshot(task))
    a=case(cid,cond,entry,expected,op,reject)
    return a

def positive(cid,cond,task,entry,expected_status,streak=None):
    def op():
        write_entry(task,entry);return query(task)
    return case(cid,cond,entry,{'status':expected_status,'clean_streak':streak},op,lambda a:a['accepted'] and a['value']['status']==expected_status and (streak is None or a['value']['clean_streak']==streak))

def fresh(group,carrier):return create(BASE/group/carrier,'T-'+group.upper().replace('_','-')+'-'+carrier.upper(),carrier)

for carrier in ['Full','Minimal']:
    k=carrier[0]
    t=fresh('lifecycle',carrier)
    case(k+'01','Engineering outcome initializes independent Pending and NotOffered',{'task':str(t)},'Implemented / Pending / NotOffered / streak=0',lambda:{'outcome':saved(t)[1],'state':query(t)},lambda a:a['accepted'] and a['value']['outcome']['user_decision']=={'outcome':'Pending'} and a['value']['state']['status']=='NotOffered')
    recase(k+'02','Decision cannot precede actual post-completion Offer',decision(),t)
    recase(k+'03','Round cannot precede explicit consent',roundentry(t,'no-consent'),t)
    early=offer(t);early['recorded_at']='2026-01-01T00:00:00Z'
    recase(k+'04','Offer must occur after saved engineering completion',early,t)
    positive(k+'05','Actual offer waits for user',t,offer(t),'AwaitingUser',0)
    recase(k+'06','Silence after offer does not authorize review',roundentry(t,'silent'),t)
    positive(k+'07','Refusal is retained independently of engineering outcome',t,decision('Declined'),'Declined',0)
    recase(k+'08','Refusal cannot start review',roundentry(t,'declined'),t)
    positive(k+'09','Deferred choice preserves result and does not opt in',t,decision('Deferred'),'Deferred',0)
    recase(k+'10','Deferral cannot start review',roundentry(t,'deferred'),t)
    case(k+'11','Declined/Deferred recommendations do not prompt auto-start',{'task':str(t)},'No continue-review or re-offer recommendation',lambda:signals.recommendations([signals.active_task_signal(t)]),lambda a:a['accepted'] and all('已获同意' not in x['reason'] and '主动询问' not in x['reason'] for x in a['value']))
    positive(k+'12','Later real explicit start reuses existing offer',t,decision(),'InProgress',0)
    recase(k+'13','Active session cannot recursively offer',offer(t),t)
    recase(k+'14','Active session does not replace consent with a second Accepted',decision(),t)
    positive(k+'15','One complete clean round counts one',t,roundentry(t,'complete-one'),'InProgress',1)
    positive(k+'16','Incomplete round resets streak',t,roundentry(t,'incomplete',coverage='Incomplete',unreviewed=['Synthetic unavailable branch']),'InProgress',0)
    positive(k+'17','Complete claim with unreviewed item cannot count',t,roundentry(t,'unreviewed',unreviewed=['Synthetic unexamined boundary']),'InProgress',0)
    f=[{'id':'SYN-F01','summary':'Synthetic counterexample','evidence_refs':[SYN+'/finding']}]
    positive(k+'18','Any confirmed finding resets streak and stays open',t,roundentry(t,'finding',findings=f),'InProgress',0)
    positive(k+'19','A clean-looking next round cannot ignore unresolved findings',t,roundentry(t,'unresolved'),'InProgress',0)
    resolution={'finding_id':'SYN-F01','disposition':'Fixed','reason':'SYNTHETIC same-version fix claim','evidence_refs':[SYN+'/same-version-fix']}
    recase(k+'20','Fixed cannot claim same verified subject',roundentry(t,'same-fix',resolutions=[resolution]),t)
    resolution['disposition']='NotAnIssue';resolution['reason']='SYNTHETIC evidential false-positive disposal'
    positive(k+'21','Evidenced false-positive disposition closes known finding',t,roundentry(t,'false-positive',resolutions=[resolution]),'InProgress',1)
    positive(k+'22','Blocked resets one clean round',t,{'event':'Blocked','recorded_at':stamp(),'reason':'SYNTHETIC environment unavailable','evidence_refs':[SYN+'/block']},'Blocked',0)
    positive(k+'23','Explicit user stop ends active work',t,decision('Stopped'),'Stopped',0)
    recase(k+'24','Stopped session rejects more rounds',roundentry(t,'after-stop'),t)
    positive(k+'25','Fresh explicit start resumes stopped session',t,decision(),'InProgress',0)
    e=roundentry(t,'clock');e['started_at']='2026-01-01T00:00:00Z'
    recase(k+'26','Round cannot start before opt-in/verified delivery',e,t)
    e=roundentry(t,'future');e['recorded_at']=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
    recase(k+'27','Future timestamps are rejected',e,t)
    e=roundentry(t,'no-zone');e['recorded_at']=datetime.now().isoformat()
    recase(k+'28','Timestamp without timezone is rejected',e,t)
    e=roundentry(t,'forged-subject');e['subject_sha256']='0'*64
    recase(k+'29','Subject hash must bind actual verified saved delivery',e,t)
    e=roundentry(t,'forged-words');e['requirements_sha256']='1'*64
    recase(k+'30','Requirements hash must bind original full words/context',e,t)
    e=roundentry(t,'report-outside');e['report_ref']=str(ARCHIVE/'outside-report.md');Path(e['report_ref']).write_text('Synthetic out-of-task report',encoding='utf-8')
    recase(k+'31','Report must be inside original task',e,t)
    e=roundentry(t,'report-empty');Path(e['report_ref']).write_text(' \n\t',encoding='utf-8')
    recase(k+'32','Whitespace-only report cannot count as actual report',e,t)
    first=roundentry(t,'final-one',report_content='Synthetic clean final round one '+carrier)
    positive(k+'33','New complete round starts streak after interruption',t,first,'InProgress',1)
    duplicate=roundentry(t,'duplicate-copy',report_content=Path(first['report_ref']).read_text(encoding='utf-8'))
    recase(k+'34','Copied report bytes cannot make second clean round',duplicate,t)
    alias=roundentry(t,'duplicate-alias');alias['report_ref']=str(Path(first['report_ref']).parent/'..'/'evidence'/Path(first['report_ref']).name)
    recase(k+'35','Alias to first report cannot make second clean round',alias,t)
    positive(k+'36','Second complete distinct same-version round ends session',t,roundentry(t,'final-two'),'Passed',2)
    recase(k+'37','Passed session rejects extra round without new real decision',roundentry(t,'after-passed'),t)
    recase(k+'38','Passed session rejects Blocked without new real decision',{'event':'Blocked','recorded_at':stamp(),'reason':'SYNTHETIC post-session block','evidence_refs':[SYN+'/ended']},t)
    path,out,b,events=saved(t)
    case(k+'39','User Acceptance remains Pending after review passes',{'task':str(t)},'Pending',lambda:out['user_decision'],lambda a:a['accepted'] and a['value']=={'outcome':'Pending'})
    recase(k+'40','User cannot predeclare uncomputed session_completed',dict(roundentry(t,'false-receipt'),session_completed=True),t)
    positive(k+'41','Restart passed session requires actual new Accepted and resets count',t,decision(),'InProgress',0)
    positive(k+'42','New session first clean round is one',t,roundentry(t,'new-session-one'),'InProgress',1)
    def render():
        _,out,b,ev=saved(t)
        markdown=ga.render_task_review(b,out,task_dir=t) if carrier=='Full' else mt.render_minimal_review(ga.read_json(t/'task-record.json'),task_dir=t)
        target=RAW/(k+'43-review.md');target.write_text(markdown,encoding='utf-8')
        return {'signal':signals.active_task_signal(t),'markdown':target.relative_to(ARCHIVE).as_posix()}
    case(k+'43','Public signals and rendered review agree with authoritative state',{'task':str(t)},'InProgress / clean=1 in signal and Markdown',render,lambda a:a['accepted'] and a['value']['signal']['adversarial_review']['clean_streak']==1 and 'InProgress' in (ARCHIVE/a['value']['markdown']).read_text(encoding='utf-8'))
    generic='adversarial_review' if carrier=='Full' else 'task_outcome.adversarial_review'
    case(k+'44','Generic amendment cannot erase review history',{'path':str(path),'field':generic,'new':[]},'Rejected',lambda:ga.amend_record(path,dotted_path=generic,new_value=[],reason='SYNTHETIC erasure',basis=SYN),reject)
    def ud():
        p,o,c,e=saved(t)
        d={'outcome':'Rejected','presented':'SYNTHETIC actual fixture delivery','response':'SYNTHETIC reject acceptance','decided_by':'synthetic-test-actor','decided_at':stamp(),'evidence_ref':SYN+'/acceptance-rejected','subject_sha256':ga.user_decision_subject_sha256(c,e,o)}
        if carrier=='Full':ga.amend_record(p,dotted_path='user_decision',new_value=d,reason='Synthetic independent acceptance',basis=SYN)
        else:mt.record_minimal_review(t,user_decision=d,reason='Synthetic independent acceptance',basis=SYN)
        return {'outcome':saved(t)[1]['user_decision'],'review':query(t)}
    case(k+'45','Acceptance rejection is independent of review state',{'task':str(t)},'Acceptance Rejected while review stays InProgress clean=1',ud,lambda a:a['accepted'] and a['value']['outcome']['outcome']=='Rejected' and a['value']['review']['clean_streak']==1)
    print('Completed lifecycle',carrier,flush=True)

# A blank response/actor/source contains no real choice; public boundary must reject it.
for carrier in ['Full','Minimal']:
    t=fresh('blank_authority',carrier);write_entry(t,offer(t))
    e=decision();e.update(response=' \t ',decided_by='   ',evidence_ref='\t')
    case(carrier[0]+'46','Whitespace-only response/actor/source must not authorize a session',e,'Reject absent actual response, actor and source',lambda:write_entry(t,e),reject)
    if query(t)['status']=='InProgress':
        write_entry(t,roundentry(t,'blank-consent-one'))
        write_entry(t,roundentry(t,'blank-consent-two'))
        calllog('blank-authority-confirmation',{'task':t},query(t))

jwrite(ARCHIVE/'cases.json',CASES)
print('TOTAL',len(CASES),'FAILED',sum(c['result']=='Failed' for c in CASES),flush=True)
