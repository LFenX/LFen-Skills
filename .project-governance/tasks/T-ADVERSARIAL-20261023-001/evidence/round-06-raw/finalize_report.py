from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,sys,platform
A=Path(__file__).resolve().parent
R=Path(r'D:/LFEN_project/dev_project/LFen-Skills')
S=R/'skills/product-engineering/run-governed-product-workflow'
def wr(name,value):
    (A/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
frozen=json.loads((R/'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/source-files-f0f3ce7fedddffcc.json').read_text(encoding='utf-8'))
files=[{'path':f['path'],'expected':f['sha256'],'actual':sha(R/f['path'])} for f in frozen['source_files']]
end={'checked_at':now,'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'source_sha256':frozen['source_sha256'],'file_count':len(files),'files':files,'mismatches':[f for f in files if f['actual']!=f['expected']]}
wr('freeze-end.json',end)
original=json.loads((A/'allowed-original-input.json').read_text(encoding='utf-8'));quote=original['request_snapshot']['text']
cases=json.loads((A/'cases.json').read_text(encoding='utf-8'))
failed=[c['id'] for c in cases if c['result']=='Failed']
# The schema/decision-line evidence is extracted only from frozen source, not earlier review results.
excerpts=[]
for path,start,stop in [('scripts/adversarial_review.py',22,58),('scripts/adversarial_review.py',120,143),('scripts/adversarial_review.py',357,432),('SKILL.md',19,32),('commands/verify.md',110,139),('commands/close.md',47,51)]:
    ls=(S/path).read_text(encoding='utf-8').splitlines()
    excerpts.append({'path':'skills/product-engineering/run-governed-product-workflow/'+path,'start':start,'end':stop,'sha256':sha(S/path),'lines':[{'line':i,'text':ls[i-1]} for i in range(start,min(stop,len(ls))+1)]})
wr('source-excerpts.json',excerpts)
# Allowed 005 engineering evidence: expose only the installed-combination fact, never its review aggregates.
v=json.loads((R/'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/validation-summary.json').read_text(encoding='utf-8'))
wr('allowed-005-installed-engineering-evidence.json',{'source':'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/validation-summary.json','installed_self_test':v['installed_self_test'],'use':'Only this allowed engineering field is retained. No imported installed module or new installed execution in AR06.'})
incident={'id':'AR06-INC01','observed_at':'2026-10-23T14:08:50.1898947Z','kind':'incidental_exposure','source':'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/validation-summary.json','facts':'While reading the allowed current-005 engineering verification summary to check installed-combination evidence, the terminal also displayed existing review aggregate fields and one prior finding identifier. No prior finding description or round report was read. The identifier is not repeated in this archive.','ordering':'All 158 case records and independent finding reproductions were already complete before this exposure; F46/M46 reproduced at 13:58:59Z onward, CLI decision/round/query evidence at 14:03:05Z–14:03:06Z.','handling':'Stopped further reading of those aggregates; did not use them for test design, expected results, issue classification, or conclusions. Disclosed immediately to parent. Parent instructed truthful reporting and completion without rerunning cases.','impact':'The read-isolation restriction was not completely met. The issue was independently reproduced before exposure; this round contains a finding and does not count as a clean round.'}
wr('independence-incident.json',incident)
findings=[{'id':'AR06-F01','severity':'P2','status':'Confirmed','title':'空白授权关键字段被接受，并可生成审查 Passed','requirement_refs':['R04','R06','R07'],'locations':[{'file':'skills/product-engineering/run-governed-product-workflow/scripts/adversarial_review.py','line':24,'detail':'共享 text 仅 minLength=1，空格/制表符通过，Decision 三个关键字段复用此定义。'},{'file':'skills/product-engineering/run-governed-product-workflow/scripts/adversarial_review.py','line':36,'detail':'Decision.response、decided_by、evidence_ref 未要求包含非空白字符。'},{'file':'skills/product-engineering/run-governed-product-workflow/scripts/adversarial_review.py','line':139,'detail':'状态重放仅凭 outcome=Accepted 置 accepted=True，不拒绝空白回答、身份、来源。'}],'condition':'已保存的 Implemented 工程结果有真实形状的 Offer；Decision.outcome=Accepted，但 response=" \\t "、decided_by=" "、evidence_ref="\\t"。仅合成 Temp 夹具。','expected':'拒绝没有实际回答、实际决定人和可核对来源的空白 Decision；保持 AwaitingUser，禁止 Round 计数。','actual':'Full 与 Minimal 的公开 append_review 均接受；公开 CLI 也 exit 0 并显示 InProgress；随后两份独立非空报告使状态达到 Passed、clean_streak=2。','impact':'机器门禁把实际缺失的授权凭据当作有效同意，能生成具有 Passed 状态的无有效授权审查会话。当前真实任务的用户同意记录完整；本发现不否定其实际授权。','root_cause':'JSON Schema minLength 检查字符长度，不能排除全部由空白字符组成的值；运行时未补充非空白校验。','minimum_reproduction':['在 Temp 中用 review_cases.create 建立 Full 或 Minimal 已完工任务，并写入 Offer。','使用公开 adversarial_review.py --entry-json-file 写入 raw/CLI-BLANK-DECISION-entry.json 形状的空白 Decision。','公开 CLI 返回 exit0/InProgress（raw/CLI-BLANK-DECISION-command.json）。','追加两份独立报告并只读查询；得到 Passed、clean_streak=2（raw/CLI-BLANK-STATE-command.json）。'],'case_ids':['F46','M46','CLI01','CLI02'],'evidence_refs':['raw/F46.json','raw/M46.json','raw/CLI-BLANK-DECISION-entry.json','raw/CLI-BLANK-DECISION-command.json','raw/CLI-BLANK-ROUND-1-command.json','raw/CLI-BLANK-ROUND-2-command.json','raw/CLI-BLANK-STATE-command.json','source-excerpts.json'],'recommended_direction':'在共享 schema 或公共追加/重放入口拒绝 Offer/Decision 关键字段的全空白值，保留合法回答原文；同步 Full/Minimal schema 并补 API/CLI 反例。此报告不修改实现。'}]
wr('findings.json',findings)
rows=[
('R01','针对当前任务增加多轮对抗性审查','已实现',['F12','F15','F36','F41','M12','M15','M36','M41'],'公开入口持续追加独立轮次；支持同范围继续和真实新决定重新开始。',['source-excerpts.json','raw/F36.json','raw/M36.json']),
('R02','直到连续两次完整审查没有发现任何问题才结束','已实现',['F15','F16','F17','F18','F19','F20','F21','F22','F33','F34','F35','F36','RF01','RF02','RF03','RF05','RM01','RM02','RM03','RM05','R-A01','R-A02'],'有效授权下，干净轮计1/2；问题、未检项、阻塞和版本变化归零；问题处置与报告去重有效。',['raw/F15.json','raw/F18.json','raw/RF01.json','raw/RM03.json','raw/F36.json']),
('R03','优化规则表述','已实现',['A02'],'SKILL总原则12、完工输出及verify规则明确了询问时机、启动条件、每轮基准、返修及终止条件。',['source-excerpts.json','raw/A02.json']),
('R04','优化执行流程','部分实现',['F01','F02','F06','F08','F10','F23','F24','F25','RF01','RM01','IOF01','IOM01','F46','M46'],'主流程、异常恢复与返修接续已实现；AR06-F01使授权字段为空白时仍放行。',['raw/IOF01.json','raw/IOM01.json','raw/F46.json','raw/M46.json']),
('R05','将规则嵌入该skill','已实现',['D01','D02','DF03','DM03','CLIF03','CLIM03'],'主skill、verify、close、minimal、status、公开脚本和两载体schema已连通；95安装文件一致，唯一保留差异符合已授权边界。',['source-excerpts.json','raw/D01.json','raw/D02.json','raw/DF03.json','raw/DM03.json']),
('R06','确保机制能够发挥作用','部分实现',['F02','F03','F06','F08','F10','F36','RF03','RM03','HF04','HM04','HPF01','HPM01','CLI01','CLI02'],'状态、证据、版本、兼容和失败恢复可运行；公开CLI仍能把全空白授权字段计为有效同意。',['raw/CLI01.json','raw/CLI02.json','raw/D01.json','raw/IO03.json']),
('R07','对抗性审查不能直接开始','部分实现',['F02','F03','F06','F08','F10','M02','M03','M06','M08','M10','F46','M46','CLI01','CLI02'],'无Offer/无Accepted/拒绝/推迟的正常路径均阻断；空白Decision凭据失效路径未阻断（AR06-F01）。',['raw/F03.json','raw/M03.json','raw/CLI-BLANK-DECISION-command.json']),
('R08','任务完成后主动询问用户是否需要进行对抗性审查','已实现',['F01','F04','F05','F11','RF08','M01','M04','M05','M11','RM08','A01','A02'],'Implemented留档后NotOffered提示主动询问；未完工不允许Offer，询问后等待真实选择；当前真实询问和明确答复与独立Pending验收分离。',['source-excerpts.json','raw/A01.json','raw/A02.json','raw/F04.json','raw/M04.json'])]
coverage=[{'id':rid,'source':'request_snapshot','quote':quote,'reading':reading,'status':state,'case_ids':ids,'actual':actual,'gap':'AR06-F01' if state=='部分实现' else None,'evidence_refs':refs} for rid,reading,state,ids,actual,refs in rows]
wr('original-requirement-coverage.json',coverage)
md=['本次任务使用的 skills：run-governed-product-workflow。','','原文（完整保留）：','','> '+quote,'','| ID | 拆出要求 | 状态 | 实际证据与差异 |','|---|---|---|---|']
for row in coverage:md.append('| '+row['id']+' | '+row['reading']+' | '+row['status']+' | '+row['actual']+' 用例：'+', '.join(row['case_ids'])+' |')
(A/'original-requirement-coverage.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
wr('verification-commands.json',{'cwd':str(R),'environment':{'PYTHONDONTWRITEBYTECODE':'1','python':'3.13.0','powershell':'7.6.5'},'top_level':[{'command':['python','-X','utf8','review_cases.py'],'phase':'first setup failure','output':'raw-setup-output.txt','direct_python_exit_not_captured':True,'result':'Uncaught schema error: synthetic R01 invalid; not a product issue.'},{'command':['python','-X','utf8','review_cases.py'],'phase':'corrected setup','output':'raw-setup-retry-output.txt','result':'Both carriers validate; NotOffered.'},{'command':['python','-X','utf8','execute_suite.py'],'output':'suite-output.txt','result':'92 assertions; 2 failing assertions for AR06-F01.'},{'command':['python','-X','utf8','execute_boundaries.py'],'output':'boundaries-output.txt','result':'141 cumulative assertions; 4 failing assertions for AR06-F01.'},{'command':['python','-X','utf8','execute_final_checks.py'],'output':'final-checks-output.txt','result':'158 cumulative assertions; 4 failing assertions for AR06-F01.'}],'exact_cli_io':'raw/*-command.json','api_input_output':'raw/api-events.jsonl plus per-case raw/*.json','note':'The original PowerShell wrappers ended with Get-Content; wrapper exit0 does not independently capture each Python exit code. Every public CLI invocation captures its actual returncode/stdout/stderr.'})
stats={'case_assertions':len(cases),'passed':sum(c['result']=='Passed' for c in cases),'failed':len(failed),'failed_case_ids':failed,'confirmed_findings':1,'severity_counts':{'P2':1},'unreviewed_items':[]}
summary={'round_id':'AR-06','review_complete':True,'result':'FindingsFound','clean_round':False,'started_at':'2026-10-23T13:51:58.3819499Z','finished_at':now,'archive_root':str(A),'delivery_task_id':'T-ADVERSARIAL-20261023-005','subject_sha256':'1ec6406b7c95580a24ef77723932c6bfd76fbd1a40bbf900f685f7261fd6acac','requirements_sha256':'57bfbf29e4c6814f1e5638d026ebc0c59a448ec654942469a082c53d94dd92ca','head':end['head'],'source_bundle_sha256':frozen['source_sha256'],'source_files_checked_start':96,'source_files_checked_end':96,'source_mismatches':end['mismatches'],'stats':stats,'findings':findings,'unreviewed_items':[],'exclusions':['No installed governance module was imported or executed; explicitly retained other-chat patch checked by hash, with allowed existing005 combination-test fact retained.','No real task, repository, installed source, Git commit, push, other chat or production operation was mutated.','Synthetic human choices, reports and engineering outcomes exist only in OS Temp; none represents a real approval or real clean review.'],'independence_incident':'independence-incident.json','tool_and_fixture_errors':['tool-setup-failure.txt','raw-setup-output.txt','setup-failure-source.py'],'evidence_index':'file-hashes.json','reproduction_script':'rebuild_all.py'}
report='''本次任务使用的 skills：run-governed-product-workflow。

# AR-06 只读独立对抗性审查

结论：发现 **1 个确认问题（P2）**。本轮不计为无问题轮次。158 个实际记录的断言：154 通过、4 失败；4 个失败均归属 AR06-F01。已检查约定范围，未检项为空。未修复源码或修改真实任务。

- 审查时间：{start} — {finish}（UTC）。
- 当前交付：`T-ADVERSARIAL-20261023-005`；工程 `Implemented`，审查 `ManagedByParent`，用户验收 `Pending`。
- 交付 subject：`1ec6406b7c95580a24ef77723932c6bfd76fbd1a40bbf900f685f7261fd6acac`。
- 原文绑定：`57bfbf29e4c6814f1e5638d026ebc0c59a448ec654942469a082c53d94dd92ca`。
- HEAD：`{head}`；源码 bundle：`{bundle}`。
- 开始和结束各核对96源码文件，差异均为0，见 [开始证明](freeze-start.json)、[结束证明](freeze-end.json)。
- 环境：Windows，Python 3.13.0，PowerShell 7.6.5；禁用Python字节码写入；只向OS Temp写夹具、脚本、输入、输出与报告。

## AR06-F01：空白授权关键字段被接受，并可生成审查 Passed（P2）

位置：`scripts/adversarial_review.py:24`、`:36–37`、`:139–142`（仓库skill目录下）。完整代码片段见 [源码证据](source-excerpts.json)。共享text仅要求minLength=1，空白字符串通过；状态重放仅凭outcome=Accepted开启会话。

最小复现：

1. 在Temp中建立已保存且已验证的Implemented工程结果，追加Offer。
2. 公开CLI追加Decision：`outcome="Accepted"`，`response=" \\t "`，`decided_by=" "`，`evidence_ref="\\t"`。
3. 实际返回exit 0，状态InProgress；再追加两份独立非空报告，最终返回Passed、clean_streak=2。

预期：拒绝缺少实际回答、实际决定人、可核对来源的空白Decision，保持AwaitingUser并禁止Round计数。实际：Full/Minimal公开API均接受；Full公开CLI也接受并最终通过。输入：[Decision](raw/CLI-BLANK-DECISION-entry.json)；输出：[CLI追加](raw/CLI-BLANK-DECISION-command.json)、[Round1](raw/CLI-BLANK-ROUND-1-command.json)、[Round2](raw/CLI-BLANK-ROUND-2-command.json)、[最终查询](raw/CLI-BLANK-STATE-command.json)。API对照：[Full](raw/F46.json)、[Minimal](raw/M46.json)。

影响：机器门禁将实际缺失的授权凭据视为有效同意，产生没有有效授权证明的Passed会话。本任务真实用户答复“开始审查”及其来源完整，本问题不否定当前实际授权。建议在共享schema/公共入口及重放校验中拒绝关键字段全空白值，保留合法原话，同步两种schema并补API/CLI反例。

## 原话逐项覆盖

完整原句与8条独立拆分均保存在 [逐条覆盖](original-requirement-coverage.md) / [结构化覆盖](original-requirement-coverage.json)，每项均保留同一来源完整原句及限定词。R01/R02/R03/R05/R08已实现；R04/R06/R07因AR06-F01部分实现，不将结构校验等同于语义正确或用户验收通过。

| 检查范围 | 实际验证 | 结果 |
|---|---|---|
| 完工、验证、留档后询问；询问/授权/人工验收独立 | F/M01–14、F/M39、F/M45、RF/RM08、A01/A02 | 正常分支通过；空白凭据反例失败 |
| 同版连续两轮、发现问题/未检项/阻塞清零、全部问题处置 | F/M15–22、33–38，RF/RM01–05，R-A01/02 | 通过 |
| 停止、恢复、会话完成后重新决定、时序和权限 | F/M23–30、40–42；RF/RM06–10；PF/PM01/02 | 通过 |
| 报告真实文件、内容去重、别名、删改、历史摘要不复用 | F/M31–35；HF/HM01–06 | 通过 |
| Full/Minimal和混合返修；新交付接续；不递归询问 | RF/RM01–08，CLI F/M03–05 | 通过 |
| 需求原文与澄清上下文绑定、说明更正不误失效 | B01、A02 | 通过 |
| 历史缺字段、旧干净轮不冒充现行通过、真正旧终态 | HF/HM07–09、HPF/HPM01 | 通过，读取不改写旧来源 |
| 失败恢复与原子性 | IOF/IOM01/02、IO03 | 原子替换注入失败后无落盘变化；原授权重试成功；44个被拒追加快照一致 |
| 公共CLI、状态/推荐/Markdown、Schema和分发 | CLI各例、F/M11和43、D01/D02、DF/DM03 | 除空白授权反例外通过 |

全部案例包含条件、实际输入、预期、实际、结果和相对证据路径，见 [cases.json](cases.json)。同一种协议在Full/Minimal分别执行，用于确认载体一致性，未将断言数量当作审查质量或真实轮次。没有重跑self_test代替本轮；既有工程验证仅用于明确安装端边界。

## 分发与范围

安装端96文件中95与冻结源码一致，唯一差异为用户明确保留的独立`governance_artifacts.py`补丁，SHA为`add9aff766c9b5ddb3eed0cdf5da8f7e464707648f5ea4870c98a462002ae153`，见 [差异核对](distribution-hash-differences.json)。未导入或改动该安装模块。允许读取的005安装组合验证事实单独保存于 [工程证据摘录](allowed-005-installed-engineering-evidence.json)，该既有结果不充当本轮对抗性审查。未重跑安装器、发布、GitHub或生产操作。

## 独立性与调用事件

本轮所有158条验证与问题独立复现完成后，14:08:50.1898947Z读取允许的005工程验证汇总时，终端意外同时显示了历史审查汇总字段及一个既有问题ID。未读取该问题描述或轮次报告，已停止读取；该ID不在本归档重复。API缺陷复现始于13:58:59Z，公开CLI证据已在14:03:05Z–14:03:06Z形成。没有使用暴露字段形成用例、预期或判断。已如实告知父Agent，并按其要求保留 [事件记录](independence-incident.json)。本轮读隔离限制未完全满足；本轮含确认问题，本就不构成无问题轮次。

调用/夹具错误全部保留：首次PowerShell命令误用Bash花括号参数语法，在解析阶段失败；首次合成需求ID写为R01，被schema要求R-01拒绝。已改正夹具后完成验证，未将其作为产品问题。记录见 [工具错误](tool-setup-failure.txt)、[初次夹具输出](raw-setup-output.txt)、[纠正后输出](raw-setup-retry-output.txt)、[原夹具脚本](setup-failure-source.py)。另有IO测试的OSError为明确标注的Temp定向故障注入，属于预期验证输入。

## 复建与证据

`python -X utf8 rebuild_all.py`会在新的OS Temp目录重建合成夹具并运行三个独立验证脚本；脚本不写仓库或安装端。执行前须保留本轮冻结源码版本；修复后重跑反例将改变预期失败统计。所有合成人的决定、报告及任务状态仅在Temp，均标注synthetic，不能登记到真实任务充当人工决定或真实轮次。

原始输入输出：[命令索引](verification-commands.json)、[API日志](raw/api-events.jsonl)、[主用例输出](suite-output.txt)、[边界输出](boundaries-output.txt)、[最终检查输出](final-checks-output.txt)。文件摘要：[file-hashes.json](file-hashes.json)。未检项：无；未执行安装端新运行、实际发布和真实数据变更为明确范围排除。
'''.format(start=summary['started_at'],finish=now,head=end['head'],bundle=frozen['source_sha256'])
(A/'report.md').write_text(report,encoding='utf-8')
summary['report_sha256']=sha(A/'report.md')
wr('summary.json',summary)
index=[{'path':p.relative_to(A).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(A.rglob('*')) if p.is_file() and p.name!='file-hashes.json']
wr('file-hashes.json',{'created_at':now,'excluded_self':'file-hashes.json','file_count':len(index),'total_bytes':sum(i['bytes'] for i in index),'files':index})
print(json.dumps({'started_at':summary['started_at'],'finished_at':now,'temp':str(A),'report_sha256':summary['report_sha256'],'stats':stats,'source_mismatches':end['mismatches'],'archive_files':len(index),'archive_bytes':sum(i['bytes'] for i in index)},ensure_ascii=False,indent=2))
