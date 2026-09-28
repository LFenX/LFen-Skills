# README 引文与静态排版

- 变更时间：2026-09-28 20:40；根据用户反馈于 20:45 修订（UTC+8）。
- 涉及文件：`README.md`、`README.en.md`、本日志。
- 变更摘要：将两份 README 首页引言区的打字动效换为居中的英文小字号文字。保留[哈佛发布的 2017 年演讲书面稿](https://news.harvard.edu/gazette/story/2017/05/mark-zuckerbergs-speech-as-written-for-harvards-class-of-2017/)中的原句，并另以英文转述紧接着的 Facebook 例子，明确区分引文和转述。
- 修订原因：用户要求仅用英文、缩小字号、更换上一版粗体图片字形，并使段落意思更完整。上一版临时生成的引文 PNG 已移除。

## 验证

- 已核对哈佛演讲书面稿中引文及其后续 Facebook 例子。
- 已检查两份 README 引言区均为英文、`<small>` 小字号、居中、无打字动效及旧图片引用。
- `python scripts/update_catalog.py --check`：通过。
- `git diff --check`：通过。
- 未执行 GitHub 在线页面预览；本地浏览器文件预览受 URL 策略阻止。
