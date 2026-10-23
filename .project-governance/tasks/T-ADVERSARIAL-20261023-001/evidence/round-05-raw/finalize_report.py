from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,platform,importlib.metadata,zipfile
T=Path(__file__).parent
R=Path(r'D:/LFEN_project/dev_project/LFen-Skills')
S=R/'skills/product-engineering/run-governed-product-workflow'
def now():return datetime.now(timezone.utc).isoformat().replace('+00:00','Z')
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
start=json.loads((T/'environment-start.json').read_text(encoding='utf-8'))
cases=json.loads((T/'cases.json').read_text(encoding='utf-8'))
commands=json.loads((T/'commands.json').read_text(encoding='utf-8'))
manifest_path=R/'.project-governance/tasks/T-ADVERSARIAL-20261023-005/evidence/source-files-f0f3ce7fedddffcc.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
(T/'frozen-source-receipt.json').write_bytes(manifest_path.read_bytes())
actual=[{'path':entry['path'],'sha256':sh(R/entry['path'])} for entry in manifest['source_files']]
bundle=hashlib.sha256(json.dumps(actual,ensure_ascii=False,sort_keys=True).encode('utf-8')).hexdigest()
freeze={'checked_at':now(),'count':len(actual),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'expected_sha256':manifest['source_sha256'],'actual_sha256':bundle,'all_files_match':actual==manifest['source_files'],'matches_start':all(x['matches'] for x in json.loads((T/'freeze-start.json').read_text())['files']),'source_files':actual}
assert freeze['all_files_match'] and freeze['actual_sha256']==freeze['expected_sha256']
assert freeze['head']==start['head']=='d7264d7898cd9695cb2d464f98fa9630bea27659'
dump(T/'freeze-end.json',freeze)
# Original requirement/clarification input, filtered so no prior Round conclusions enter this report.
before=json.loads((R/'.project-governance/tasks/T-ADVERSARIAL-20261023-001/before.json').read_text(encoding='utf-8'))
source={'request_snapshot':before['request_snapshot'],'clarification':before['clarification'],'trusted_current_review_consent':json.loads((T/'actual-consent-source.json').read_text(encoding='utf-8'))}
dump(T/'requirement-source.json',source)
quote=source['request_snapshot']['text']
assert len(source['clarification']['rounds'])==0
rows=[
('REQ-01','针对当前任务开展多轮对抗性审查。',['AR05-C011','AR05-C016','AR05-C019','AR05-C022','AR05-C036','AR05-C145','AR05-C149','AR05-C159'],['任务与返修归属保持在原审查任务','多轮无固定上限，不在一轮后结束']),
('REQ-02','只有连续两轮均未发现任何问题才能结束。',['AR05-C016','AR05-C017','AR05-C018','AR05-C023','AR05-C025','AR05-C026','AR05-C028','AR05-C029','AR05-C030','AR05-C031','AR05-C033','AR05-C052','AR05-C067','AR05-C294','AR05-C304'],['首轮完整干净记1','第二轮同版完整干净记2并结束','发现问题、未解决项、未检项、阻塞、交付歧义或版本变化清零']),
('REQ-03','优化规则表述，明确启动、每轮检查、计数和结束标准。',['AR05-C310'],['真实原文逐条复核','完整同版两轮无问题与无未检/未决项','不以单次普通测试或复制报告冒充审查']),
('REQ-04','优化可执行流程，发现问题后修复、复验、保存新交付再审。',['AR05-C075','AR05-C082','AR05-C092','AR05-C094','AR05-C102','AR05-C145','AR05-C151','AR05-C152','AR05-C153','AR05-C154','AR05-C155','AR05-C156','AR05-C173','AR05-C299','AR05-C309'],['问题先登记并归零','Fixed绑定新验证交付','停止和已结束证明失效后必须真实新决定']),
('REQ-05','把规则与流程嵌入该 skill 的实际入口。',['AR05-C219','AR05-C220','AR05-C221','AR05-C222','AR05-C226','AR05-C227','AR05-C256','AR05-C257','AR05-C290','AR05-C310'],['主skill、verify、close、Minimal、status入口一致','共享Schema/协议与安装分发一致']),
('REQ-06','机制能够发挥作用，状态、证据与异常路径可核对。',['AR05-C098','AR05-C102','AR05-C179','AR05-C181','AR05-C186','AR05-C198','AR05-C206','AR05-C207','AR05-C208','AR05-C209','AR05-C210','AR05-C211','AR05-C213','AR05-C214','AR05-C217','AR05-C218','AR05-C219','AR05-C222','AR05-C248','AR05-C250','AR05-C278','AR05-C280'],['原话与报告摘要绑定','历史不追溯伪造新证明','并发追加不丢失用户决定','派生推荐与Markdown按当前证明显示']),
('REQ-07','对抗性审查不能直接开始。',['AR05-C003','AR05-C004','AR05-C006','AR05-C008','AR05-C010','AR05-C039','AR05-C040','AR05-C042','AR05-C044','AR05-C046','AR05-C212','AR05-C215'],['无Offer或无明确Accepted不得Round','沉默、拒绝、推迟及普通验收同意均不授权']),
('REQ-08','必须在工程任务完成并保存结果后再询问。',['AR05-C001','AR05-C002','AR05-C037','AR05-C038','AR05-C223','AR05-C224'],['完工前/结果未保存时阻断','真实留档时间早于真实Offer']),
('REQ-09','主动询问用户是否需要审查，允许明确选择。',['AR05-C005','AR05-C007','AR05-C009','AR05-C011','AR05-C041','AR05-C043','AR05-C045','AR05-C047','AR05-C223','AR05-C225','AR05-C226','AR05-C229','AR05-C232','AR05-C235','AR05-C256','AR05-C259','AR05-C262','AR05-C265','AR05-C310'],['NotOffered提醒主动询问','用户实际同意后启动','未答/拒绝/推迟不自动催问且保留工程结果'])]
coverage=[]
by_id={c['id']:c for c in cases}
for rid,reading,ids,conditions in rows:
    coverage.append({'id':rid,'source':'request_snapshot','quote':quote,'reading':reading,'conditions':conditions,'status':'已实现','case_ids':ids,'evidence':[{'case_id':cid,'artifacts':[Path(p).relative_to(T).as_posix() if Path(p).is_relative_to(T) else p for p in by_id[cid]['evidence']],'result':by_id[cid]['result']} for cid in ids]})
