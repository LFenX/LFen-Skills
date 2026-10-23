from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import copy, hashlib, importlib.util, json, subprocess, traceback
from pathlib import Path
from datetime import datetime, timezone
BASE=Path(__file__).resolve().parent/"supplement-run-3"
BASE.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location("audit_harness",Path(__file__).resolve().parent/"audit.py")
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
ga,mt,ar=h.ga,h.mt,h.ar
cases=[];errors=[]
def dump(name,data):h.dump(BASE/name,data)
def now():return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def check(cid,inp,expected,actual,success):
    cases.append({"id":cid,"input":inp,"expected":expected,"actual":actual,"result":"Passed" if success else "Failed"})
    dump("supplement-results.json",{"cases":cases,"errors":errors})
    print(cid,cases[-1]["result"],flush=True)
def cli(task,entry=None,signal=False):
    cmd=[sys.executable,"-X","utf8","-B",str(h.SKILL/"scripts"/("signals.py" if signal else "adversarial_review.py"))]
    if signal:cmd+=["--project-root",str(task.resolve().parents[2])]
    else:cmd+=[str(task)]
    if entry is not None:
        inp=BASE/("input-"+task.name+"-"+str(len(cases))+".json");h.dump(inp,entry)
        cmd+=["--entry-json-file",str(inp),"--reason","Independent synthetic boundary check","--basis","synthetic-ar02://supplement"]
    proc=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8")
    value={"command":cmd,"exit":proc.returncode,"stdout":proc.stdout,"stderr":proc.stderr}
    try:value["json"]=json.loads(proc.stdout)
    except ValueError:pass
    return value
def absolute_paths():
    for minimal in (False,True):
        tag="MIN" if minimal else "FULL"
        t=h.build(BASE/("absolute-"+tag),"T-ABS-"+tag,minimal)
        h.optin(t)
        e=h.make_round(t,1)
        p,doc,out,bc,ev=h.snap(t)
        ledger_before=copy.deepcopy(ev)
        original=h.digest(p)
        absolute=copy.deepcopy(e);absolute["report_ref"]=str(t.resolve().parents[2]/e["report_ref"])
        actual=cli(t,absolute)
        actual["outcome_bytes_unchanged"]=h.digest(p)==original
        actual["ledger_unchanged"]=h.snap(t)[4]==ledger_before
        check("PATH-"+tag+"-ABS",absolute,"Absolute in-task non-empty report is supported; append Round and return exit 0",
            actual,actual["exit"]==0)
        # Retry the identical record with only the path expressed relative to the project.
        canonical=cli(t,e)
        check("PATH-"+tag+"-CANONICAL",e,"Identical report via canonical project-relative path succeeds",canonical,
              canonical["exit"]==0 and canonical.get("json",{}).get("clean_streak")==1)
        e2=h.make_round(t,2)
        e2["report_ref"]="./"+e2["report_ref"]
        act2=cli(t,e2)
        check("PATH-"+tag+"-DOTREL",e2,"Equivalent project-relative path normalizes and succeeds",act2,act2["exit"]==0)
def git_init(root):
    root.mkdir(parents=True,exist_ok=True)
    (root/"src").mkdir(exist_ok=True)
    (root/"src/label.txt").write_text("baseline\n",encoding="utf-8")
    (root/".gitignore").write_text(".project-governance/\nLG_project_docs/\nsurveyed.md\n",encoding="utf-8")
    for cmd in [["git","init","-q"],["git","-c","user.name=AR02 Synthetic","-c","user.email=synthetic-ar02@example.invalid","add","."],
                ["git","-c","user.name=AR02 Synthetic","-c","user.email=synthetic-ar02@example.invalid","commit","-q","-m","Independent synthetic baseline"]]:
        subprocess.run(cmd,cwd=root,capture_output=True,check=True)
