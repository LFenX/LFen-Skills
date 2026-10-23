from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import hashlib,json,subprocess
from pathlib import Path
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parent
ROOT=Path(r"D:\LFEN_project\dev_project\LFen-Skills")
S=ROOT/"skills/product-engineering/run-governed-product-workflow"
def read(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
cases=[]
for name,p in [("canonical",BASE/"canonical-run/results.json"),("supplement",BASE/"supplement-run-3/supplement-results.json"),("boundaries",BASE/"boundary-run/boundary-results.json")]:
    r=read(p)
    assert not r.get("fixture_errors") and not r.get("errors"),(name,r.get("errors"))
    for c in r["cases"]:cases.append({"suite":name,**c})
assert len(cases)==146
original=read(ROOT/".project-governance/tasks/T-ADVERSARIAL-20261023-001/before.json")
quote=original["request_snapshot"]["text"]
assert original["clarification"]["mode"]=="Skipped" and original["clarification"]["state"]=="Settled" and not original["clarification"]["rounds"]
freeze=read(ROOT/".project-governance/tasks/T-ADVERSARIAL-20261023-002/evidence/source-files-5376dee45f101d83.json")
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
changes=[x["path"] for x in freeze["source_files"] if sha(ROOT/x["path"])!=x["sha256"]]
assert not changes
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
assert head=="62aeb847cfb6fe75679a3b0ae66fdababd995bcf"
skill_paths={str(p.relative_to(ROOT)).replace("\\","/") for p in S.rglob("*") if p.is_file() and "__pycache__" not in p.parts}
extra_skill_files=sorted(skill_paths-{x["path"] for x in freeze["source_files"]})
missing_skill_files=sorted({x["path"] for x in freeze["source_files"]}-skill_paths)
assert not missing_skill_files
install={}
for label,path in [("Codex junction",Path(r"C:\Users\Administrator\.codex\skills\run-governed-product-workflow")),("Installed clone",Path(r"C:\Users\Administrator\.lfenskills\skills\product-engineering\run-governed-product-workflow"))]:
    drift=[]
    for x in freeze["source_files"]:
        rel=(ROOT/x["path"]).relative_to(S)
        if not (path/rel).is_file() or sha(path/rel)!=x["sha256"]:drift.append(str(rel))
    install[label]={"path":str(path),"checked":96,"drift":drift}
    if drift: print("INSTALL_DRIFT",label,drift)
end=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
req_data=[
("R01","将审查绑定到本任务，支持多轮查错、返修、复验","已实现",["SKILL.md:26","commands/verify.md:119","commands/verify.md:133","scripts/adversarial_review.py:277"],["FULL-12","MIN-12","CROSS-MIN-FULL-ROUND","FULL-WRONG-DELIVERY","MIN-WRONG-DELIVERY"],None),
("R02","只有当前同一交付版本连续两轮完整审查未发现问题才结束","部分实现",["commands/verify.md:138","commands/verify.md:139","scripts/adversarial_review.py:205","scripts/adversarial_review.py:326"],["FULL-12","FULL-16","MIN-12","MIN-16","FULL-21","MIN-21","VERSION-FULL-QUERY","VERSION-FULL-OLD-APPEND","VERSION-MIN-QUERY","VERSION-MIN-OLD-APPEND"],"AR02-F002：新登记且内容不同的返修交付未使旧计数失效，旧交付可继续获得 Passed。"),
("R03","优化原要求的表述，使启动、轮次、完成判据明确","已实现",["SKILL.md:26","SKILL.md:190","commands/verify.md:117"],["STATIC-SCHEMA","STATUS-OFFER"],None),
("R04","优化流程并嵌入 skill，形成可执行、可核对的调用机制","部分实现",["commands/close.md:49","commands/verify.md:144","commands/status.md:29","scripts/adversarial_review.py:290","scripts/signals.py:184","scripts/deploy_console.py:42"],["FZ-01","STATIC-SCHEMA","DIST-CLOSURE","PATH-FULL-ABS","PATH-MIN-ABS","VERSION-FULL-SIGNALS","VERSION-MIN-SIGNALS"],"AR02-F001 拒绝文档支持的有效报告路径；AR02-F002 可把过期交付记为通过。"),
("R05","对抗性审查不能直接开始；必须取得本次审查明确同意","已实现",["SKILL.md:190","commands/verify.md:123","scripts/adversarial_review.py:122","scripts/adversarial_review.py:138"],["FULL-03","FULL-04","FULL-06","FULL-08","FULL-10","FULL-11","MIN-03","MIN-04","MIN-06","MIN-08","MIN-10","MIN-11","EDGE-13","FULL-27","MIN-27"],None),
("R06","任务工程完成后主动询问是否需要审查，保留开始/拒绝/稍后分支","已实现",["SKILL.md:190","commands/close.md:49","commands/minimal.md:61","scripts/governance_artifacts.py:3975","scripts/minimal_task.py:952","scripts/signals.py:185"],["FULL-01","FULL-05","FULL-07","FULL-09","FULL-34","MIN-01","MIN-05","MIN-07","MIN-09","MIN-34","STATUS-OFFER"],None),
]
reqs=[{"id":rid,"source":"request_snapshot","quote":quote,"reading":reading,"status":status,"evidence_locations":[str(S/loc.split(":")[0])+":"+loc.split(":")[1] for loc in locs],"case_ids":ids,"gap":gap} for rid,reading,status,locs,ids,gap in req_data]
findings=[
{"id":"AR02-F001","severity":"P2","title":"合法绝对 report_ref 被原始路径与归一化路径比较拒绝","status":"Confirmed",
 "locations":[{"file":str(S/"scripts/adversarial_review.py"),"line":348},{"file":str(S/"commands/verify.md"),"line":162}],
 "preconditions":["合法 Full 或 Minimal 已以 Implemented close","原审查已有 Offer 和明确 Accepted","非空独立报告位于原任务目录内，Round 的摘要和时间均正确"],
 "steps":["使用绝对路径填写 report_ref，其他字段使用真实临时夹具当前绑定；执行 adversarial_review.py --entry-json-file。",
          "观察 exit 2 和 ERROR: report_ref must match the actual report or delivery；结果文件与封闭 RunLedger 未改写。",
          "仅将同一报告的 report_ref 换为规范项目相对路径，再执行同一 Round；exit 0、clean_streak=1。",
          "Full 与 Minimal 均复现；等价 ./ 项目相对路径也被拒绝。"],
 "expected":"验证文件边界和内容后接受文档支持的绝对路径，并保存规范化后的报告引用。",
 "actual":"facts 中的 report_ref 已规范化为项目相对路径；348-350 行把输入必填 report_ref 作为派生值逐字比较，绝对路径必然不同。",
 "impact":"用户按文档提供合法绝对路径时无法追加审查轮次；同一记录改为规范相对路径才能继续。",
 "evidence":[str(BASE/"supplement-run-3/supplement-results.json"),str(BASE/"results-initial-absolute.json"),str(BASE/"audit-initial-absolute.log"),str(BASE/"reproduce-findings.log")],
 "case_ids":["PATH-FULL-ABS","PATH-MIN-ABS","PATH-FULL-CANONICAL","PATH-MIN-CANONICAL","PATH-FULL-DOTREL","PATH-MIN-DOTREL"],
 "false_positive_exclusion":["同一个实际非空文件、同一 Round、同一交付摘要的规范相对路径对照成功，排除授权、摘要、时间、报告内容及 fixture 失效。",
                             "绝对路径属于 commands/verify.md:162 的明确承诺，不是额外路径功能建议。"]},
{"id":"AR02-F002","severity":"P1","title":"新登记并复验的返修版本不使旧交付计数失效，旧版可继续获得 Passed","status":"Confirmed",
 "locations":[{"file":str(S/"scripts/adversarial_review.py"),"line":205},{"file":str(S/"scripts/adversarial_review.py"),"line":326},{"file":str(S/"scripts/adversarial_review.py"),"line":174},{"file":str(S/"commands/verify.md"),"line":138}],
 "preconditions":["同一临时真实 Git 项目，原任务工程已完成并明确同意审查","旧版 Alpha 已有一轮完整干净记录","新返修在同项目、直接依赖原任务，使用 --review-parent-task-id 完成复验与 close"],
 "steps":["初始 src/label.txt 为 baseline；通过合法任务将其交付为 Alpha\\n，记录 mutation、成功 verification 与 close。",
          "原审查 Offer/Accepted 后记录 Alpha 的第 1 个完整干净轮次，得到 clean_streak=1。",
          "通过新返修任务将同一文件改为 Beta\\n，保留实际内容与 SHA256 证据；记录 mutation、成功 verification，close 时关联原审查。子任务正确显示 ManagedByParent。",
          "只读查询原审查；实际仍 InProgress/1，而非 Stale/0。",
          "追加独立新报告，但 delivery_task_id 仍指向旧 Alpha；CLI exit 0 并得到 Passed/2。signals 与生成的审阅 Markdown 同步显示该旧版 Passed。",
          "Full 与 Minimal 均复现。"],
 "expected":"当前交付改变时旧计数归零并显式失效；旧 delivery 不能作为当前版本的后续干净轮次，新 Beta 必须独立完成两轮。",
 "actual":"_current_bindings 仅读取历史 Round 已经引用的任务；新登记返修没有进入当前绑定集合。append_review 核对旧任务自身摘要仍一致后接受，review_state 的 subject 未变而累计为 2。",
 "impact":"当前 Beta 未经历两轮审查，却可把父审查标记 Passed 并停止；违反本需求的核心完成条件。",
 "source_versions":{"old":{"text":"Alpha\\n","sha256":"0c3ec75a4c7c5e6d69c725e4931ecc14abf1f999ea80ab74a427f67a5a7791a2"},"new":{"text":"Beta\\n","sha256":"b2e8b5f1f37c76a627cf51ae0531c613aa2ccbc7609248c568dd526b7c2fd41e"}},
 "evidence":[str(BASE/"supplement-run-3/version-proof-FULL.json"),str(BASE/"supplement-run-3/version-proof-MIN.json"),str(BASE/"supplement-run-3/stale-round-FULL.json"),str(BASE/"supplement-run-3/stale-round-MIN.json"),str(BASE/"supplement-run-3/signals-after-FULL.json"),str(BASE/"supplement-run-3/signals-after-MIN.json"),str(BASE/"boundary-run/generated-FULL.md"),str(BASE/"boundary-run/generated-MIN.md"),str(BASE/"reproduce-findings.log")],
 "case_ids":["VERSION-FULL-DIFFERENT","VERSION-FULL-QUERY","VERSION-FULL-OLD-APPEND","VERSION-FULL-SIGNALS","VERSION-MIN-DIFFERENT","VERSION-MIN-QUERY","VERSION-MIN-OLD-APPEND","VERSION-MIN-SIGNALS"],
 "false_positive_exclusion":["Alpha 与 Beta 的实际文件内容、SHA256 不同；两个交付均有成功 verification 和已保存结果。",
                             "返修通过公开 close 参数合法登记，项目、直接依赖、父审查同意均通过校验；未离线伪造或覆盖已保存治理记录。",
                             "报告内容与 round_id 均独立，时间在复验和保存之后；不是报告复制、提前开始或授权缺失。",
                             "使用正确新 delivery 时重算为第一轮的对照 EDGE-01/EDGE-06 通过；问题是旧 delivery 没有被判为当前已过期。"]}
]
conditions=[
{"condition":"工程完成并保存后才询问/审查","met":["FULL-01","MIN-01","STATUS-OFFER"],"not_met":["FULL-34","MIN-34"],"result":"Passed"},
{"condition":"仅明确同意才开始；未答/拒绝/推迟不得开始","met":["FULL-11","MIN-11","FULL-12","MIN-12"],"not_met":["FULL-04","FULL-06","FULL-08","FULL-10","MIN-04","MIN-06","MIN-08","MIN-10"],"result":"Passed"},
{"condition":"只有连续两轮完整无问题且无未解决/未检查项才通过","met":["FULL-16","MIN-16"],"not_met":["FULL-19","FULL-21","FULL-23","MIN-19","MIN-21","MIN-23","FULL-COVERAGE-INCOMPLETE","FULL-UNREVIEWED","MIN-COVERAGE-INCOMPLETE","MIN-UNREVIEWED"],"result":"Passed for fixed registered subject; current-version switch fails AR02-F002"},
{"condition":"版本或原文变化使旧计数失效；说明更正不改变绑定","met":["EDGE-05","FULL-REQUEST-CHANGED","MIN-REQUEST-CHANGED","FULL-ANSWER-CHANGED","MIN-ANSWER-CHANGED","VERSION-FULL-QUERY","VERSION-MIN-QUERY"],"not_met":["EDGE-03","EDGE-04"],"result":"Partial: same-task modification invalidates; newly registered repaired task does not"},
{"condition":"返修沿用已同意原审查，禁止无父会话或递归开始","met":["FULL-35","MIN-35","CROSS-MIN-FULL"],"not_met":["FULL-36","MIN-36","FULL-NO-CONSENT-PARENT","MIN-NO-CONSENT-PARENT","FULL-STOPPED-PARENT","MIN-STOPPED-PARENT"],"result":"Passed"},
{"condition":"独立报告可以共享支持证据；同一报告/内容不得复用","met":["FULL-16","MIN-16"],"not_met":["FULL-14","FULL-15","MIN-14","MIN-15"],"result":"Passed"},
{"condition":"合法绝对/相对报告路径应可使用；文件越界/空报告不得使用","met":["PATH-FULL-ABS","PATH-MIN-ABS","PATH-FULL-CANONICAL","PATH-MIN-CANONICAL"],"not_met":["EDGE-09","EDGE-10"],"result":"Partial: AR02-F001"},
{"condition":"停止后禁止继续；真实后续同意可恢复","met":["FULL-28","MIN-28"],"not_met":["FULL-27","MIN-27"],"result":"Passed"},
{"condition":"人工验收与审查授权互不替代；旧记录不补造协议","met":["EDGE-14","FULL-30","MIN-30","CONCURRENCY-FULL","CONCURRENCY-MIN"],"not_met":["EDGE-13","COMPAT-01","COMPAT-02"],"result":"Passed"}
]
summary={"reviewer":"/root/adversarial_round_02","started_at": "2026-10-23T10:47:42.7498397Z","ended_at":end,
"reviewed_commit":head,"skill_sha256":freeze["source_sha256"],"skill_files":96,
"delivery_task_id":"T-ADVERSARIAL-20261023-002","delivery_completed_at":"2026-10-23T10:41:43.098330Z",
"delivery_freeze_captured_at":"2026-10-23T10:39:25.692548Z",
"conclusion":"FoundIssues","coverage":"Complete","clean_round":False,"unreviewed_requirement_items":[],
"counts":{"valid_final_cases":146,"passed":sum(c["result"]=="Passed" for c in cases),"failed":sum(c["result"]=="Failed" for c in cases),"confirmed_findings":2,"P1":1,"P2":1},
"authority":{"request_snapshot":original["request_snapshot"],"clarification":original["clarification"]},
"requirements":reqs,"condition_pairs":conditions,"findings":findings,
"limitations":["独立反例在 Windows / Python 3.13.0 执行；未在 Python 3.11、3.12、macOS、Linux 重跑本轮反例。未把其他人的工程测试结果作为本轮结论。",
"本轮不操作生产、不安装/更新真实分发、不启动 Web 服务；安装分发用文件逐项摘要与入口解析检查。",
"机器结构和摘要校验不证明自然语言审查质量；本轮发现项均有自主构造、实际执行的反例。",
"没有新增 live console UI 的原始要求，因此没有将新 UI 呈现作为缺陷或未实现项。"],
"scope_controls":{"previous_round_reports_read":False,"self_test_run":False,"subagents_spawned":False,"shared_files_edited":False,
"actual_original_offer":"2026-10-23T09:34:53.863146Z","actual_original_accepted":"2026-10-23T09:58:06.866514Z",
"original_user_answer":"开始审查","all_test_writes":"OS Temp only","installation_checks":install},
"retry_notes":[
{"files":["audit-initial-absolute.py","audit-initial-absolute.log","results-initial-absolute.json"],"observed":"初始合法绝对 report_ref 使 Full/Minimal/返修组在首个 Round 失败；该结果归入 AR02-F001，未计作干净轮次。改用规范项目相对路径完成后续覆盖。"},
{"files":["supplement-initial.py","supplement-initial.log","supplement-run/supplement-results.json"],"observed":"真实 Git 夹具沿用了仅绝对根路径声明，scope reconciliation 拒绝 src/label.txt；在新的临时项目预先声明 src/label.txt 后重试。该夹具错误不作为产品发现。"},
{"files":["supplement-run-2.py","supplement-run-2.log","supplement-run-2/supplement-results.json"],"observed":"测试进程读取 signals 中文输出时 UTF-8 与系统管道编码不一致；在新临时项目以 Python -X utf8 运行 CLI 后完成。该读取错误不作为产品发现。"},
{"files":["reproduce_findings.py","reproduce-findings.log"],"observed":"独立重放第一次遇到 Windows Temp 短路径与 resolve 后长路径不一致；把新建临时根 resolve 后完成两种载体重放。有效重放目录 ar02-replay-p28x3bu3。"}],
"reproduction":{"command":'python -X utf8 -B "'+str(BASE/"reproduce_findings.py")+'"',
"current_complete_run":r"C:\Users\Administrator\AppData\Local\Temp\ar02-replay-p28x3bu3\reproduction.json",
"note":"脚本每次新建独立临时消费项目，检查当前受审固定提交；调用保存的同目录审查辅助脚本。"},
"files":{"full_cases":str(BASE/"cases.json"),"report":str(BASE/"report.md"),"json_report":str(BASE/"report.json"),"requirements":str(BASE/"requirements-audit.json")}}
dump(BASE/"cases.json",cases);dump(BASE/"requirements-audit.json",{"original_quote":quote,"clarification":original["clarification"],"requirements":reqs,"condition_pairs":conditions})
dump(BASE/"report.json",summary)
lines=[
"本次任务使用的 skills：run-governed-product-workflow（verify）。",
"",
"# AR-02 独立只读对抗性审查",
"",
"结论：发现 2 项已确认问题（P1 × 1、P2 × 1）。本轮不计为干净轮次；需要返修并从新交付版本重新累计。",
"",
f"- 执行者：{summary['reviewer']}。",
f"- 开始 UTC：{summary['started_at']}；结束 UTC：{end}。",
f"- 固定提交：{head}。",
f"- 固定 skill：{S}；96 文件冻结摘要：{freeze['source_sha256']}。",
"- 实际已验证交付：T-ADVERSARIAL-20261023-002；completed_at=2026-10-23T10:41:43.098330Z。",
"- 原任务的真实问题发生于 2026-10-23T09:34:53.863146Z；明确回答“开始审查”发生于 2026-10-23T09:58:06.866514Z。本轮使用该已授权会话。",
"- 146 个最终有效用例：132 个满足断言，14 个断言失败均归入以下两项问题。初始错误和重试单独留存，不冒充通过。",
"",
"## 原始权威输入与逐条结论",
"",
"以下完整原话从 T-ADVERSARIAL-20261023-001/before.json 的 request_snapshot 独立读取；没有以派生任务卡或上一轮报告替代。",
"",
"> "+quote,
"",
"澄清：mode=Skipped、state=Settled、rounds=[]，没有需要另行展开的真实回答。每条结构化记录均保留同一完整原句、来源及限定词，见 requirements-audit.json。",
"",
"| ID | 独立摘取的要求 | 状态 | 差异与证据 |",
"|---|---|---|---|"]
for r in reqs:
    lines.append("| "+r["id"]+" | "+r["reading"]+" | "+r["status"]+" | "+(r["gap"] or "；".join(r["case_ids"]))+" |")
lines+=["","未实现项：无独立的完全未实现项。部分实现项：R02、R04，分别由 AR02-F002、AR02-F001/002 证明；不得作为已全部实现交付。","","## 已确认发现",""]
for f in findings:
    lines+=["### "+f["id"]+" ["+f["severity"]+"] "+f["title"],"",
    "- 位置："+"；".join(x["file"]+":"+str(x["line"]) for x in f["locations"])+"。",
    "- 预期："+f["expected"],
    "- 实际："+f["actual"],
    "- 影响："+f["impact"],
    "",
    "复现步骤：",""]
    lines += [str(i+1)+". "+x for i,x in enumerate(f["steps"])]
    lines += ["","误报排除：",""]+["- "+x for x in f["false_positive_exclusion"]]
    lines += ["","证据：",""]+["- "+x for x in f["evidence"]]+[""]
lines+=["## 条件与例外的正反对照",""]
for c in conditions:
    lines+=["- 条件："+c["condition"]+"。成立输入："+", ".join(c["met"])+"；不成立输入："+", ".join(c["not_met"])+"；结论："+c["result"]+"。"]
lines+=["","## 覆盖范围、兼容与边界","",
"已完整检查入口 SKILL、verify/close/status/minimal 命令说明、adversarial_review 主实现、Full/Minimal 结果生成与归属、修订守卫/锁、Schema、signals、生成审阅 Markdown、get_approval_subject、既有部署闭包及安装分发。其余不相关规范正文没有递归读取。",
"",
"- 需求原文及澄清绑定、工程完成/同意/停止时间、轮次/问题 ID、独立报告及内容、未检查项、阻塞、问题处置、返修关联与复验均有正反对照。",
"- 既有结果、user_decision 和封闭 RunLedger 保持兼容：Pending 不被替换成批准，普通 Acceptance 不启动审查；实际并发线程保存拒绝决定与新发现，Full/Minimal 均无丢失。",
"- 缺少协议的旧结果只读显示 LegacyUntracked；旧轮次显示 LegacyNotRevalidated，不被计为新 v2 两轮通过。旧记录用纯读取模型测试，不离线改写权威文件。",
"- 已对源、安装克隆及 Codex Junction 入口的全部 96 文件逐项 SHA256 核对；审查末尾无受审文件漂移，当前提交仍固定。",
"- 只有一个独立执行者完成本轮；146 个用例没有拆成多个审查轮次。没有读取先前任何轮次报告，没有执行 self_test，没有启动子 Agent。",
"- 未向共享仓库、真实安装目录或真实用户决定写入。本轮测试、夹具、Git 项目及报告全部位于 OS Temp。",
"",
"未检查需求项：[]。执行环境与范围限制：",""]+["- "+x for x in summary["limitations"]]
lines+=["","## 重试与原始文件",""]
for n in summary["retry_notes"]:lines+=["- "+n["observed"]+" 文件："+", ".join(n["files"])+"。"]
lines+=["","独立重放命令：","","\u0060\u0060\u0060powershell",summary["reproduction"]["command"],"\u0060\u0060\u0060","",
"已成功的最新重放结果："+summary["reproduction"]["current_complete_run"],"",
"原始脚本：audit.py、audit-initial-absolute.py、supplement.py、supplement-initial.py、supplement-run-2.py、boundaries.py、reproduce_findings.py。原始结果：canonical-run/results.json、supplement-run-3/supplement-results.json、boundary-run/boundary-results.json。",
"",
"Full per-case input / expected / actual / result: cases.json (146 cases).", ""]
(BASE/"report.md").write_text("\n".join(lines),encoding="utf-8")
receipt={"started_at":summary["started_at"],"ended_at":end,"fixed_commit":head,"source_sha256":freeze["source_sha256"],"source_files_checked":96,"source_drift":changes,"extra_skill_files":extra_skill_files,"install":install,
"report":str(BASE/"report.md"),"report_sha256":sha(BASE/"report.md"),"json_report":str(BASE/"report.json"),"case_file":str(BASE/"cases.json"),"case_file_sha256":sha(BASE/"cases.json"),
"reproduction":summary["reproduction"],"summary":summary["counts"],"test_files":[str(BASE/p) for p in ["audit.py","supplement.py","boundaries.py","reproduce_findings.py"]]}
dump(BASE/"receipt.json",receipt)
print(json.dumps(receipt,ensure_ascii=False,indent=2))
