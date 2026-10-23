import hashlib,json
from pathlib import Path
p=Path(r'D:/LFEN_project/dev_project/LFen-Skills/.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/source-files-f0f3ce7fedddffcc.json')
d=json.loads(p.read_text()); rows=d['source_files'];expected=d['source_sha256']
for options in [{},{'sort_keys':True},{'sort_keys':True,'separators':(',',':')},{'separators':(',',':')}]:
    value=hashlib.sha256(json.dumps(rows,ensure_ascii=False,**options).encode()).hexdigest();print(options,value,value==expected)
for separator in ['\n','']:
    value=hashlib.sha256(separator.join(x['path']+':'+x['sha256'] for x in rows).encode()).hexdigest();print('colon',repr(separator),value,value==expected)
