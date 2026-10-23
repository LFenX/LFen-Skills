from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import copy, importlib.util, json, threading, traceback, hashlib
from pathlib import Path
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent/"boundary-run";BASE.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location("h",Path(__file__).resolve().parent/"audit.py");h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
ga,mt,ar=h.ga,h.mt,h.ar
cases=[];errors=[]
def check(cid,inp,expected,actual,ok):
    cases.append({"id":cid,"input":inp,"expected":expected,"actual":actual,"result":"Passed" if ok else "Failed"})
    h.dump(BASE/"boundary-results.json",{"cases":cases,"errors":errors})
    print(cid,cases[-1]["result"],flush=True)
def deny(cid,path,inp,fn):
    sha=h.digest(path) if path.exists() else None
    try:fn();a={"denied":False}
    except ga.GovernanceError as exc:a={"denied":True,"message":str(exc)}
    a["bytes_unchanged"]=h.digest(path)==sha if sha else not path.exists()
    check(cid,inp,"Deny invalid transition/input and preserve stored bytes",a,a["denied"] and a["bytes_unchanged"])
def close_ready(t,minimal,parent):
    if minimal:
        return mt.close_minimal_record(t,status="Implemented",established_facts=["Synthetic ready"],actual_changes=["Synthetic change"],verification=["Passed::Independent synthetic check::synthetic-ar02://boundary"],review_parent_task_id=parent)
    ev=ga.read_jsonl(t/"run.jsonl")
    if ev[-1]["event_type"]!="run_finished":
        ga.append_run_event(t,run_id=ev[0]["run_id"],attempt_id="A-01",event_type="run_finished",summary="Synthetic ready for parent linkage validation",status="succeeded")
    return ga.close_task(t,status="Implemented",established_facts=["Synthetic ready"],actual_changes=["Synthetic change"],verification=[{"result":"Passed","summary":"Independent synthetic check","evidence_refs":["synthetic-ar02://boundary"]}],review_parent_task_id=parent)
