# 可复用模板

## 1. Requirements checklist

| ID | Requirement | Authority | Weight | Required output | Status | Evidence | Missing action |
|---|---|---|---:|---|---|---|---|

## 2. Evidence inventory

| Evidence ID | Path/source | Type | Version/date | What it proves | Reliability | Used in | Validation |
|---|---|---|---|---|---|---|---|

## 3. Traceability matrix

| Requirement ID | Code/source | Test/experiment | Raw output | Table/figure | Report section | PPT slide | Status |
|---|---|---|---|---|---|---|---|

## 4. Experiment plan

| Field | Value |
|---|---|
| Research question | |
| Hypothesis | |
| Input/data | |
| Independent variable | |
| Dependent variables | |
| Controls | |
| Warm-up/pilot | |
| Formal repetitions | |
| Statistics | |
| Correctness gate | |
| Raw schema/path | |
| Failure procedure | |
| Claim boundary | |

## 5. Required-question paragraph

```text
Direct answer:

Evidence:

Observation:

Explanation:

Theory/model/complexity:

Limitation:

Practical implication:
```

## 6. Figure/table audit

| ID | Caption states conclusion | Source | Unit | Metric | Body reference | Appendix reference | Readable | Values verified |
|---|---|---|---|---|---|---|---|---|

## 7. Code-change impact log

| Change | Tests | Formal outputs | Report text/code appendix | Figures/tables | PPT/UI | Submission package |
|---|---|---|---|---|---|---|

## 8. Submission manifest

| Artifact | Required name | Actual path | Size | SHA-256 | Format check | Content check | Upload status |
|---|---|---|---:|---|---|---|---|

## 9. Final issue list

| Priority | Root cause | Evidence | Requirement affected | Score/submission impact | Fix | Recheck |
|---|---|---|---|---|---|---|

## 10. Scope lock

| Field | Value |
|---|---|
| Requested deliverable | |
| Files/sections allowed to change | |
| Must remain unchanged | |
| Required verification | |
| Out-of-scope findings to report only | |

## 11. Official and internal standards ledger

| Check | Type: official / quality | Authority | Score effect | Current status | Action |
|---|---|---|---:|---|---|

只有 `official` 项可以直接影响正式评分。`quality` 项用于提升可读性、专业度或复现性，不得伪装成任务书处罚。

## 12. Teacher clarification log

| Date | Exact question | Exact answer | Applies to | Does not prove | Saved evidence |
|---|---|---|---|---|---|

## 13. Artifact freeze table

| Artifact | Workspace path | Upload candidate | Downloaded copy | SHA-256/status | Supersedes |
|---|---|---|---|---|---|

## 14. 可直接调用的总提示词

```text
请使用 $assignment-polishing 审查并改进当前课程作业。

先完整读取任务书、rubric、格式/提交要求、教师说明、当前源码、测试、
原始数据、程序输出、报告、图表、PPT和最终提交候选。建立权威顺序，
遇到冲突时报告冲突，不自行猜测。

先建立 requirements checklist、evidence inventory、traceability matrix 和
report outline，再决定需要修复代码、补实验、重算证据还是只修改表达。

所有 required question 使用“直接结论 → 证据 → 观察 → 原因 → 理论/复杂度
→ 局限 → 实际意义”。不得虚构结果、引用、实现、经历或贡献。缺失证据要
明确列出。

代码修改应保持学生可解释、职责清楚和最小必要复杂度；正确性先于性能，
核心算法先于展示层。任何代码变化都要检查测试、输出、报告、图表、PPT和
提交包的连带影响。

最终在干净临时环境验证构建、测试、运行和提交包；实际渲染文档和PPT；
检查命名、页数、格式、隐私、AI过程文件和跨制品一致性。输出已验证事项、
问题优先级、修改记录、最终路径和仍需作者确认的内容。

把任务书明确要求与内部高标准分开。严格评分只使用前者。先锁定本轮允许
修改的范围；若只是局部修改，不得顺手重写其他内容。制作型任务先交付一个
完整可用版本，再审计和迭代，不能用无限检查代替成品。
```
