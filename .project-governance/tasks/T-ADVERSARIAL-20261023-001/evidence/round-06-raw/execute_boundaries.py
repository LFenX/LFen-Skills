from review_cases import *
CASES.extend(json.loads((ARCHIVE/'cases.json').read_text(encoding='utf-8')))
BASE=ARCHIVE/'boundary-fixtures'

def finishopen(task,carrier,parent=None,status='Implemented'):
    if carrier=='Full':
        if not ga.read_jsonl(task/'run.jsonl')[-1]['event_type']=='run_finished':
            ga.append_run_event(task,run_id=task.name+'-run',attempt_id='A01',event_type='run_finished',status='succeeded',summary='Synthetic complete')
        return str(ga.close_task(task,status=status,established_facts=['Synthetic verified'],actual_changes=['Synthetic label'],verification=[{'result':'Passed','summary':'Synthetic check','evidence_refs':[SYN+'/repair-check']}],review_parent_task_id=parent))
    return str(mt.close_minimal_record(task,status=status,established_facts=['Synthetic verified'],actual_changes=['Synthetic label'],verification=['Passed::Synthetic check::'+SYN+'/repair-check'],review_parent_task_id=parent))

def yes(task,rid,**kwargs):write_entry(task,roundentry(task,rid,**kwargs));return ar.review_status(task)