assert all(e['result']=='Passed' for r in coverage for e in r['evidence'])
dump(T/'coverage.json',coverage)
# Compact traceable case index with paths relative to the archive root.
case_index=[]
for c in cases:
    case_index.append({'id':c['id'],'name':c['name'],'result':c['result'],'classification':c.get('classification'),'corrected_by':c.get('corrected_by'),'evidence':[Path(p).relative_to(T).as_posix() if Path(p).is_relative_to(T) else p for p in c['evidence']]})
dump(T/'case-evidence-index.json',case_index)
corrections=[{'artifact':f'fixture-error-{i:02}.txt','classification':'FixtureError','cause':cause} for i,cause in [(1,'Full夹具缺少development_type_scopes。'),(2,'Full夹具scope.in_scope与类型作用域不匹配。'),(3,'Full夹具缺少actual_execution/authority_available事实。'),(4,'Full夹具缺少结构化Authority评估。')]]
corrections += [{'artifact':'fixture-error-05-schema-path.txt','classification':'FixtureError','cause':'Schema检查器按properties直接取Minimal outcome，实际定义位于oneOf[1]。已纠正并通过C222。'}, {'case_ids':['AR05-C190','AR05-C202'],'classification':'FixtureError','cause':'历史夹具把*_at改为历史时间，但未改ledger.timestamp，实际输入仍是现行记录。系统正确拒绝。纠正输入后C217/C218通过。'}]
dump(T/'fixture-corrections.json',corrections)
# Bundle all synthetic fixture files, including intentionally remaining altered/missing report scenarios.
with zipfile.ZipFile(T/'fixture-snapshot.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
    for p in sorted((T/'fixtures').rglob('*')):
        if p.is_file():archive.write(p,p.relative_to(T).as_posix())
end=now()
env={'start_utc':start['start_utc'],'end_utc':end,'platform':platform.platform(),'python':sys_version if False else platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'powershell':start['powershell'],'git':start['git'],'source_head':freeze['head'],'source_bundle_sha256':bundle,'frozen_files':len(actual)}
dump(T/'environment-end.json',env)
failed=[c for c in cases if c['result']=='Failed']
assert len(failed)==2 and all(c.get('classification')=='FixtureError' and by_id[c['corrected_by']]['result']=='Passed' for c in failed)
summary={'review_id':'AR-05','reviewer':'/root/adversarial_round_05','coverage':'Complete','started_at':start['start_utc'],'ended_at':end,'delivery_task_id':'T-ADVERSARIAL-20261023-005','subject_sha256':'1ec6406b7c95580a24ef77723932c6bfd76fbd1a40bbf900f685f7261fd6acac','requirements_sha256':'57bfbf29e4c6814f1e5638d026ebc0c59a448ec654942469a082c53d94dd92ca','source_head':freeze['head'],'source_sha256':bundle,'frozen_files':96,'raw_case_count':len(cases),'passed':len(cases)-len(failed),'fixture_input_failures_corrected':len(failed),'effective_obligations_passed':len(cases)-len(failed),'findings':[],'unreviewed_items':[],'unresolved_items':[],'limitations':['本轮仅为一次独立完整审查，不代表已满足整个会话连续两轮条件。','状态与摘要只能核验记录关系，不能证明任意人填入的自然语言来源真实；真实同意另核对原件及父任务提供的工具答复来源。','删除/篡改报告的用例刻意保留其末态；原始命令结果及历史摘要见raw-phase1与fixture-snapshot.zip。'],'user_decision':'Pending','report_ref':'report.md','cases_ref':'cases.json','coverage_ref':'coverage.json','commands_ref':'commands.json','case_evidence_index_ref':'case-evidence-index.json','source_excerpts_ref':'source-excerpts.json','fixture_archive_ref':'fixture-snapshot.zip'}
dump(T/'summary.json',summary)
markdown=f'''本次任务使用的 skills：run-governed-product-workflow。

# AR-05 独立只读对抗性审查

本轮完整审查未发现确认问题；`findings=[]`、`unreviewed_items=[]`、`unresolved_items=[]`。本结论只代表这一轮；用户 Acceptance 保持 Pending。

- 执行者：`/root/adversarial_round_05`，新的只读独立执行者；未创建其他 Agent，未修复或改动仓库/安装端/真实任务记录，未提交或推送。
- 实际 UTC：`{start['start_utc']}` 至 `{end}`。
- 交付：`T-ADVERSARIAL-20261023-005`，subject `1ec6406b7c95580a24ef77723932c6bfd76fbd1a40bbf900f685f7261fd6acac`。
- 原需求绑定：`57bfbf29e4c6814f1e5638d026ebc0c59a448ec654942469a082c53d94dd92ca`。
- 源码：HEAD `{freeze['head']}`；开始/结束均核对同一96文件，bundle `{bundle}`，无变动。见 [开始冻结](freeze-start.json)、[结束冻结](freeze-end.json)、[原始清单](frozen-source-receipt.json)。
- 环境：PowerShell {start['powershell']}、Python {platform.python_version()}、{start['git']}、jsonschema {env['jsonschema']}。见 [环境](environment-end.json)。

## 原文逐项覆盖

完整原话（没有额外澄清回答）：

> {quote}

由原话独立提取以下9项；[coverage.json](coverage.json) 的每项均保留完整原话、限定条件、结果及可归档的案例和原始输出路径，不以任务卡替代原话。

| 编号 | 独立提取要求 | 结论 | 主要证据 |
|---|---|---|---|
'''
for rid,reading,ids,_ in rows:
    markdown+=f'| {rid} | {reading} | 已实现 | {", ".join(ids[:6])}{"；完整映射见coverage.json" if len(ids)>6 else ""} |\n'
markdown+='''
## 实际验证与反例

自建夹具并实际调用公开 CLI 与最小 API；没有调用已有 self_test。夹具中的人类决定、报告及问题均明确标记为 synthetic，仅存在 OS Temp。

| 约定检查范围 | 代表性实测案例 |
|---|---|
| 完工留档后真实主动询问、明确同意后才审查 | C001–C015、C037–C051、C223–C225；真实 Offer 09:34:53Z 晚于工程留档 09:34:07Z，实际同意 09:58:06Z。普通 Acceptance 不授权：C212/C215。 |
| 完整原话逐条核对、独立反例与独立报告 | C310 的源码与指令人工复核；本轮 coverage.json 独立拆句。报告路径、内容副本、别名、历史摘要复用、篡改和删除反例：C075–C144。 |
| 同版连续两轮无任何问题且无未检/未决项 | C016–C036、C052–C072；发现问题、Incomplete、未检项、未解决问题、Blocked 分别归零，第三轮禁止旧会话继续。 |
| 发现问题后新任务返修、复验、保存新交付再审 | C145–C178；Full/Minimal及跨载体返修、ManagedByParent、直接依赖、旧版拒绝、Fixed必须新交付。 |
| 拒绝、推迟、停止、恢复、授权与时间边界 | C007–C022、C043–C058、C082–C087、C118–C123、C102–C107、C138–C143；未来/无时区/早于留档与前轮时间均拒绝且文件未变。 |
| 当前交付歧义、版本失效与授权结束边界 | C294–C309；并列最新返修不计数；已结束会话版本/报告证明失效为RestartRequired，必须真实新决定。 |
| 历史读取与失败恢复 | C179–C218；无新字段保持LegacyUntracked，不自动入会；旧协议两轮为LegacyNotRevalidated；身份损坏仍拒绝；修正历史夹具输入后读操作不改源字节。 |
| 原话、澄清上下文及证据绑定 | C075/C076、C111/C112、C206–C210；原话/原问题/推荐默认/答复变动影响绑定，说明basis/survey/capture时间不变更原话绑定。 |
| 用户决定独立、历史追加及并发不丢失 | C032/C068、C211–C215、C300；并发Offer与user_decision均保留，通用amend不能删除审查或重写返修归属。 |
| Full/Minimal状态、推荐及Markdown一致 | C226–C285；NotOffered、AwaitingUser、Declined、Deferred、InProgress、Blocked、Stale、Passed、RestartRequired、Stopped十种状态；仅已同意未结束会话提示继续。 |
| Schema、分发与安装端公开入口 | C219–C222、C286–C290；源码/安装端Manifest全量匹配，12个审查相关分发文件相同，Full/Minimal均等于共享Schema，安装端真实CLI完成合成两轮。 |

共310条检查记录：308 Passed；2条 Failed 均为夹具输入错误，已明确归因并由C217/C218纠正重跑通过。没有未执行案例，没有未解决产品缺陷。原始失败保留，未冒充产品缺陷或静默改成通过。

- C190/C202：夹具错误地保留现行 ledger.timestamp，输入不满足其自称的历史条件；产品按现行记录正确拒绝。纠正后通过 C217/C218。
- 初始化及检查器另有5次调用错误：缺少类型作用域、作用域不匹配、未知执行/权限事实、缺少Authority结构、Minimal Schema oneOf取值路径。错误全文与修正原因见 [fixture-corrections.json](fixture-corrections.json) 和 fixture-error-* 文件。

## 问题与未检项

确认问题：无。未检项：无。未决项：无。未为扩大范围创建新业务要求。

真实审查启动同意另核对 [询问原件](actual-offer-source.json)、[同意原件](actual-consent-source.json)，与父任务提供的 `user-question-reply://current-thread/call_8cd6b5e9865947c0874609e44fcfba2c/0` 一致。未读取原任务既有轮次报告或问题清单；只提取了Offer/Decision与原话字段。最新交付before/after及验证冻结材料仅作为允许的交付输入。

## 可归档证据

- [summary.json](summary.json)：机器可读轮次结论、版本与统计。
- [coverage.json](coverage.json)、[requirement-source.json](requirement-source.json)：完整原话逐项对照。
- [cases.json](cases.json)：每条条件、输入、预期、实际、结果与证据；[case-evidence-index.json](case-evidence-index.json) 提供归档根目录相对路径。
- [commands.json](commands.json)、raw-phase1/、raw/、phase*-console*.log：逐次原始命令、UTC、退出码、stdout/stderr；逐条案例直接引用对应文件。
- independent_suite.py、phase2.py、phase3.py、phase3-fixture-retry.py、phase4.py、phase5.py：本轮自建测试实现；fixture-snapshot.zip保存全部合成任务末态，inputs/保存实际CLI输入。针对删除/篡改报告的测试刻意保留末态，命令原始结果保留先前登记摘要。
- [source-excerpts.json](source-excerpts.json)：实际核对的源码/指令行号与文件哈希。
- [file-index.json](file-index.json)：所有归档文件的相对路径、长度及SHA-256；索引不包含自身，避免自引用。

结构和摘要校验不替代自然语言审查或真实人的决定。此报告不宣称绝对无缺陷，不替代连续两轮会话判定、用户Acceptance或发布批准。
'''
(T/'report.md').write_text(markdown,encoding='utf-8')
# Keep every evidence file addressable after the directory is copied as a unit.
files=[{'path':p.relative_to(T).as_posix(),'bytes':p.stat().st_size,'sha256':sh(p)} for p in sorted(T.rglob('*')) if p.is_file() and p.name!='file-index.json']
dump(T/'file-index.json',{'generated_at':now(),'excludes':['file-index.json'],'file_count':len(files),'files':files})
print(json.dumps({'start_utc':start['start_utc'],'end_utc':end,'report':str(T/'report.md'),'report_sha256':sh(T/'report.md'),'case_count':len(cases),'passed':len(cases)-len(failed),'fixture_failures_corrected':len(failed),'findings':[],'unreviewed_items':[],'bundle':bundle,'index_files':len(files),'fixture_zip_bytes':(T/'fixture-snapshot.zip').stat().st_size},ensure_ascii=False,indent=2))
