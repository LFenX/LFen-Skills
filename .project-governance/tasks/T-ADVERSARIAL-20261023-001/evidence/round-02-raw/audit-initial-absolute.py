from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import copy, hashlib, json, os, subprocess, traceback
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path(r"D:\LFEN_project\dev_project\LFen-Skills")
SKILL = ROOT/"skills/product-engineering/run-governed-product-workflow"
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL/"scripts"))
import governance_artifacts as ga
import minimal_task as mt
import adversarial_review as ar
from self_test import new_task, minimal_fixture_record
from signals import active_task_signal, recommendations
START = "2026-10-23T10:47:42.7498397Z"
CASES = []
FAILURES = []
FIXTURES = []
def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def check(cid, inp, expected, actual, predicate):
    row = {"id":cid,"input":inp,"expected":expected,"actual":actual,"result":"Passed" if predicate else "Failed"}
    CASES.append(row)
    dump(BASE/"results.json", {"started_at":START,"cases":CASES,"fixture_errors":FAILURES})
    print(cid, row["result"], flush=True)
    return row
def snap(task):
    full = (task/"before.json").exists()
    path=task/("after.json" if full else "task-record.json")
    doc=ga.read_json(path)
    outcome=doc if full else doc["task_outcome"]
    before=ga.read_json(task/"before.json") if full else mt.minimal_approval_contract(doc)
    ledger=ga.read_jsonl(task/"run.jsonl") if full else doc["run_ledger"]
    return path,doc,outcome,before,ledger
def evidence_review(contract):
    sources=dict(ga._requirement_source_texts(contract))
    items=copy.deepcopy(contract["requirement_items"])
    for item in items:
        item["review"]={"source_sha256":hashlib.sha256(sources[item["source"]].encode()).hexdigest(),"conditions":[],
            "cases":[{"condition":None,"branch":"Unconditional","input":"Independent synthetic protocol fixture",
                      "expected":"Protocol fixture is ready","actual":"Protocol fixture is ready","result":"Passed",
                      "evidence_refs":["synthetic-ar02://fixture/assessment"]}]}
    return items
def build(root, tid, minimal=False, parent=None, complete=True):
    root.mkdir(parents=True, exist_ok=True)
    task=root/".project-governance/tasks"/tid
    if minimal:
        p=minimal_fixture_record(root,tid)
        record=ga.read_json(p)
        record["task_contract"]["decisions"]=[d for d in record["task_contract"]["decisions"] if d["kind"]=="Proceed"]
        record["task_contract"]["requirement_items"]=evidence_review(record["task_contract"])
        if parent: record["depends_on"]=[parent]
        ga.atomic_write_json(p,record)
        mt.append_minimal_event(task,event_type="run_started",summary="Independent synthetic protocol work",status="started")
        mt.append_minimal_event(task,event_type="verification",summary="Independent synthetic protocol verification",status="succeeded",evidence_refs=["synthetic-ar02://verified/"+tid])
        if complete:
            mt.close_minimal_record(task,status="Implemented",established_facts=["Synthetic fixture complete"],actual_changes=["Synthetic fixture change"],
                verification=["Passed::Independent protocol fixture check::synthetic-ar02://verified/"+tid],
                review_parent_task_id=parent)
    else:
        new_task(root,tid,1,project_id="P-MIN" if parent and (root/".project-governance/tasks"/parent/"task-record.json").exists() else "P-TEST",depends_on=[parent] if parent else [])
        record=ga.read_json(task/"before.json")
        record["authority"]["required_gates"]=[]
        record["decisions"]=[d for d in record["decisions"] if d["kind"]=="Proceed"]
        record["requirement_items"]=evidence_review(record)
        ga.atomic_write_json(task/"before.json",record)
        ga.append_run_event(task,run_id="RUN-"+tid,attempt_id="A-01",event_type="run_started",summary="Independent synthetic protocol work",status="started")
        ga.append_run_event(task,run_id="RUN-"+tid,attempt_id="A-01",event_type="verification",summary="Independent synthetic protocol verification",status="succeeded",evidence_refs=["synthetic-ar02://verified/"+tid])
        if complete:
            ga.append_run_event(task,run_id="RUN-"+tid,attempt_id="A-01",event_type="run_finished",summary="Independent synthetic finished",status="succeeded")
            ga.close_task(task,status="Implemented",established_facts=["Synthetic fixture complete"],actual_changes=["Synthetic fixture change"],
                verification=[{"result":"Passed","summary":"Independent protocol fixture check","evidence_refs":["synthetic-ar02://verified/"+tid]}],
                review_parent_task_id=parent)
    FIXTURES.append({"task":str(task),"carrier":"Minimal" if minimal else "Full","complete":complete})
    if complete:
        errors=ga.validate_task_directory(task)
        if errors: raise RuntimeError("fixture invalid: "+str(errors))
    return task
