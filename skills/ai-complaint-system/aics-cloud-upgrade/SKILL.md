---
name: aics-cloud-upgrade
description: >-
  在本机按顺序升级 AI 客诉系统。用户说升级服务、拉取新镜像、重启 AICS 容器或挂维护页时使用。
  先确认镜像标签并拉取，读镜像说明，把维护页挂到 80 端口，停容器并备份生产库且不恢复旧 dump，
  核对发信总闸和全部邮箱 SMTP，做迁移与读取模型对拍，启动后检查每个容器，再把 80 端口切回正式服务。
description_en: >-
  Upgrade the on-host AICS stack from the Tencent CCR image
  ccr.ccs.tencentyun.com/aics/aics. Use when the user says 升级服务, 拉取新镜像,
  重启 AICS 容器, or 挂维护页. Confirm the tag, pull it, read the image README,
  put the maintenance page on port 80, stop containers, back up the production
  database without restoring an old dump, verify mail send settings and every
  mailbox SMTP account, run migrations and read-model parity, check every
  container, then switch port 80 back to the app.
---

# AICS 云端镜像升级

在这台机器上按下面的顺序做。维护页必须在停业务容器之前挂上。读取模型对拍通过之前不要启动 Web。不要先启动会写读取模型的容器，再补登录或数据卷。

部署目录：`/data/aics/deploy`。编排文件：`docker-compose.yml`。一次性任务镜像写在 `aics-run.sh` 的 `IMAGE=`。

公网入口是宿主机 nginx 的 80 端口，站点文件 `/etc/nginx/sites-available/aics`。正式服务在 `127.0.0.1:3025`，维护页在 `127.0.0.1:3027`。云上把外部 3025 转到这台机器的 80。

## 1. 确认镜像存在并拉取

登录仓库。用户指定了标签就拉取该标签。用户只说拉取最新、没有指定标签时，再按选择规则取标签。不要假定标签是 `latest`。

仓库：`ccr.ccs.tencentyun.com/aics/aics`，命名空间 `aics`。使用本机已经登录的 Docker 凭据拉取。不要把仓库密码写进技能、仓库或终端日志。标签列表要用 registry token，Basic 直接访问 `/v2/.../tags/list` 会 401：

```bash
# 用 ~/.docker/config.json 里登录成功后的 auth，向
# https://ccr.ccs.tencentyun.com/service/token?service=token-service&scope=repository:aics/aics:pull
# 换 Bearer，再请求 /v2/aics/aics/tags/list
```

选择规则：忽略 `V1.0.0`、`migration-*`、`qa-readonly-sql-*`，在 `*-dirty-<时间戳>` 里取时间戳最大的标签并 `docker pull`。用户点名的版本优先于这条规则。

标签在仓库里不存在就停，不要拿别的标签顶上。

## 2. 读镜像说明

拉取后、改配置和数据库之前，读镜像内 `/app/IMAGE-README.md`。说明和本文冲突时，以这版镜像说明为准。

这台机器已有生产库。按说明做增量迁移。不要把旧 dump 覆盖到 `ai_complaint_mail`，不要运行 `seed-migration-data.sh`，不要用完整 `prisma db seed` 补权限。常驻容器的 `RUN_MIGRATIONS` 保持关闭。

说明里要求单独执行、且用户没有点名要跑的脚本不要自动开。包括历史分类入队 `scripts/real-data/26-requeue-unclassified.ts --apply`，以及 `sent-translation` profile 下的发件箱翻译轮询。

## 3. 启动前检查

检查完再停容器。缺了就补上，不要带着缺口进入停机。

`/data/aics/deploy/.env` 里必须有：

```bash
MAIL_SEND_ALLOW_REAL_RECIPIENT=true
```

值不是 `true` 就改成 `true`。缺这一项，邮件发不出去。

同一份 `.env` 还要有 `MAIL_SMTP_ACCOUNTS`。应用不读 `SMTP配置.txt`，只认这个变量，格式是 `邮箱:口令`，多个账号用分号接起来。口令按第一个冒号切分，口令里不能带分号。

