from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).resolve().parent/'audit.py'
prefix=base.read_text(encoding='utf-8-sig').split("log('runtime_integrity'")[0]
exec(compile(prefix,str(base),'exec'),globals())
import threading
# Hold the public amendment immediately before its already-validated atomic replacement.
# The public append runs while this writer is paused; no data-validation function is bypassed.
t=create('concurrent-confirmed-finding'); ready(t)
p,d,o,c,e=load(t); old_rounds=len(o['adversarial_review']); old_rev=d['revision']
import governance_artifacts as ga
original_atomic=ga.atomic_write_json
paused=threading.Event(); resume=threading.Event(); thread_errors=[]
def intercept_atomic(path,document):
    if Path(path)==p and threading.current_thread().name=='generic-amendment':
        paused.set()
        if not resume.wait(20): raise RuntimeError('fixture scheduling timeout')
    return original_atomic(path,document)
ga.atomic_write_json=intercept_atomic
new_decision={'outcome':'Rejected','presented':'Fixture verified delivery','response':'Fixture user rejects delivery','decided_by':'synthetic-fixture-user','decided_at':now_utc(),'evidence_ref':'fixture://user-rejection','subject_sha256':user_decision_subject_sha256(c,e,o)}
def amendment_thread():
    try: ga.amend_record(p,dotted_path='user_decision',new_value=new_decision,reason='Fixture delayed user decision',basis='fixture://user-rejection')
    except Exception as ex: thread_errors.append(str(ex))
thread=threading.Thread(target=amendment_thread,name='generic-amendment'); thread.start()
if not paused.wait(20): raise RuntimeError('fixture did not pause amendment')
write(t,round_entry(t,1,findings=[{'id':'F-LOST','summary':'Confirmed fixture issue must remain unresolved','evidence_refs':['fixture://known-problem']}]))
mid=load(t)[2]
mid_state=review_state(mid,load(t)[3])
(ROOT/'concurrency-midpoint.json').write_text(json.dumps(mid,ensure_ascii=False,indent=2),encoding='utf-8')
resume.set(); thread.join(20); ga.atomic_write_json=original_atomic
p,d,o,c,e=load(t)
log('concurrent-finding-before-and-after',thread_errors=thread_errors,mid_state=mid_state,final_state=review_state(o,c),final_user_decision=o['user_decision']['outcome'],validation=validate_task_directory(t),old_revision=old_rev,mid_revision=mid['revision'],final_revision=d['revision'],round_dropped=len(mid['adversarial_review'])>len(o['adversarial_review']),fixture=str(t))
write(t,round_entry(t,2)); write(t,round_entry(t,3))
log('counterexample-lost-confirmed-issue-permits-Passed',state=review_state(load(t)[2],load(t)[3]),validation=validate_task_directory(t),fixture=str(t))
(ROOT/'concurrency-results.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2),encoding='utf-8')