def cli(argv,label):
    cmd=[sys.executable,'-X','utf8']+[str(x) for x in argv]
    cp=subprocess.run(cmd,cwd=ARCHIVE,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    data={'command':cmd,'cwd':str(ARCHIVE),'returncode':cp.returncode,'stdout':cp.stdout,'stderr':cp.stderr,'at':stamp()}
    jwrite(RAW/(label+'-command.json'),data)
    return data

for carrier in ['Full','Minimal']:
    k=carrier[0];root=BASE/('repair-'+carrier)
    parent=create(root,'T-PARENT-'+k,carrier);authorize(parent)
    yes(parent,'original-clean')
    findings=[{'id':'SYN-R01','summary':'Synthetic repair needed','evidence_refs':[SYN+'/repair-needed']}]
    yes(parent,'repair-discovered',findings=findings)
    repair_carrier='Minimal' if carrier=='Full' else 'Full'
    repair=create(root,'T-REPAIR-'+k,repair_carrier,parent=parent.name)
    case('R'+k+'01','New explicitly associated saved repair supersedes old current delivery before any round',{'parent':parent.name,'repair':repair.name,'mixed_carrier':repair_carrier},'parent Stale / streak 0 / current repair; repair ManagedByParent',lambda:{'parent':ar.review_status(parent),'repair':ar.review_status(repair)},lambda a:a['accepted'] and a['value']['parent']['status']=='Stale' and a['value']['parent']['current_delivery']['task_id']==repair.name and a['value']['parent']['clean_streak']==0 and a['value']['repair']['status']=='ManagedByParent')
    case('R'+k+'02','Old delivery cannot continue count after saved repair',roundentry(parent,'stale-old'), 'Rejected',lambda:write_entry(parent,roundentry(parent,'stale-old-again')),reject)
    fix=[{'finding_id':'SYN-R01','disposition':'Fixed','reason':'SYNTHETIC verified subsequent repair','evidence_refs':[SYN+'/fixed-new-delivery']}]
    case('R'+k+'03','Fixed binds newly verified saved repair and starts clean count anew',{'delivery':repair.name,'resolution':fix},'InProgress / clean 1 / no open findings',lambda:yes(parent,'repaired-first',delivery=repair,resolutions=fix),lambda a:a['accepted'] and a['value']['status']=='InProgress' and a['value']['clean_streak']==1 and a['value']['open_findings']==[])
    case('R'+k+'04','Repair does not recursively offer a new review',offer(repair),'Rejected',lambda:write_entry(repair,offer(repair)),reject)
    case('R'+k+'05','Second full clean round must remain on repaired version',{'delivery':repair.name},'Passed / clean 2',lambda:yes(parent,'repaired-second',delivery=repair),lambda a:a['accepted'] and a['value']['status']=='Passed' and a['value']['clean_streak']==2)
    case('R'+k+'06','Ended parent cannot grant repair suppression',{'parent':parent.name},'Rejected',lambda:ar.require_review_parent(repair,saved(repair)[2],parent.name),reject)
    # Public close path must reject missing consent. New ready repair stays unclosed.
    denied_root=BASE/('denied-'+carrier)
    denied_parent=create(denied_root,'T-DENIED-'+k,carrier)
    candidate=create(denied_root,'T-DENIED-REPAIR-'+k,carrier,parent=denied_parent.name,finish=False)
    case('R'+k+'07','Unconsented parent cannot suppress repair opt-in',{'task':candidate.name,'parent':denied_parent.name},'Rejected / no saved outcome',lambda:finishopen(candidate,carrier,parent=denied_parent.name),reject)
    case('R'+k+'08','Unfinished engineering cannot offer optional review',offer(candidate),'Rejected',lambda:write_entry(candidate,offer(candidate)),reject)
    # Active session recovers from a blocker without recursively reauthorizing.
    active_root=BASE/('blocked-resume-'+carrier)
    active=create(active_root,'T-BLOCKED-'+k,carrier);authorize(active)
    yes(active,'before-block')
    write_entry(active,{'event':'Blocked','recorded_at':stamp(),'reason':'SYNTHETIC environment gap','evidence_refs':[SYN+'/blocked-env']})
    case('R'+k+'09','Existing authorization survives safe same-scope failure recovery',{'task':active.name},'InProgress / clean 1 after blocker resolution',lambda:yes(active,'after-block'),lambda a:a['accepted'] and a['value']['status']=='InProgress' and a['value']['clean_streak']==1)
    e=roundentry(active,'forged-completion');e['session_completed']=False
    # This would actually produce the second clean count, so supplied false must fail atomically.
    before=snapshot(active)
    a=case('R'+k+'10','Caller cannot suppress computed session-end receipt',e,'Rejected without changing stored outcome',lambda:write_entry(active,e),reject)
    calllog('false-receipt-atomicity',{'task':active,'before':before},snapshot(active))
    # Corrupt an already registered report in a synthetic fixture only.
    first=saved(active)[1]['adversarial_review'][-1]
    rp=active.parents[2]/first['report_ref'];old=rp.read_text(encoding='utf-8');rp.write_text('SYNTHETIC changed after registration',encoding='utf-8')
    case('H'+k+'01','A changed report invalidates an active clean proof',{'report':str(rp)},'Stale / clean 0',lambda:ar.review_status(active),lambda a:a['accepted'] and a['value']['status']=='Stale' and a['value']['clean_streak']==0)
    dup=roundentry(active,'old-content-copy',report_content=old)
    case('H'+k+'02','Changing original report does not erase historical-content deduplication',dup,'Rejected',lambda:write_entry(active,dup),reject)
    case('H'+k+'03','Stale active session can continue existing authorization with a new report',{'task':active.name},'InProgress / clean 1',lambda:yes(active,'after-stale'),lambda a:a['accepted'] and a['value']['clean_streak']==1)
    yes(active,'now-ended')
    ended_last=saved(active)[1]['adversarial_review'][-1]
    end_report=active.parents[2]/ended_last['report_ref'];end_report.unlink()
    case('H'+k+'04','Deleting ended-session report invalidates proof but retains ended authorization boundary',{'deleted_report':str(end_report)},'RestartRequired / clean 0',lambda:ar.review_status(active),lambda a:a['accepted'] and a['value']['status']=='RestartRequired' and a['value']['clean_streak']==0)
    case('H'+k+'05','Ended stale proof cannot resume under old consent',roundentry(active,'no-new-decision'),'Rejected',lambda:write_entry(active,roundentry(active,'no-new-decision2')),reject)
    write_entry(active,decision())
    case('H'+k+'06','Fresh actual start after invalid ended proof creates a new session',{'task':active.name},'InProgress / clean 1',lambda:yes(active,'fresh-after-ended'),lambda a:a['accepted'] and a['value']['status']=='InProgress' and a['value']['clean_streak']==1)
    # Simulated legacy records are fabricated solely in Temp and explicitly labelled.
    legacy_root=BASE/('legacy-'+carrier)
    legacy=create(legacy_root,'T-LEGACY-'+k,carrier)
    lp,lo,lc,le=saved(legacy)
    doc=ga.read_json(lp)
    (doc if carrier=='Full' else doc['task_outcome']).pop('adversarial_review')
    jwrite(lp,doc)
    case('H'+k+'07','Old result without review field stays compatible and untracked',{'task':legacy.name,'synthetic_legacy':True},'LegacyUntracked / valid',lambda:{'state':ar.review_status(legacy),'validation':ga.validate_task_directory(legacy)},lambda a:a['accepted'] and a['value']['state']['status']=='LegacyUntracked' and a['value']['validation']==[])
    case('H'+k+'08','Legacy result is not enrolled by silently inventing an offer',offer(legacy),'Rejected',lambda:write_entry(legacy,offer(legacy)),reject)
    # Simulate pre-report-binding clean rounds using explicit legacy-shaped inputs.
    historical=copy.deepcopy(lo);historical['adversarial_review']=[]
    at=stamp();historical['adversarial_review']=[dict(offer(legacy),recorded_at=at),dict(decision(),recorded_at=at)]
    legacy_req=hashlib.sha256(json.dumps({'request_snapshot':lc.get('request_snapshot'),'clarification':lc.get('clarification')},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    for i in [1,2]:
        historical['adversarial_review'].append({'event':'Round','recorded_at':stamp(),'started_at':at,'round_id':'legacy-'+str(i),'reviewer':'synthetic-historical','delivery_task_id':legacy.name,'subject_sha256':ga.user_decision_subject_sha256(lc,le,lo),'requirements_sha256':legacy_req,'coverage':'Complete','unreviewed_items':[],'evidence_refs':[SYN+'/legacy-round/'+str(i)],'findings':[],'resolutions':[]})
        at=historical['adversarial_review'][-1]['recorded_at']
    jwrite(RAW/('H'+k+'09-historical-input.json'),{'outcome':historical,'contract':lc})
    case('H'+k+'09','Pre-report-binding clean pair does not become current Passed',{'synthetic_legacy_input':'raw/H'+k+'09-historical-input.json'},'LegacyNotRevalidated / clean 0',lambda:ar.review_state(historical,lc),lambda a:a['accepted'] and a['value']['status']=='LegacyNotRevalidated' and a['value']['clean_streak']==0)
    print('Completed repair/history',carrier,flush=True)

# Current delivery ambiguity and wrong project require a safe reject.
root=BASE/'ambiguous';p=create(root,'T-AMB-P');authorize(p);yes(p,'base-clean')
a=create(root,'T-AMB-A','Full',parent=p.name);b=create(root,'T-AMB-B','Minimal',parent=p.name)
bp,bo,bc,be=saved(b);bd=ga.read_json(bp);ao=saved(a)[1]
bd['task_outcome']['completed_at']=ao['completed_at'];bd['completed_at']=ao['completed_at']
# Preserve ledger time ordering: this simulation uses two completions at the later original timestamp.
common_time=max(ao['completed_at'],bo['completed_at'])
ap,_,_,_=saved(a);ad=ga.read_json(ap);ad['completed_at']=common_time;jwrite(ap,ad)
bd['task_outcome']['completed_at']=common_time;bd['completed_at']=common_time;jwrite(bp,bd)
case('R-A01','Same latest completion time cannot choose between two saved repairs',{'parent':p.name,'repairs':[a.name,b.name]},'current_delivery Ambiguous / streak0; new round rejected',lambda:{'state':ar.review_status(p),'rejection':_attempt_ambiguous if False else None},lambda x:x['accepted'] and x['value']['state']['current_delivery'].get('status')=='Ambiguous' and x['value']['state']['clean_streak']==0)
case('R-A02','Ambiguous latest delivery cannot count a candidate round',{'task':p.name,'delivery':a.name},'Rejected',lambda:write_entry(p,roundentry(p,'ambiguous-round',delivery=a)),reject)
# Requirements binding includes source words, conditions, original question/default context, excludes explanatory metadata.
_,out,c,ev=saved(p)
cl=copy.deepcopy(c);cl['clarification']['rounds']=[{'ordinal':1,'exchanges':[{'question':'SYNTHETIC question','changes':['scope'],'recommended_default':'SYNTHETIC default','answer':'SYNTHETIC answer','answer_state':'Explicit'}]}]
q=ar.requirements_subject(cl)
meta=copy.deepcopy(cl);meta['request_snapshot']['captured_at']='2026-01-01T00:00:00Z';meta['clarification']['basis']='SYNTHETIC corrected metadata';meta['clarification']['survey_refs']=['changed-metadata.md']
variants=[]
for field in ['question','recommended_default','answer','changes','answer_state']:
    v=copy.deepcopy(cl);ex=v['clarification']['rounds'][0]['exchanges'][0];ex[field]=['changed'] if field=='changes' else 'SYNTHETIC changed';variants.append({'field':field,'different':ar.requirements_subject(v)!=q})
word=copy.deepcopy(cl);word['request_snapshot']['text']+=' Extra synthetic requirement.'
case('B01','Requirements digest binds exact source words and clarification context while metadata correction stays stable',{'synthetic_contract':cl,'changes':variants},'word/context changes hash, capture/basis/survey correction does not',lambda:{'metadata_same':ar.requirements_subject(meta)==q,'words_different':ar.requirements_subject(word)!=q,'context_changes':variants},lambda a:a['accepted'] and a['value']['metadata_same'] and a['value']['words_different'] and all(v['different'] for v in a['value']['context_changes']))

# CLI-only reproduction of absent consent proof being treated as opt-in.
root=BASE/'cli-blank';t=create(root,'T-CLI-BLANK','Full')
commands=[]
def cliappend(entry,label):
    ep=RAW/(label+'-entry.json');jwrite(ep,entry)
    result=cli([SKILL/'scripts/adversarial_review.py',t,'--entry-json-file',ep,'--reason','Synthetic independent CLI boundary','--basis',SYN+'/cli'],label)
    commands.append(label+'-command.json');return result
cliappend(offer(t),'CLI-BLANK-OFFER')
e=decision();e.update(response=' \t ',decided_by=' ',evidence_ref='\t')
case('CLI01','Public CLI rejects absent response/actor/source rather than treating enum Accepted as proof',e,'exit 2; AwaitingUser',lambda:cliappend(e,'CLI-BLANK-DECISION'),lambda a:a['accepted'] and a['value']['returncode']==2)
for n in [1,2]:cliappend(roundentry(t,'cli-round-'+str(n)),'CLI-BLANK-ROUND-'+str(n))
case('CLI02','Absent consent proof cannot produce a passed session',{'cli_commands':commands},'status must remain AwaitingUser with no counted rounds',lambda:cli([SKILL/'scripts/adversarial_review.py',t],'CLI-BLANK-STATE'),lambda a:a['accepted'] and json.loads(a['value']['stdout'])['status']=='AwaitingUser')
# Distinct valid CLI repair-close and state/query surfaces.
for carrier in ['Full','Minimal']:
    k=carrier[0];root=BASE/('cli-repair-'+carrier)
    parent=create(root,'T-CLI-P-'+k,carrier);authorize(parent)
    ready=create(root,'T-CLI-R-'+k,carrier,parent=parent.name,finish=False)
    if carrier=='Full':
        ga.append_run_event(ready,run_id=ready.name+'-run',attempt_id='A01',event_type='run_finished',status='succeeded',summary='Synthetic CLI close readiness')
        args=[SKILL/'scripts/close_task.py',ready,'--status','Implemented','--fact','Synthetic verified','--change','Synthetic edit','--verification','Passed::Synthetic verified::'+SYN+'/cli-verified','--review-parent-task-id',parent.name]
    else:
        args=[SKILL/'scripts/manage_minimal_task.py','close',ready,'--status','Implemented','--fact','Synthetic verified','--change','Synthetic edit','--verification','Passed::Synthetic verified::'+SYN+'/cli-verified','--review-parent-task-id',parent.name]
    case('CLI'+k+'03','Documented close flag saves explicit repair association',{'args':[str(v) for v in args]},'exit0 / ManagedByParent',lambda:{'cli':cli(args,'CLI-'+k+'-REPAIR-CLOSE'),'state':ar.review_status(ready)},lambda a:a['accepted'] and a['value']['cli']['returncode']==0 and a['value']['state']['status']=='ManagedByParent')
    case('CLI'+k+'04','Read-only CLI subject query matches actual delivery hash',{'task':ready.name},'exit0 / subject hash equals saved subject',lambda:cli([SKILL/'scripts/get_approval_subject.py',ready],'CLI-'+k+'-SUBJECT'),lambda a:a['accepted'] and a['value']['returncode']==0 and ga.user_decision_subject_sha256(saved(ready)[2],saved(ready)[3],saved(ready)[1]) in a['value']['stdout'])
    case('CLI'+k+'05','Signals CLI exposes managed repair and active parent',{'root':str(root)},'exit0 / ManagedByParent and InProgress',lambda:cli([SKILL/'scripts/signals.py','--project-root',root],'CLI-'+k+'-SIGNALS'),lambda a:a['accepted'] and a['value']['returncode']==0 and 'ManagedByParent' in a['value']['stdout'] and 'InProgress' in a['value']['stdout'])

jwrite(ARCHIVE/'cases.json',CASES)
print('TOTAL',len(CASES),'FAILED',sum(c['result']=='Failed' for c in CASES),flush=True)