def transitions(minimal):
    tag="MIN" if minimal else "FULL"
    t=h.build(BASE/tag,"T-BOUND-"+tag,minimal);h.optin(t)
    p=h.snap(t)[0]
    deny(tag+"-ACTIVE-OFFER",p,{"event":"Offer while accepted"},lambda:h.offer(t))
    deny(tag+"-ACTIVE-ACCEPT",p,{"event":"duplicate Accepted while active"},lambda:h.decision(t))
    deny(tag+"-ACTIVE-DECLINE",p,{"event":"Declined while active; caller must record Stopped"},lambda:h.decision(t,"Declined"))
    h.round_(t,1)
    h.round_(t,2,coverage="Incomplete",unreviewed_items=[])
    a=ar.review_status(t);check(tag+"-COVERAGE-INCOMPLETE",{"coverage":"Incomplete","unreviewed_items":[]},"clean streak resets even without enumerated unchecked items",a,a["clean_streak"]==0)
    h.round_(t,3)
    h.round_(t,4,coverage="Complete",unreviewed_items=["Not reviewed branch"])
    a=ar.review_status(t);check(tag+"-UNREVIEWED",{"coverage":"Complete","unreviewed_items":["Not reviewed branch"]},"unreviewed item resets even if coverage claims Complete",a,a["clean_streak"]==0)
    h.round_(t,5,findings=[{"id":"ISSUE-"+tag,"summary":"Confirmed low impact synthetic issue","evidence_refs":["synthetic-ar02://low-issue"]}])
    e=h.make_round(t,6,resolutions=[{"finding_id":"UNKNOWN","disposition":"NotAnIssue","reason":"Synthetic invalid resolution","evidence_refs":["synthetic-ar02://none"]}])
    deny(tag+"-UNRELATED-RESOLUTION",p,e,lambda:h.write(t,e))
    h.round_(t,7,resolutions=[{"finding_id":"ISSUE-"+tag,"disposition":"NotAnIssue","reason":"Synthetic documented counter-evidence","evidence_refs":["synthetic-ar02://proof"]}])
    _,_,out,bc,ev=h.snap(t)
    changed=copy.deepcopy(bc);changed["request_snapshot"]["text"]+=" New actual requirement wording."
    a=ar.review_state(out,changed)
    check(tag+"-REQUEST-CHANGED",{"reader_input":"same saved outcome, changed authoritative request words"},"old bound rounds become Stale/0",a,a["status"]=="Stale" and a["clean_streak"]==0)
    changed=copy.deepcopy(bc);changed["clarification"]["rounds"]=[{"ordinal":1,"exchanges":[{"question":"What result?","changes":["Acceptance"],"recommended_default":"Observed output","answer":"Explicit actual answer","answer_state":"Settled"}]}]
    a=ar.review_state(out,changed)
    check(tag+"-ANSWER-CHANGED",{"reader_input":"same saved outcome, additional clarification Q/default/actual-answer context"},"old bound rounds become Stale/0",a,a["status"]=="Stale" and a["clean_streak"]==0)
    future=h.make_round(t,8,recorded_at="2099-01-01T00:00:00Z")
    deny(tag+"-FUTURE",p,future,lambda:h.write(t,future))
    outside=h.build(BASE/tag,"T-UNRELATED-"+tag,minimal)
    wrong=h.make_round(t,9,delivery=outside)
    deny(tag+"-WRONG-DELIVERY",p,wrong,lambda:h.write(t,wrong))
    h.decision(t,"Stopped")
    ready=h.build(BASE/tag,"T-STOPPED-CHILD-"+tag,minimal,parent=None,complete=False)
    # Initial fixture dependency declaration is set before its close; this is a
    # test of require_review_parent, not an edit to any saved engineering result.
    if minimal:
        rp=ready/"task-record.json";r=ga.read_json(rp);r["depends_on"]=[t.name];ga.atomic_write_json(rp,r)
        bytes_path=rp
    else:
        rp=ready/"before.json";r=ga.read_json(rp);r["depends_on"]=[t.name];ga.atomic_write_json(rp,r)
        bytes_path=ready/"after.json"
    deny(tag+"-STOPPED-PARENT",bytes_path,{"parent":t.name,"state":"Stopped"},lambda:close_ready(ready,minimal,t.name))
def no_parent_consent(minimal):
    tag="MIN" if minimal else "FULL";root=BASE/("noconsent-"+tag)
    t=h.build(root,"T-NO-CONSENT-"+tag,minimal)
    ready=h.build(root,"T-CHILD-"+tag,minimal,complete=False)
    p=ready/("task-record.json" if minimal else "before.json")
    r=ga.read_json(p);r["depends_on"]=[t.name];ga.atomic_write_json(p,r)
    out=p if minimal else ready/"after.json"
    deny(tag+"-NO-CONSENT-PARENT",out,{"parent":t.name,"state":"NotOffered"},lambda:close_ready(ready,minimal,t.name))
    q=ar.review_status(t);check(tag+"-NO-CONSENT-STILL-OFFER",str(t),"child close refusal preserves original NotOffered",q,q["status"]=="NotOffered")
def crosscarrier():
    root=BASE/"cross-min-full"
    parent=h.build(root,"T-MIN-PARENT",True);h.optin(parent)
    child=h.build(root,"T-FULL-CHILD",False,parent=parent.name)
    a=ar.review_status(child);check("CROSS-MIN-FULL",{"parent":str(parent),"child":str(child)},"Full repair can belong to opted-in Minimal parent",a,a["status"]=="ManagedByParent")
    h.round_(parent,1,delivery=child)
    a=ar.review_status(parent);check("CROSS-MIN-FULL-ROUND",{"delivery":str(child)},"original Minimal review binds current Full repaired delivery",a,a["clean_streak"]==1 and a["reviewed_delivery"]["task_id"]==child.name)
