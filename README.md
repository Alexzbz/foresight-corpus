# foresight-corpus · AI 硬件前瞻共享证据语料库

[ai-hardware-foresight](../ai-hardware-foresight) 技能的公共证据语料库：每条证据
带来源 URL、可定位的摘录（excerpt / locator）、发布层级（A-primary / B-expert /
C-secondary）与偏差标注，全部可回溯、可复核。

**当前版本：`lib-2026.10.22` · 357 条证据（339 个独立事件）· 260 个来源 · 7 个域 · schema v3（主题标签/来源类型/数值指标/事件聚类/核验状态）**
（consumer / home / medical-assistive / cross-domain / robotics / automotive / industrial，校验和见
[corpus/corpus-meta.json](corpus/corpus-meta.json)）

## 在线看板

- **网页看板**：[Alexzbz.github.io/foresight-corpus](https://Alexzbz.github.io/foresight-corpus/) —— 指标总览、域/层级/发布方分布、全文检索与逐条溯源（数据由仓库快照实时加载）
- CDN 直达（国内更快）：[cdn.jsdelivr.net/gh/Alexzbz/foresight-corpus@main/docs/index.html](https://cdn.jsdelivr.net/gh/Alexzbz/foresight-corpus@main/docs/index.html)

## 三种使用方式

| 方式 | 适合谁 | 说明 |
|---|---|---|
| **零配置在线检索** | skill 使用者 | 公共只读凭证已内置在 skill 中：`library.py search "关键词" --remote` 即查，无需注册 |
| **免注册整库下载** | 离线 / 自建检索 | 从 jsDelivr 直拉快照：`library.py pull --url https://cdn.jsdelivr.net/gh/Alexzbz/foresight-corpus@main/corpus/corpus.db` |
| **直接 SQL** | 数据分析 | Turso 在线库 `https://foresight-corpus-alex707.aws-ap-northeast-1.turso.io`（只读令牌随 skill 发行）或下载 `corpus/corpus.db` 本地查询 |

## 仓库结构

```
corpus/corpus.db            # 每周快照（SQLite + FTS5），tag 对应 lib-YYYY.MM.DD
corpus/corpus-meta.json     # 版本、条数、sha256 校验和
corpus/evidence/*.jsonl     # 按域导出的可 diff 明文（一行一证据）
corpus/evidence/sources.jsonl
candidates/                 # 每日采集的候选证据，维护者复核后进入 corpus
scripts/validate_corpus.py  # CI 完整性校验（可溯源、去重、FTS 覆盖、导出同步）
.github/workflows/ci.yml    # 每次推送 + 每周一自动校验
```

## 更新流程（维护者）

1. 本地合并通过校验的 run 产出：`library.py build --run <run-dir>`
2. 推送在线库：`library.py push`
3. 导出快照与按域 JSONL 到本仓库，更新 `corpus-meta.json`
4. 提交、打 tag（`lib-YYYY.MM.DD`）、推送 —— CI 自动校验，jsDelivr 自动分发

## 数据口径

- 证据按技能双门（schema + 诚实性门）入库：摘录/定位器必填、时间戳为真实时钟、
  单一来源不构成趋势；
- 每条证据的 `provenance` 记录采集方式与所属语料版本，报告可回溯到确切版本；
- 商业来源标注偏差（bias_notes），医疗/车载安全类声明须权威来源或标记未验证。

## 许可

数据许可见后续维护者声明；引用请指向具体 `corpus_id` 与语料版本号。
