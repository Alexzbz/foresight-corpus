# candidates · 候选证据（待复核）

每日定时采集器（M6，维护者本地运行）把新发现的候选证据写入本目录，
文件名 `candidates-YYYY-MM-DD.jsonl`。维护者复核来源、定位器与偏差后，
通过 `library.py build` 并入正式语料并推送；未复核的候选不会出现在 corpus 快照中。