def write(task,entry): return ar.append_review(task,entry,reason="Independent AR-02 synthetic protocol test",basis="synthetic-ar02://test")
def offer(task):
    return write(task,{"event":"Offer","recorded_at":ga.now_utc(),"prompt":"Synthetic post-completion question: start adversarial review?","evidence_ref":"synthetic-ar02://offer"})
def decision(task, outcome="Accepted"):
    return write(task,{"event":"Decision","recorded_at":ga.now_utc(),"outcome":outcome,"response":"Synthetic explicit "+outcome,"decided_by":"synthetic-user","evidence_ref":"synthetic-ar02://decision"})
def optin(task): offer(task);decision(task)
def make_round(task, num, delivery=None, **overrides):
    delivery=delivery or task
    _,_,_,before,_=snap(task)
    _,_,out,db,de=snap(delivery)
    path=task/"evidence"/("independent-report-"+str(num)+".md")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("Independent synthetic protocol report "+str(num)+"\nSubject: "+delivery.name+"\nSynthetic inputs and assertions are in the external audit script.\n",encoding="utf-8")
    entry={"event":"Round","recorded_at":ga.now_utc(),"round_id":"AR02-"+str(num),"started_at":ga.now_utc(),
        "reviewer":"Independent AR02 synthetic fixture","delivery_task_id":delivery.name,
        "subject_sha256":ga.user_decision_subject_sha256(db,de,out),"requirements_sha256":ar.requirements_subject(before),
        "report_ref":str(path),"coverage":"Complete","unreviewed_items":[],"evidence_refs":["synthetic-ar02://shared-support"],
        "findings":[],"resolutions":[]}
    entry["recorded_at"]=ga.now_utc()
    entry.update(overrides)
    return entry
def round_(task,num,delivery=None,**overrides): return write(task,make_round(task,num,delivery,**overrides))
def denial(cid, task, entry, expected):
    path=task/("after.json" if (task/"before.json").exists() else "task-record.json")
    before=digest(path) if path.exists() else None
    try:
        write(task,entry); actual={"accepted":True}
    except Exception as exc:
        actual={"accepted":False,"exception":type(exc).__name__,"message":str(exc)}
    actual["unchanged"]=not path.exists() if before is None else digest(path)==before
    return check(cid,entry,expected,actual,actual.get("accepted")==False and actual["unchanged"])
def state_check(cid,task,expected):
    actual=ar.review_status(task)
    return check(cid,str(task),expected,actual,all(actual.get(k)==v for k,v in expected.items()))