def build_actual(root,tid,content,minimal,parent=None):
    t=root/".project-governance/tasks"/tid
    if minimal:
        p=h.minimal_fixture_record(root,tid);rec=ga.read_json(p)
        rec["task_contract"]["decisions"]=[d for d in rec["task_contract"]["decisions"] if d["kind"]=="Proceed"]
        rec["task_contract"]["requirement_items"]=h.evidence_review(rec["task_contract"])
        if parent:rec["depends_on"]=[parent]
        ga.atomic_write_json(p,rec)
        mt.append_minimal_event(t,event_type="run_started",summary="Independent version-changing work",status="started")
    else:
        h.new_task(root,tid,1,depends_on=[parent] if parent else [])
        p=t/"before.json";rec=ga.read_json(p)
        rec["decisions"]=[d for d in rec["decisions"] if d["kind"]=="Proceed"]
        rec["authority"]["required_gates"]=[]
        rec["source_snapshot"]=ga.capture_source_snapshot(root)
        rec["scope"]["allowed_paths"]=["src/label.txt"]
        rec["requirement_items"]=h.evidence_review(rec)
        ga.atomic_write_json(p,rec)
        ga.append_run_event(t,run_id="RUN-"+tid,attempt_id="A-01",event_type="run_started",summary="Independent version-changing work",status="started")
    target=root/"src/label.txt";target.write_text(content,encoding="utf-8")
    sha=h.digest(target)
    receipt=t/"evidence/delivery.json"
    h.dump(receipt,{"observed_at":now(),"source":str(target),"text":content,"sha256":sha})
    ref=str(receipt)
    if minimal:
        mt.append_minimal_event(t,event_type="mutation",summary="Set actual local source label",status="succeeded",evidence_refs=[ref])
        mt.append_minimal_event(t,event_type="verification",summary="Read and hash actual delivered local label",status="succeeded",evidence_refs=[ref])
        mt.close_minimal_record(t,status="Implemented",established_facts=["Label read and hashed"],actual_changes=["Set src/label.txt to "+content.strip()],verification=["Passed::Actual source label hash checked::"+ref],review_parent_task_id=parent)
    else:
        for kind,summary in [("mutation","Set actual local source label"),("verification","Read and hash actual delivered local label"),("run_finished","Version-changing work finished")]:
            ga.append_run_event(t,run_id="RUN-"+tid,attempt_id="A-01",event_type=kind,summary=summary,status="succeeded",evidence_refs=[ref])
        ga.close_task(t,status="Implemented",established_facts=["Label read and hashed"],actual_changes=["Set src/label.txt to "+content.strip()],verification=[{"result":"Passed","summary":"Actual source label hash checked","evidence_refs":[ref]}],review_parent_task_id=parent)
    err=ga.validate_task_directory(t)
    if err:raise RuntimeError("actual-version fixture invalid: "+str(err))
    return t,{"text":content,"sha256":sha,"receipt":str(receipt),"verified_task":str(t)}
def actual_versions():
    for minimal in (False,True):
        tag="MIN" if minimal else "FULL"
        root=BASE/("actual-version-"+tag);git_init(root)
        parent,old=build_actual(root,"T-OLD-"+tag,"Alpha\n",minimal)
        h.optin(parent);h.round_(parent,1)
        first=cli(parent)
        repair,new=build_actual(root,"T-NEW-"+tag,"Beta\n",minimal,parent=parent.name)
        after=cli(parent)
        sig=cli(parent,signal=True)
        dump("version-proof-"+tag+".json",{"old":old,"new":new,"original_status_before_repair":first,"original_status_after_repair":after,"signals":sig})
        check("VERSION-"+tag+"-DIFFERENT",{"old":old,"new":new},"Actual governed source delivery changes Alpha to Beta and new child is ManagedByParent",
            {"new_review":ar.review_status(repair),"different_source_sha256":old["sha256"]!=new["sha256"],"old_subject":h.snap(parent)[2]["scope_reconciliation"] if not minimal else first.get("json",{}).get("subject_sha256")},
            old["sha256"]!=new["sha256"] and ar.review_status(repair)["status"]=="ManagedByParent")
        check("VERSION-"+tag+"-QUERY",{"old":old,"new":new},"Old clean streak invalidates when new registered verified delivery replaces it",after,
            after["exit"]==0 and after.get("json",{}).get("clean_streak")==0 and after.get("json",{}).get("status")=="Stale")
        before_new_round_hash=h.digest(h.snap(parent)[0])
        e=h.make_round(parent,2)
        stale_append=cli(parent,e)
        dump("stale-round-"+tag+".json",{"input":e,"result":stale_append,"new_delivery":new,"old_delivery":old,"query_before":after,"signals_before":sig})
        check("VERSION-"+tag+"-OLD-APPEND",{"new_delivery":new,"round":e},"Old delivery cannot produce two-clean-round Passed on current Beta",stale_append,
            stale_append["exit"]!=0)
        after_sig=cli(parent,signal=True)
        pprogress=[x for x in after_sig.get("json",{}).get("task_progress",[]) if x["task_id"]==parent.name]
        check("VERSION-"+tag+"-SIGNALS",{"new_delivery":new,"task":parent.name},"signals never publishes Passed for superseded Alpha after current Beta exists",pprogress,
              bool(pprogress) and pprogress[0]["adversarial_review"]["status"]!="Passed")
        dump("signals-after-"+tag+".json",after_sig)
