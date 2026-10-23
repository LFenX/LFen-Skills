import hashlib,json,sys,subprocess,platform
from pathlib import Path
from datetime import datetime,timezone
root=Path(r'D:/LFEN_project/dev_project/LFen-Skills')
out=Path(r'C:/Users/ADMINI~1/AppData/Local/Temp/ar06-independent-20261023T135251Z')
manifest=json.loads((root/'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/source-files-f0f3ce7fedddffcc.json').read_text(encoding='utf-8'))
actual=[{'path':f['path'],'expected':f['sha256'],'actual':hashlib.sha256((root/f['path']).read_bytes()).hexdigest()} for f in manifest['source_files']]
data={'started_at':'2026-10-23T13:51:58.3819499Z','checked_at':datetime.now(timezone.utc).isoformat(),'python':sys.version,'platform':platform.platform(),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'source_sha256':manifest['source_sha256'],'files':actual,'mismatches':[f for f in actual if f['expected']!=f['actual']]}
(out/'freeze-start.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
b=json.loads((root/'.project-governance/tasks/T-ADVERSARIAL-20261023-001/before.json').read_text(encoding='utf-8'))
a=json.loads((root/'.project-governance/tasks/T-ADVERSARIAL-20261023-001/after.json').read_text(encoding='utf-8'))
inputs={'request_snapshot':b['request_snapshot'],'clarification':b['clarification'],'offer_decision':[v for v in a['adversarial_review'] if v['event'] in ['Offer','Decision']]}
(out/'allowed-original-input.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'tool-setup-failure.txt').write_text('First setup command used Bash brace-list syntax in PowerShell rg arguments. PowerShell parser rejected before any command ran (Missing argument in parameter list). Corrected command used separate literal file paths. Harness/tool invocation error, not product finding.\n',encoding='utf-8')
print(json.dumps({'temp':str(out),'file_count':len(actual),'mismatches':data['mismatches'],'head':data['head']},ensure_ascii=False,indent=2))
