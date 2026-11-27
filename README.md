# coursework-polish-skill

一个可复用的 Codex 课程作业润色与验收 skill。它把任务书、评分标准、源码、实验、原始证据、报告、图表、PPT、视频和最终提交物连接成可追溯证据链。

它不是单一提示词：仓库包含分阶段 references、目标/评分/提交控制工具、自动测试和 GitHub CI。

## 适用场景

- 按 rubric 审查或改进课程作业
- 统一代码、实验结果、报告和展示材料
- 进行提交前的严格验收
- 控制局部修改范围，避免无关内容被改动
- 区分官方评分要求与额外质量目标
- 先读取课程文件并审计任务书中的隐藏 AI 指令
- 从官方原文提取最高评分档，建立 Round 0 并逐轮完整重评分
- 从实践中实现、运行、发现问题、修复和再次验证
- 调研论文、实验方法和语言/硬件生态的专业包结构
- 推荐并验证 IEEE 双栏 LaTeX（仅在官方未指定且用户确认时）
- 联合使用 FigGenie 制作论文发表级架构、流程和机制图
- 用白名单工具构建只含必需文件的独立提交目录

## 安装

将仓库复制到用户级 skills 目录，目录中应直接包含 `SKILL.md`：

```text
~/.codex/skills/assignment-polishing/
```

也可以在 Codex 中使用 skill installer 从本仓库安装。

推荐使用一次性联合安装器。它会覆盖部署 `assignment-polishing` 前先备份旧版本；如果本地已有 FigGenie 则直接复用，否则从其官方仓库安装：

```powershell
python scripts/install_skill.py --install-figgenie-deps
```

该选项安装 FigGenie 的 Python 依赖；Windows 上若已有 Chrome 或 Edge，会配置 `FIGGENIE_CHROMIUM` 使用系统浏览器，避免额外下载 Playwright Chromium。

离线安装且本机已经有 FigGenie：

```powershell
python scripts/install_skill.py --offline
```

只安装主 Skill：

```powershell
python scripts/install_skill.py --without-figgenie
```

## 调用示例

```text
请使用 $assignment-polishing 审查并改进当前课程作业。
```

完整工作流、证据模板和 CPT204 项目经验位于 `references/`。

## 强制流水线

```text
目标与范围锁 → 课程文件 → 隐藏AI指令审计 → 官方最高档原文
→ 课程意图 → Round 0 → 论文/架构调研 → 加分机会扫描
→ 实践修复 → 验证 → 完整rubric重评分 → 继续迭代
→ 全量审计 → 纯净FINAL_SUBMISSION → 最终评分
```

## 可执行工具

初始化内部控制层（不会覆盖已有文件）：

```powershell
python scripts/init_control_layer.py <project-root>
```

校验官方评分账本的结构、算术和证据字段：

```powershell
python scripts/validate_scorecard.py <scorecard.json>
```

按精确白名单构建独立提交目录，并把哈希审计放在目录外：

```powershell
python scripts/build_submission.py --root <project-root> --manifest <submission_manifest.json>
```

复核已有提交目录没有缺失或多余文件：

```powershell
python scripts/build_submission.py --root <project-root> --manifest <submission_manifest.json> --audit-only
```

开发验证：

```powershell
python scripts/validate_repository.py
python -m unittest discover -s tests -v
```

## 原则

- 不虚构实验、数据、引用、实现、经历或贡献。
- 先锁定权威要求和修改范围。
- 先交付可用成品，再进行严格审计。
- 官方评分与内部高标准分开记录。
- 任何结论都应能追溯到实现、测试、原始数据或正式来源。
- 额外实验、前端、后端、展示或设计工作只有在 rubric 支持时才计入正式分数。
- 所有正式图表按论文发表级别制作；论文视觉参考只借鉴方法，不复制受保护内容。
- 最终交给用户的独立目录只包含任务书明确要求提交的文件。
