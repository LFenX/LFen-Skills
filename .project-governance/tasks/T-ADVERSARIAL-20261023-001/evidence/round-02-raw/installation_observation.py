import difflib,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
base=Path(__file__).resolve().parent
source=Path(r"D:\LFEN_project\dev_project\LFen-Skills\skills\product-engineering\run-governed-product-workflow\scripts\governance_artifacts.py")
installed=Path(r"C:\Users\Administrator\.lfenskills\skills\product-engineering\run-governed-product-workflow\scripts\governance_artifacts.py")
a,b=source.read_bytes(),installed.read_bytes()
d=list(difflib.unified_diff(a.decode("utf-8").splitlines(),b.decode("utf-8").splitlines(),fromfile=str(source),tofile=str(installed),n=3))
observation={"observed_at":datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),"source":{"path":str(source),"sha256":hashlib.sha256(a).hexdigest(),"bytes":len(a)},"installed":{"path":str(installed),"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)},"same_text_ignoring_line_endings":a.replace(b"\r\n",b"\n")==b.replace(b"\r\n",b"\n"),"unified_diff":d}
(base/"installation-observation.json").write_text(json.dumps(observation,ensure_ascii=False,indent=2),encoding="utf-8")
(base/"installation-observation.diff").write_text("\n".join(d)+"\n",encoding="utf-8")
print(json.dumps(observation,ensure_ascii=False,indent=2))