def concurrency(minimal):
    tag="MIN" if minimal else "FULL"
    t=h.build(BASE/("concurrent-"+tag),"T-CONCURRENT-"+tag,minimal);h.optin(t)
    p,doc,out,bc,ev=h.snap(t)
    ud={"outcome":"Rejected","presented":"Independent synthetic current delivery","response":"Synthetic independent user rejection","decided_by":"synthetic-user","decided_at":ga.now_utc(),"evidence_ref":"synthetic-ar02://synthetic-rejection","subject_sha256":ga.user_decision_subject_sha256(bc,ev,out)}
    e=h.make_round(t,1,findings=[{"id":"KEEP-"+tag,"summary":"Independent synthetic confirmed issue","evidence_refs":["synthetic-ar02://keep"]}])
    b=threading.Barrier(2);exc=[]
    def human():
        try:
            b.wait()
            if minimal:mt.record_minimal_review(t,user_decision=ud,reason="Synthetic concurrent user decision",basis="synthetic-ar02://rejection")
            else:ga.amend_record(p,dotted_path="user_decision",new_value=ud,reason="Synthetic concurrent user decision",basis="synthetic-ar02://rejection")
        except Exception as err:exc.append(repr(err))
    def review():
        try:b.wait();h.write(t,e)
        except Exception as err:exc.append(repr(err))
    a=threading.Thread(target=human);d=threading.Thread(target=review)
    a.start();d.start();a.join();d.join()
    o=h.snap(t)[2];state=ar.review_status(t)
    actual={"thread_errors":exc,"user_decision":o["user_decision"],"review":state,"revision":h.snap(t)[1]["revision"]}
    check("CONCURRENCY-"+tag,{"operations":["actual synthetic user Rejected","new confirmed finding Round"],"schedule":"2 real threads start at barrier"},"both records retained with no lost update",actual,
        not exc and o["user_decision"]==ud and state["open_findings"]==["KEEP-"+tag])
def distribution():
    import deploy_console
    closure=deploy_console.computed_closure(h.SKILL/"scripts")
    a={"declared":sorted(deploy_console.SNAPSHOT_MODULES),"actual_import_closure":list(closure)}
    check("DIST-CLOSURE",{"entry_modules":deploy_console.CONSOLE_ENTRY_MODULES},"deployed pinned existing-console dependency closure contains new review module and is complete",a,
          tuple(sorted(deploy_console.SNAPSHOT_MODULES))==closure and "adversarial_review.py" in closure)
    # Reader APIs and generated Markdown use exactly the same bound status.
    for tag in ("FULL","MIN"):
        t=Path(__file__).resolve().parent/"supplement-run-3"/("actual-version-"+tag)/".project-governance/tasks"/("T-OLD-"+tag)
        p,d,o,bc,ev=h.snap(t)
        rendered=mt.render_minimal_review(d,task_dir=t) if tag=="MIN" else ga.render_task_review(bc,o,task_dir=t)
        (BASE/("generated-"+tag+".md")).write_text(rendered,encoding="utf-8")
        check("CONSUME-"+tag,{"task":str(t)},"generated review Markdown consumes the same status as readonly CLI",{"contains_Passed":"'status': 'Passed'" in rendered,"state":ar.review_status(t)},
              "'status': 'Passed'" in rendered)
def main():
    runs=[("transitions-FULL",lambda:transitions(False)),("transitions-MIN",lambda:transitions(True)),
        ("noconsent-FULL",lambda:no_parent_consent(False)),("noconsent-MIN",lambda:no_parent_consent(True)),
        ("crosscarrier",crosscarrier),("concurrency-FULL",lambda:concurrency(False)),("concurrency-MIN",lambda:concurrency(True)),("distribution",distribution)]
    for name,fn in runs:
        try:fn()
        except Exception as exc:
            errors.append({"suite":name,"error":repr(exc),"traceback":traceback.format_exc()});print(traceback.format_exc(),flush=True)
    h.dump(BASE/"boundary-results.json",{"ended_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"cases":cases,"errors":errors})
    print(json.dumps({"cases":len(cases),"failed":[c["id"] for c in cases if c["result"]=="Failed"],"errors":len(errors)}))
if __name__=="__main__":main()