从 `/data/aics/deploy/SMTP配置.txt` 解析后写入。文件开头是 SMTP/IMAP 地址和端口，账号是一行邮箱、下一行口令，空行隔开。`MAILBOXES` 里的每一个地址都要有对应口令，文件里多出来的账号也要写上。缺任何一个，用该邮箱发信会报「未配置发件邮箱 … 的 SMTP 凭据」。不要把口令写进日志或汇报。

文件头里的 SMTP 主机和端口要和进程实际使用的一致。未单独设置 `MAIL_SMTP_HOST`、`MAIL_SMTP_PORT`、`MAIL_SMTP_SECURE` 时，代码默认是 `smtp.feishu.cn:465` 且走 SSL。和文件不一致就显式写上这三项。

`env_file` 只在容器创建时读入。改完 `.env` 后，发信相关容器要重建，`docker restart` 不会加载新值。

Cursor 登录用本机已经配置的 API 密钥。容器用户是 `1001:1001`，家目录挂载为 `/data/aics/deploy/agent-home` → `/home/nextjs`。不要把密钥写进仓库或汇报。

- 确认 `/data/aics/deploy/agent-home/.config/cursor/auth.json` 的 `apiKey` 与 `/data/aics/deploy/.env` 的 `CURSOR_API_KEY` 是同一把当前有效密钥。文件权限 `0600`，属主 `1001:1001`。
- 同一把密钥也在 `/root/.config/cursor/auth.json`。密钥轮换时三处一起改，不要把值写进本技能。
- 确认调用 agent 的服务（web、task-worker、live-watchdog、lark-listener）都只读挂载了 cursor-agent 二进制，并挂载了 `agent-home`。

再核对：

1. `imap-connect.json` 在数据卷里：`/var/lib/docker/volumes/aics-data/_data/samples/imap-connect.json`。记下 SHA256。web、读取模型 worker、一次性同步容器必须看到同一份，并与 `MAILBOX_SOURCE_MARKER_SHA256` 一致。
2. web、`mailbox-read-model`、以及任何一次性同步容器的 `/app/data` 都是卷 `aics-data`，`/app/storage` 都是卷 `aics-storage`。漏挂会导致派生投影被删，而 12 场景对拍仍可能通过。
3. 读镜像 `docker-entrypoint.sh`。若新增了角色而 compose 没有，补上服务。`mailbox-read-model` 必须和 web 一样挂这两卷，并设置 `MAILBOX_READ_MODEL_SYNC=1`。`.env` 里 web 使用 `MAILBOX_READ_MODEL=1`、`MAILBOX_READ_MODEL_SYNC=0`。
4. compose 把 `/data/aics/deploy/sql` 绑到 `/app/sql`。镜像里的 `002_message_change_log.sql` 必须出现在宿主机这个目录。不要用镜像里的旧 `001_init.sql` 覆盖宿主机已有的 `001_init.sql`。
5. 不要在这些挂载确认前启动 `mailbox-read-model`。它启动就会 `--write`。

把 compose 的 `x-image` 和 `aics-run.sh` 的 `IMAGE` 改成刚拉取的标签。`docker compose config --images` 必须全是这个标签。

## 4. 挂维护页

停业务容器之前做完这一步，并确认公网已经是维护页。

维护服务是 systemd 单元 `aics-maintenance.service`，工作目录 `/data/aics/maintenance`，监听 `3027`。先启动它。再把 `/etc/nginx/sites-available/aics` 里的 `proxy_pass` 改成 `http://127.0.0.1:3027;`，`nginx -t` 通过后重载 nginx。其余代理头和 `proxy_redirect` 不动。

用 `http://127.0.0.1/` 确认返回的是维护页正文。此时业务容器仍可留在 3025，直到下一步停掉。

## 5. 停容器并备份

维护页确认可见之后，停掉全部 `aics-*` 容器（含 web、live-watchdog、task-worker、lark-listener、imap-watchdog、tech-reminders、help-site、mailbox-read-model，以及若在跑的 sent-translate-watch）。不要停维护服务。

然后备份当前生产库，不要恢复旧 dump。本机没有 `sudo`，用 `runuser -u postgres`。`/data/aics/backup` 是 `0700`，postgres 写不进去时先 dump 到 `/tmp`，再移到 `/data/aics/backup`，记下 SHA256，删掉 `/tmp` 副本。

## 6. 按镜像说明升级并启动

