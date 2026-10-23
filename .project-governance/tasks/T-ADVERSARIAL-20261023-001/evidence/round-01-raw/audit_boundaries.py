from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).resolve().parent/'audit.py'
prefix=base.read_text(encoding='utf-8-sig').split("log('runtime_integrity'")[0]
exec(compile(prefix,str(base),'exec'),globals())
# A valid repair inherits the original review authorization according to the command card.
t=create('repair-invitation'); ready(t)
write(t,round_entry(t,1,findings=[{'id':'F-INVITE','summary':'Fixture original accepted review needs repair','evidence_refs':['fixture://invite-repro']}]))
repair=create('T-REPAIR-INVITE',False,depends=(t.parent.parent.parent,[t.name]))
signals=[active_task_signal(t),active_task_signal(repair)]
log('counterexample-repair-repeats-optin-recommendation',signals=signals,recommendations=recommendations(signals),fixture=str(t),repair_fixture=str(repair))
# Complete two rounds with distinct reports but shared verification evidence.
t=create('reports-shared-support'); ready(t)
write(t,round_entry(t,1,evidence_refs=['fixture://unique-full-report-one','fixture://shared-original-and-test-log']))
attempt('distinct-reports-share-legitimate-support',t,round_entry(t,2,evidence_refs=['fixture://unique-full-report-two','fixture://shared-original-and-test-log']),expected='accept')
# Recommendations have no review-continuation prompt for no reply or negative decisions.
for status in ('NotOffered','AwaitingUser','Declined','Deferred','Stopped','InProgress','Blocked','Passed','LegacyUntracked','NotApplicable'):
    log('recommendation-'+status,recommendations=recommendations([{'engineering_recorded':True,'pending_acceptance':True,'adversarial_review':{'status':status}}]))
# Engineering status other than Implemented is not eligible to offer (pure state boundary).
for status in ('Blocked','Cancelled','Superseded','Failed'):
    outcome={'status':status,'completed_at':'2026-10-23T00:00:00Z','adversarial_review':[]}
    initial=review_state(outcome)
    outcome['adversarial_review']=[{'event':'Offer','recorded_at':now_utc(),'prompt':'Fixture question','evidence_ref':'fixture://question'}]
    try: review_state(outcome); error='accepted'
    except Exception as ex: error=str(ex)
    log('unfinished-state-'+status,initial=initial,offer=error)
# Guards for history mutations through the generic public amendment.
t=create('history-guard'); ready(t)
try:
    amend_record(load(t)[0],dotted_path='adversarial_review',new_value=[],reason='Fixture attempts erase',basis='fixture://erase')
    error='accepted'
except Exception as ex: error=str(ex)
log('Full-generic-amendment-review-erase',error=error,validation=validate_task_directory(t))
# No review field is not automatically enrolled or marked Passed, including old terminal status.
log('historical-status-preservation',old_outcome={'status':'Implemented','completed_at':'2026-08-15T00:00:00Z'},review=review_state({'status':'Implemented','completed_at':'2026-08-15T00:00:00Z'}))
(ROOT/'boundary-results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2),encoding='utf-8')