def freeze():
    receipt=ga.read_json(ROOT/".project-governance/tasks/T-ADVERSARIAL-20261023-002/evidence/source-files-5376dee45f101d83.json")
    mismatches=[x["path"] for x in receipt["source_files"] if digest(ROOT/x["path"])!=x["sha256"]]
    records=[{"path":x["path"],"sha256":digest(ROOT/x["path"])} for x in receipt["source_files"]]
    clone=Path(r"C:\Users\Administrator\.lfenskills\skills\product-engineering\run-governed-product-workflow")
    entry=Path(r"C:\Users\Administrator\.codex\skills\run-governed-product-workflow")
    distributions={}
    for name,base in [("install-clone",clone),("codex-entry",entry)]:
        missing=[]; changed=[]
        for item in receipt["source_files"]:
            rel=Path(item["path"]).relative_to(SKILL.relative_to(ROOT))
            if not (base/rel).is_file(): missing.append(str(rel))
            elif digest(base/rel)!=item["sha256"]: changed.append(str(rel))
        distributions[name]={"path":str(base),"missing":missing,"changed":changed,"files_checked":len(records)}
    result={"commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),"freeze_sha256":receipt["source_sha256"],"files":records,"mismatches":mismatches,"distributions":distributions}
    dump(BASE/"freeze-check.json",result)
    check("FZ-01",{"receipt":str(ROOT/".project-governance/tasks/T-ADVERSARIAL-20261023-002/evidence/source-files-5376dee45f101d83.json")},"96 files match fixed freeze and both installed entry points",{"mismatches":mismatches,"distributions":distributions},len(records)==96 and not mismatches and all(not d["missing"] and not d["changed"] for d in distributions.values()))
def suite(minimal):
    tag="MIN" if minimal else "FULL"
    root=BASE/"workspaces"/tag
    task=build(root,"T-"+tag,minimal)
    _,doc,out,before,ledger=snap(task)
    ledger_before=copy.deepcopy(ledger)
    state_check(tag+"-01",task,{"status":"NotOffered","clean_streak":0})
    check(tag+"-02",str(task),"new result preserved independently as Pending",out.get("user_decision"),out.get("user_decision")=={"outcome":"Pending"})
    denial(tag+"-03",task,{"event":"Decision","recorded_at":ga.now_utc(),"outcome":"Accepted","response":"Synthetic begin","decided_by":"synthetic-user","evidence_ref":"synthetic-ar02://decision"},"deny decision before question")
    denial(tag+"-04",task,make_round(task,1),"deny round before offer/opt-in")
    offer(task)
    state_check(tag+"-05",task,{"status":"AwaitingUser","clean_streak":0})
    denial(tag+"-06",task,make_round(task,2),"deny round with no answer")
    decision(task,"Declined")
    state_check(tag+"-07",task,{"status":"Declined","clean_streak":0})
    denial(tag+"-08",task,make_round(task,3),"deny after decline")
    decision(task,"Deferred")
    state_check(tag+"-09",task,{"status":"Deferred","clean_streak":0})
    denial(tag+"-10",task,make_round(task,4),"deny after defer")
    decision(task)
    state_check(tag+"-11",task,{"status":"InProgress","clean_streak":0})
    round_(task,5)
    state_check(tag+"-12",task,{"status":"InProgress","clean_streak":1,"rounds":1})
    dup=make_round(task,6);dup["round_id"]="AR02-5"
    denial(tag+"-13",task,dup,"deny duplicate round id")
    alias=make_round(task,7);alias["report_ref"]=str(task/"evidence/../evidence/independent-report-5.md")
    denial(tag+"-14",task,alias,"deny report alias")
    copied=make_round(task,8)
    Path(copied["report_ref"]).write_bytes((task/"evidence/independent-report-5.md").read_bytes())
    denial(tag+"-15",task,copied,"deny copy of first report")
    round_(task,9)
    state_check(tag+"-16",task,{"status":"Passed","clean_streak":2,"rounds":2})
    denial(tag+"-17",task,make_round(task,10),"deny further round after passed without new decision")
    decision(task)
    state_check(tag+"-18",task,{"status":"InProgress","clean_streak":0})
    round_(task,11,coverage="Incomplete",unreviewed_items=["Independent untested branch"])
    state_check(tag+"-19",task,{"status":"InProgress","clean_streak":0})
    round_(task,12)
    state_check(tag+"-20",task,{"status":"InProgress","clean_streak":1})
    write(task,{"event":"Blocked","recorded_at":ga.now_utc(),"reason":"Synthetic missing isolated dependency","evidence_refs":["synthetic-ar02://blocked"]})
    state_check(tag+"-21",task,{"status":"Blocked","clean_streak":0})
    round_(task,13,findings=[{"id":tag+"-ISSUE-A","summary":"Independent confirmed protocol fixture finding","evidence_refs":["synthetic-ar02://issue-a"]}])
    state_check(tag+"-22",task,{"status":"InProgress","clean_streak":0,"open_findings":[tag+"-ISSUE-A"]})
    round_(task,14)
    state_check(tag+"-23",task,{"status":"InProgress","clean_streak":0,"open_findings":[tag+"-ISSUE-A"]})
    denial(tag+"-24",task,make_round(task,15,resolutions=[{"finding_id":tag+"-ISSUE-A","disposition":"Fixed","reason":"Synthetic claimed same-delivery fix","evidence_refs":["synthetic-ar02://fix"]}]),"deny Fixed without new verified delivery")
    round_(task,16,resolutions=[{"finding_id":tag+"-ISSUE-A","disposition":"NotAnIssue","reason":"Independent synthetic counter-evidence excludes issue","evidence_refs":["synthetic-ar02://false-positive-proof"]}])
    state_check(tag+"-25",task,{"status":"InProgress","clean_streak":1,"open_findings":[]})
    decision(task,"Stopped")
    state_check(tag+"-26",task,{"status":"Stopped","clean_streak":0})
    denial(tag+"-27",task,make_round(task,17),"deny round after user stop")
    decision(task)
    state_check(tag+"-28",task,{"status":"InProgress","clean_streak":0})
    round_(task,18)
    round_(task,19)
    state_check(tag+"-29",task,{"status":"Passed","clean_streak":2})
    _,doc2,out2,_,ledger2=snap(task)
    check(tag+"-30",str(task),"review preserves Pending user decision and closed ledger",{"user_decision":out2.get("user_decision"),"ledger_unchanged":ledger2==ledger_before},out2.get("user_decision")=={"outcome":"Pending"} and ledger2==ledger_before)
    recs=recommendations([active_task_signal(task)])
    check(tag+"-31",str(task),"Passed does not trigger another review",recs,not any("对抗性审查尚未" in x["reason"] or "主动询问是否" in x["reason"] for x in recs))
    # report loss and restoration are evidence operations, not offline governance edits.
    (task/"evidence/independent-report-19.md").rename(task/"evidence/moved-report-19.md")
    state_check(tag+"-32",task,{"status":"Stale","clean_streak":0})
    write(task,{"event":"Blocked","recorded_at":ga.now_utc(),"reason":"Actual synthetic report moved; restore evidence before continuation","evidence_refs":["synthetic-ar02://moved-report"]})
    state_check(tag+"-33",task,{"status":"Blocked","clean_streak":0})
    unfinished=build(BASE/"workspaces"/(tag+"-unfinished"),"T-INCOMPLETE-"+tag,minimal,complete=False)
    denial(tag+"-34",unfinished,{"event":"Offer","recorded_at":ga.now_utc(),"prompt":"Synthetic premature question","evidence_ref":"synthetic-ar02://offer"},"deny offer before engineering result saved")
    # New actual verified repair is registered through the public close path.
    parent=build(BASE/"workspaces"/(tag+"-repair"),"T-ORIGINAL-"+tag,minimal)
    optin(parent)
    round_(parent,"repair-A")
    repair=build(parent.resolve().parents[2],"T-REPAIR-"+tag,minimal,parent=parent.name)
    state_check(tag+"-35",repair,{"status":"ManagedByParent","clean_streak":0})
    denial(tag+"-36",repair,{"event":"Offer","recorded_at":ga.now_utc(),"prompt":"Synthetic recursive question","evidence_ref":"synthetic-ar02://offer"},"deny recursive review on child")
    # Candidate counterexample: query the original review after a new registered repair exists.
    state_check(tag+"-37",parent,{"status":"Stale","clean_streak":0})
    try:
        round_(parent,"repair-old-again")
        actual={"accepted":True,"state":ar.review_status(parent)}
    except Exception as exc:
        actual={"accepted":False,"message":str(exc),"state":ar.review_status(parent)}
    check(tag+"-38",{"task":str(parent),"new_verified_repair":str(repair),"round_delivery":parent.name},
          "A round cannot certify the superseded delivery; it must use the current registered repair",
          actual,not actual["accepted"])
def targeted():
    root=BASE/"workspaces/targeted"
    parent=build(root,"T-PARENT")
    optin(parent)
    round_(parent,1,findings=[{"id":"CASE-FIX","summary":"Synthetic review issue","evidence_refs":["synthetic-ar02://finding"]}])
    repair=build(root,"T-REPAIR",parent=parent.name)
    round_(parent,2,delivery=repair,resolutions=[{"finding_id":"CASE-FIX","disposition":"Fixed","reason":"Independent verification on the registered repair","evidence_refs":["synthetic-ar02://fixed-evidence"]}])
    state_check("EDGE-01",parent,{"status":"InProgress","clean_streak":1,"open_findings":[]})
    round_(parent,3,delivery=repair)
    state_check("EDGE-02",parent,{"status":"Passed","clean_streak":2})
    # Metadata correction does not alter delivered content.
    ga.amend_record(parent/"after.json",dotted_path="established_facts",new_value=["Clarified synthetic report prose"],reason="Actual synthetic prose correction",basis="synthetic-ar02://correction")
    state_check("EDGE-03",parent,{"status":"Passed","clean_streak":2})
    ga.amend_record(parent/"before.json",dotted_path="clarification.basis",new_value="Synthetic survey explanation corrected",reason="Actual survey explanation correction",basis="synthetic-ar02://correction")
    state_check("EDGE-04",parent,{"status":"Passed","clean_streak":2})
    # Correct engineering check list through the official amendment, thus altering version.
    checks=snap(repair)[2]["verification"]
    checks=copy.deepcopy(checks);checks[0]["summary"]="Corrected engineering verification statement"
    ga.amend_record(repair/"after.json",dotted_path="verification",new_value=checks,reason="Actual synthetic check correction",basis="synthetic-ar02://correction")
    state_check("EDGE-05",parent,{"status":"Stale","clean_streak":0})
    round_(parent,4,delivery=repair)
    state_check("EDGE-06",parent,{"status":"InProgress","clean_streak":1})
    # Round starts before completed delivery must be rejected.
    early=make_round(parent,5,delivery=repair,started_at="2026-08-15T00:00:00Z")
    denial("EDGE-07",parent,early,"deny a round started before opt-in/completion/verification")
    # Full generic amendments cannot rewrite append-only history or assignment.
    denial_value=[]
    before_hash=digest(parent/"after.json")
    errs=[]
    for path,value in [("adversarial_review",[]),("adversarial_review_parent","T-OTHER")]:
        try:ga.amend_record(parent/"after.json",dotted_path=path,new_value=value,reason="Synthetic erase attempt",basis="synthetic-ar02://invalid",allow_add=True)
        except ga.GovernanceError as exc:errs.append(str(exc))
    check("EDGE-08",["amend adversarial_review", "amend adversarial_review_parent"],"both official generic writes denied and original bytes preserved",errs,len(errs)==2 and before_hash==digest(parent/"after.json"))
    # Invalid report locations, empty report, wrong hashes, malformed CLI payloads.
    outside=BASE/"outside-report.md";outside.write_text("Actual external synthetic report",encoding="utf-8")
    denial("EDGE-09",parent,make_round(parent,6,delivery=repair,report_ref=str(outside)),"deny report outside original review task")
    empty=make_round(parent,7,delivery=repair);Path(empty["report_ref"]).write_bytes(b" ")
    denial("EDGE-10",parent,empty,"deny empty report")
    denial("EDGE-11",parent,make_round(parent,8,delivery=repair,subject_sha256="0"*64),"deny wrong delivery digest")
    denial("EDGE-12",parent,make_round(parent,9,delivery=repair,requirements_sha256="0"*64),"deny wrong original request digest")
    for n,payload in enumerate(["{", "[]", "null", '{"event":"Round"}']):
        p=BASE/f"bad-{n}.json";p.write_text(payload,encoding="utf-8")
        proc=subprocess.run([sys.executable,"-B",str(SKILL/"scripts/adversarial_review.py"),str(parent),"--entry-json-file",str(p),"--reason","Independent malformed-input check","--basis","synthetic-ar02://malformed"],capture_output=True,text=True,encoding="utf-8")
        check(f"CLI-{n}",{"payload":payload},"controlled exit 2 with no traceback",{"exit":proc.returncode,"stdout":proc.stdout,"stderr":proc.stderr},proc.returncode==2 and "Traceback" not in proc.stderr)
    # Ordinary user Acceptance is independent and must not open a new session.
    t=build(BASE/"workspaces/decision-independent","T-DECISION")
    p,doc,out,bc,ev=snap(t)
    user={"outcome":"Approved","presented":"Synthetic completed delivery","response":"Synthetic ordinary Acceptance","decided_by":"synthetic-user","decided_at":ga.now_utc(),"evidence_ref":"synthetic-ar02://ordinary-acceptance","subject_sha256":ga.user_decision_subject_sha256(bc,ev,out)}
    ga.amend_record(p,dotted_path="user_decision",new_value=user,reason="Record synthetic ordinary Acceptance",basis="synthetic-ar02://ordinary-acceptance")
    state_check("EDGE-13",t,{"status":"NotOffered","clean_streak":0})
    optin(t);round_(t,1);round_(t,2)
    p,doc,out,bc,ev=snap(t)
    check("EDGE-14",str(t),"real result-level Acceptance preserved through review history",out["user_decision"],out["user_decision"]==user)
def main():
    freeze()
    for minimal in (False,True):
        try:suite(minimal)
        except Exception as exc:
            FAILURES.append({"suite":"Minimal" if minimal else "Full","exception":repr(exc),"traceback":traceback.format_exc()})
            dump(BASE/"results.json",{"started_at":START,"cases":CASES,"fixture_errors":FAILURES})
            print(traceback.format_exc(),flush=True)
    try:targeted()
    except Exception as exc:
        FAILURES.append({"suite":"targeted","exception":repr(exc),"traceback":traceback.format_exc()})
        print(traceback.format_exc(),flush=True)
    end=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    dump(BASE/"results.json",{"started_at":START,"test_end_at":end,"cases":CASES,"fixture_errors":FAILURES,"fixtures":FIXTURES})
    print(json.dumps({"cases":len(CASES),"failed":[x["id"] for x in CASES if x["result"]=="Failed"],"fixture_errors":len(FAILURES),"test_end_at":end}),flush=True)
if __name__=="__main__":main()