def static_boundaries():
    s=ga.read_json(h.SKILL/"assets/runtime/schemas/task-after.schema.json")
    m=ga.read_json(h.SKILL/"assets/runtime/schemas/minimal-task-record.schema.json")
    same=s["properties"]["adversarial_review"]==ar.review_schema()
    nested=m["properties"]["task_outcome"]["oneOf"][1]["properties"]["adversarial_review"]
    check("STATIC-SCHEMA",{"Full":"task-after.schema.json","Minimal":"minimal-task-record.schema.json"},"Both carrier schemas exactly match public review event contract",
          {"Full_match":same,"Minimal_match":nested==ar.review_schema()},same and nested==ar.review_schema())
def compatibility():
    t=h.build(BASE/"compatibility","T-COMPAT")
    p,doc,out,bc,ev=h.snap(t)
    old=copy.deepcopy(out);old.pop("adversarial_review")
    a=ar.review_state(old,bc)
    check("COMPAT-01",{"model":"Saved historical outcome without adversarial_review; file unmodified"},"Historical read remains LegacyUntracked",a,a["status"]=="LegacyUntracked")
    h.optin(t);h.round_(t,1);h.round_(t,2)
    out=h.snap(t)[2]
    legacy=copy.deepcopy(out)
    for entry in legacy["adversarial_review"]:
        if entry["event"]=="Round":
            for key in ["review_contract_version","report_sha256","delivery_completed_at","delivery_verified_at"]:entry.pop(key,None)
            entry["requirements_sha256"]=ar._legacy_requirements_subject(bc)
    a=ar.review_state(legacy,bc)
    check("COMPAT-02",{"model":"Two genuine old-contract complete rounds replayed as a pure reader input"},"Old convergence is LegacyNotRevalidated, never counted as new v2 Passed",a,
          a["status"]=="LegacyNotRevalidated" and a["clean_streak"]==0)
    # A normal result without a recorded question still recommends an actual offer.
    nt=h.build(BASE/"recommendations","T-NOTOFFERED")
    a=h.recommendations([h.active_task_signal(nt)])
    check("STATUS-OFFER",{"task":str(nt)},"Fresh completed engineering actively recommends asking before adversarial review",a,
          any("主动询问" in x["reason"] and "明确同意前不得开始" in x["reason"] for x in a))
def main():
    for name,fn in [("absolute_paths",absolute_paths),("actual_versions",actual_versions),("compatibility",compatibility),("static",static_boundaries)]:
        try:fn()
        except Exception as exc:
            errors.append({"suite":name,"error":repr(exc),"traceback":traceback.format_exc()})
            print(traceback.format_exc(),flush=True)
    dump("supplement-results.json",{"ended_at":now(),"cases":cases,"errors":errors})
    print(json.dumps({"cases":len(cases),"failed":[x["id"] for x in cases if x["result"]=="Failed"],"errors":len(errors)}),flush=True)
if __name__=="__main__":main()
