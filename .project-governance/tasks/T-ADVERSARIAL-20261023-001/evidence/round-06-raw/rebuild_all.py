"""Rebuild AR-06 synthetic fixtures into a new OS Temp directory; never writes repository or installed skill."""
from pathlib import Path
from datetime import datetime,timezone
import sys,os,tempfile,shutil,subprocess,json,hashlib
source=Path(__file__).resolve().parent
out=Path(tempfile.mkdtemp(prefix='ar06-rebuild-')).resolve()
repo=Path(r'D:/LFEN_project/dev_project/LFen-Skills')
for name in ['review_cases.py','execute_suite.py','execute_boundaries.py','execute_final_checks.py','allowed-original-input.json']:
    shutil.copy2(source/name,out/name)
manifest=json.loads((repo/'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/source-files-f0f3ce7fedddffcc.json').read_text(encoding='utf-8'))
installed=Path(r'C:/Users/Administrator/.codex/skills/run-governed-product-workflow')
diff=[]
for item in manifest['source_files']:
    rel=Path(item['path']).relative_to('skills/product-engineering/run-governed-product-workflow');p=installed/rel
    h=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else 'missing'
    if h!=item['sha256']:diff.append({'path':rel.as_posix(),'installed':h,'repo':item['sha256']})
(out/'distribution-hash-differences.json').write_text(json.dumps({'installed':str(installed),'file_count':len(manifest['source_files']),'differences':diff},indent=2),encoding='utf-8')
commands=[]
for name in ['execute_suite.py','execute_boundaries.py','execute_final_checks.py']:
    command=[sys.executable,'-X','utf8',str(out/name)]
    p=subprocess.run(command,cwd=out,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    log=name.replace('.py','-rebuild-output.txt');(out/log).write_text(p.stdout+p.stderr,encoding='utf-8')
    commands.append({'command':command,'returncode':p.returncode,'output':log})
    if p.returncode:break
(out/'rebuild-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'output':str(out),'commands':commands},ensure_ascii=False,indent=2))
