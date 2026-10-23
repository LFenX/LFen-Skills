"""Fresh OS Temp reproduction for AR02-F001 and AR02-F002. All records are synthetic."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import importlib.util, json, subprocess, tempfile
from pathlib import Path
BASE=Path(__file__).resolve().parent
def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
h=mod("replay_h",BASE/"audit.py")
s=mod("replay_s",BASE/"supplement.py")
fixed="62aeb847cfb6fe75679a3b0ae66fdababd995bcf"
if subprocess.check_output(["git","rev-parse","HEAD"],cwd=h.ROOT,text=True).strip()!=fixed:
    raise SystemExit("This reproducer requires fixed reviewed commit "+fixed)
run=Path(tempfile.mkdtemp(prefix="ar02-replay-")).resolve()
results=[]
for minimal in (False,True):
    tag="MIN" if minimal else "FULL"
    task=h.build(run/("paths-"+tag),"T-PATH-"+tag,minimal);h.optin(task)
    entry=h.make_round(task,1)
    canonical=entry["report_ref"]
    entry["report_ref"]=str(task.resolve().parents[2]/canonical)
    before=h.digest(h.snap(task)[0])
    try:h.write(task,entry);actual={"accepted":True}
    except h.ga.GovernanceError as exc:actual={"accepted":False,"message":str(exc)}
    actual["stored_bytes_unchanged"]=h.digest(h.snap(task)[0])==before
    entry["report_ref"]=canonical
    h.write(task,entry)
    results.append({"finding":"AR02-F001","carrier":tag,"absolute_result":actual,"same_record_canonical_result":h.ar.review_status(task)})
    root=run/("version-"+tag);s.git_init(root)
    parent,old=s.build_actual(root,"T-ALPHA-"+tag,"Alpha\n",minimal)
    h.optin(parent);h.round_(parent,1)
    child,new=s.build_actual(root,"T-BETA-"+tag,"Beta\n",minimal,parent=parent.name)
    status_after_new=h.ar.review_status(parent)
    h.round_(parent,2)
    results.append({"finding":"AR02-F002","carrier":tag,"old":old,"new":new,"state_after_new_delivery":status_after_new,
                    "state_after_old_round":h.ar.review_status(parent),"child_state":h.ar.review_status(child)})
out=run/"reproduction.json"
out.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"run":str(run),"results":str(out),"observed":results},ensure_ascii=False,indent=2))

