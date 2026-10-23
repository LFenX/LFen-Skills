import review_harness as h, json, copy
from pathlib import Path
h.CASES=json.loads((h.BASE/'cases.json').read_text(encoding='utf-8')); h.COUNTER=len(list(h.RAW.glob('*.json')))
# Public amendment of a completed review's verified result must not silently authorize a new session.
t=h.fresh('Full','ended_session')
h.offer(t,'ended-offer'); h.decision(t,'ended-start')
h.entry(t,'ended-clean1',h.round_value(t,'ended-clean1'),expected={'status':'InProgress','clean_streak':1})
h.entry(t,'ended-clean2',h.round_value(t,'ended-clean2'),expected={'status':'Passed','clean_streak':2})
p=h.outcome_path(t); checks=h.read_outcome(t)['verification']; checks[0]['summary']='Synthetic verification receipt description corrected after review ended'
ip=h.write(h.BASE/'inputs'/'ended-amend-verification.json',checks)
raw,res,rp=h.cli('amend_record.py',[p,'--path','verification','--value-json-file',ip,'--reason','Correct evidenced result description','--basis','ar04://synthetic-correction'],'ended-amend')
h.check('ended-amend-public-entry',raw,{'exit_code':0},raw,raw['exit_code']==0,{'path':'verification','value':checks},rp)
h.query(t,'ended-now-stale',{'status':'Stale','clean_streak':0})
h.entry(t,'ended-round-without-new-decision',h.round_value(t,'ended-new-round'),expected_rc=2)
# Synthetic legacy records: only historical reading is under test; no actual historical human facts are asserted.
for carrier in ['Full','Minimal']:
    tag=carrier.lower(); t=h.fresh(carrier,tag+'_legacy_history'); h.offer(t,tag+'-legacy-offer'); h.decision(t,tag+'-legacy-start')
    doc=h.g.read_json(h.outcome_path(t)); out=doc if carrier=='Full' else doc['task_outcome']; _,_,_,contract,events=h.a._read_saved(t)
    for i in [1,2]:
        v={'event':'Round','recorded_at':h.now(),'round_id':tag+'-legacy-'+str(i),'started_at':h.now(),'reviewer':'synthetic-legacy-reviewer-'+str(i),'delivery_task_id':t.name,'subject_sha256':h.g.user_decision_subject_sha256(contract,events,out),'requirements_sha256':h.a._legacy_requirements_subject(contract),'coverage':'Complete','unreviewed_items':[],'evidence_refs':['ar04://synthetic-old-report-'+str(i)],'findings':[],'resolutions':[]}; v['recorded_at']=h.now(); out['adversarial_review'].append(v)
    h.g.atomic_write_json(h.outcome_path(t),doc)
    h.query(t,tag+'-legacy-already-converged',{'status':'LegacyNotRevalidated','clean_streak':0})
    h.entry(t,tag+'-legacy-round-before-new-decision',h.round_value(t,tag+'-legacy-unauthorized'),expected_rc=2)
    if carrier=='Full':
        ip=h.write(h.BASE/'inputs'/'legacy-metadata.json','Synthetic survey explanation corrected')
        raw,res,rp=h.cli('amend_record.py',[t/'before.json','--path','clarification.basis','--value-json-file',ip,'--reason','Correct explanatory metadata without changing words','--basis','ar04://correction'],'legacy-metadata-correction')
        h.check('legacy-metadata-public-amend',raw,{'exit_code':0},raw,raw['exit_code']==0,{'path':'clarification.basis'},rp)
        h.query(t,'legacy-corrected-explanation-still-ended',{'status':'LegacyNotRevalidated','clean_streak':0})
        h.entry(t,'legacy-round-after-metadata-without-new-decision',h.round_value(t,'legacy-reopened-by-metadata'),expected_rc=2)
    h.decision(t,tag+'-legacy-real-new-decision')
    h.entry(t,tag+'-legacy-current-one',h.round_value(t,tag+'-legacy-current-one'),expected={'status':'InProgress','clean_streak':1})
    h.entry(t,tag+'-legacy-current-two',h.round_value(t,tag+'-legacy-current-two'),expected={'status':'Passed','clean_streak':2})
h.write(h.BASE/'supplement-summary.json',{'at':h.now(),'case_count':len(h.CASES),'failed':[x for x in h.CASES if x['result']=='Failed']})
print(json.dumps({'case_count':len(h.CASES),'failed':[x['name'] for x in h.CASES if x['result']=='Failed']},ensure_ascii=False))