生产迁移只跑一个实例，命令使用本次镜像和目标库。

web 使用 `pid: container:aics-live-watchdog`。看门狗停着时，不要对 web 做 `docker compose run`。迁移、权限和读取模型一次性命令改在 `mailbox-read-model` 上跑。

按镜像说明的顺序：

1. `prisma migrate deploy`。结束后 `migrate status` 必须是 Database schema is up to date。
2. 权限目录先预演，再 `--write`，再跑检查。检查必须输出 `PASS`。只补缺失目录及父链。
3. 跑镜像里的只读发布预检 `deploy/verify_mailbox_release.py`。预检失败就不要写读取模型。
4. 用同一 `/app/data`、`/app/storage` 跑一次 `scripts/real-data/35-sync-mailbox-read-model.ts --write --verify`。日志必须给出 `parity=pass` 和镜像说明要求的场景数。`sourceCount` 应等于 `projectedCount`。`removedCount` 必须解释清楚；草稿箱和已删除不进索引，这不算漏邮件。失败时检查点不会变成就绪，不要启动 Web。
5. 对拍通过后，`docker compose up -d --force-recreate` 启动已有常驻服务。不要带上 `sent-translation` profile，除非用户这次明确要求开启发件箱翻译。
6. 按镜像说明把生产 AI 设为 `paused=false`，再确认唯一的 AI 巡检在跑。IMAP 看门狗会自己启动 `app.serve`，不要另起第二个。若 `/app/data/imap-serve.pid` 里的号正好是新看门狗进程，而 `app.serve` 没起来，确认没有真实的 `app.serve` 后删掉这个过期 pid，让看门狗重新拉起。
7. 镜像说明里的发信头修复只做预演。有可修复行并且库已备份，才允许 `--apply`。

历史分类入队和发件箱翻译仍按第 2 节保持关闭，除非用户在这次升级里点名要跑。

## 7. 检查每个容器

每个业务容器的镜像 ID 必须是刚拉取的那个。然后核对：

- `aics-web` 健康检查通过，`http://127.0.0.1:3025/api/health` 返回 200。帮助站 `3026` 返回 200。
- 读取模型检查点版本与镜像内 `mailbox-model-version.json` 一致，状态 `READY`，`lastError` 为空，`lastSyncAt` 在说明允许的秒数内。镜像若要求观察一轮约 10 分钟的复核，等这一轮出现后再算通过。
- `aics-web` 环境里 `MAIL_SEND_ALLOW_REAL_RECIPIENT` 是 `true`，`MAILBOX_READ_MODEL` 是 `1`，`MAILBOX_READ_MODEL_SYNC` 不是 `1`。读取模型容器的 `MAILBOX_READ_MODEL_SYNC` 是 `1`。
- 在发信容器里用和 `smtpAccounts()` 相同的规则解析 `MAIL_SMTP_ACCOUNTS`（分号分隔，第一个冒号切分）。`MAILBOXES` 每个地址都要能取到非空口令。只核对地址是否齐，不要打印口令。
- 以 uid 1001 在 `aics-live-watchdog` 里用容器自带的 `CURSOR_API_KEY` 调一次 `composer-2.5`，结果必须是成功。二进制路径是 `CURSOR_AGENT_BIN`，不在默认 `PATH` 里。
- IMAP 这次启动之后的日志里没有 `must be owner of table messages`、缺少 `002_message_change_log.sql` 或新的 Traceback。只看本次 supervisor start 之后的行。
- AI 巡检进程在跑，`AiPipelineControl.paused` 为 false。

镜像说明要求用授权会话核对投影接口时，再用应急 owner 做短时会话，跑完只退出这次会话。不要做六页冷热耗时，除非用户这次明确要求。

任何一项失败，保持维护页，不要做下一步。

## 8. 切回正式服务

第 7 步全部通过之后，单独做这一步。不要和容器刚启动放在一起。

把 nginx 的 `proxy_pass` 改回 `http://127.0.0.1:3025;`，测试配置后重载。停掉 `aics-maintenance.service`。确认 `http://127.0.0.1/` 不再是维护页，`/api/health` 经 80 端口返回 200。

对用户汇报时不要复述 API 密钥、仓库密码、数据库口令和 SMTP 口令。
