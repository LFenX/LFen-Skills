import json
from pathlib import Path
p=Path(r'D:/LFEN_project/dev_project/LFen-Skills/skills/product-engineering/run-governed-product-workflow/assets/runtime/schemas/minimal-task-record.schema.json')
d=json.loads(p.read_text());print(json.dumps(d['properties']['task_outcome'],ensure_ascii=False)[:700])
