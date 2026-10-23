import hashlib,json
from pathlib import Path
b=Path(__file__).resolve().parent
obs=json.loads((b/"installation-observation.json").read_text(encoding="utf-8"))
rp=b/"report.json"; report=json.loads(rp.read_text(encoding="utf-8"))
old=report["ended_at"]; report["ended_at"]=obs["observed_at"]
report["environment_observations"]=[{"classification":"EnvironmentChangeNotCodeFinding","initial_check":"FZ-01: 96 文件全一致","observation":obs,
"note":"固定源文件摘要未变化；安装目录出现新增 dirty-worktree baseline 逻辑，来源未确认。审查 Agent 未修改该目录，交由主会话核对。"}]
rp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
p=b/"report.md"; s=p.read_text(encoding="utf-8").replace(old,obs["observed_at"])
s=s.replace("已对源、安装克隆及 Codex Junction 入口的全部 96 文件逐项 SHA256 核对；审查末尾无受审文件漂移，当前提交仍固定。",
"初始 FZ-01 对源、安装克隆及 Codex Junction 的 96 文件逐项 SHA256 核对一致；结束时固定源 96 文件仍无漂移，但安装目录出现下述环境变化。")
s=s.replace("Full per-case input / expected / actual / result: cases.json (146 cases).","逐例 input / expected / actual / result 完整记录见 cases.json（146 例），并保留原始分组 JSON。")
s+="\n## 安装环境末尾观察（不列为第三项代码发现）\n\n"
s+=f"- 观察 UTC：{obs['observed_at']}。\n"
s+=f"- 固定源码：{obs['source']['path']}；SHA256={obs['source']['sha256']}，{obs['source']['bytes']} 字节。\n"
s+=f"- 安装克隆及其 Codex Junction：{obs['installed']['path']}；SHA256={obs['installed']['sha256']}，{obs['installed']['bytes']} 字节。\n"
s+="- 最小差异：安装版 capture_source_snapshot 新增 worktree_baseline；新增 _git_path_states；reconcile_scope 新增 dirty-path-bytes-v1 对照与 preexisting_unchanged。不是仅换行变化。\n"
s+="- 初始检查相符、末尾偏离，变更来源未确认。审查执行者未写入安装路径；固定源码的两项反例结论不受影响。\n"
s+="- 原始摘要和逐行差异：installation-observation.json、installation-observation.diff。主会话独立核对该外部变化。\n"
p.write_text(s,encoding="utf-8")
rpath=b/"receipt.json"; r=json.loads(rpath.read_text(encoding="utf-8"))
r["ended_at"]=obs["observed_at"];r["report_sha256"]=hashlib.sha256(p.read_bytes()).hexdigest();r["environment_observation"]=str(b/"installation-observation.json")
rpath.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"ended_at":r["ended_at"],"report":str(p),"report_bytes":p.stat().st_size,"report_sha256":r["report_sha256"],"cases":r["case_file"],"findings":r["summary"],"observation":r["environment_observation"]},ensure_ascii=False,indent=2))
