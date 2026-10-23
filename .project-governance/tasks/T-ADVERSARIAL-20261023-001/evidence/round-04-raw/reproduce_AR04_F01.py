from pathlib import Path
import sys, tempfile, json
sys.path.insert(0,str(Path(__file__).resolve().parent))
import review_harness as h
h.BASE=Path(tempfile.mkdtemp(prefix="lfen_ar04_f01_replay_"))
h.RAW=h.BASE/"raw"; h.RAW.mkdir()
h.FIX=h.BASE/"fixtures"; h.FIX.mkdir()
h.CASES=[]; h.COUNTER=0
t=h.fresh("Full","ended_session")
h.offer(t,"offer"); h.decision(t,"accepted")
h.entry(t,"clean-one",h.round_value(t,"clean-one"),expected={"status":"InProgress","clean_streak":1})
h.entry(t,"clean-two",h.round_value(t,"clean-two"),expected={"status":"Passed","clean_streak":2})
checks=h.read_outcome(t)["verification"]
checks[0]["summary"]="Synthetic verified receipt description corrected after review ended"
p=h.write(h.BASE/"checks.json",checks)
raw,result,ref=h.cli("amend_record.py",[h.outcome_path(t),"--path","verification","--value-json-file",p,"--reason","Correct description","--basis","ar04://synthetic-correction"],"amend")
if raw["exit_code"]: raise RuntimeError(raw)
h.query(t,"now-stale",{"status":"Stale","clean_streak":0})
h.entry(t,"unauthorized-new-round",h.round_value(t,"unauthorized-new-round"),expected_rc=2)
print(json.dumps({"replay_root":str(h.BASE),"case_count":len(h.CASES),"failed":[c["name"] for c in h.CASES if c["result"]=="Failed"]},ensure_ascii=False))
