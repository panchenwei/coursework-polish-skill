# FigGenie 集成与联合部署

## 1. 正式来源

FigGenie 官方仓库：

```text
https://github.com/Sleepy-Avacado/FigGenie-paper-diagram-skill.git
```

该仓库以 MIT 许可发布其代码和说明，并包含大量论文图参考、字体、范例和素材。论文图仍归原作者/出版方所有，只能用于研究和版式参考，不能当作新作业的可复制素材。

## 2. 为什么不直接复制进本仓库

完整 FigGenie 超过 500 MiB、包含一万余文件。直接复制会：

- 让主 Skill 下载和更新异常沉重；
- 重复上游历史，难以获得安全更新；
- 混合上游论文参考素材的版权和来源记录；
- 使普通文本润色用户也承担巨大下载成本。

因此采用一次性联合安装，而不是重新发布其完整资产。

## 3. 用户体验

用户下载本仓库后只运行一次：

```text
python scripts/install_skill.py
```

安装器：

1. 把本仓库部署为 `assignment-polishing`；
2. 检测本地是否已有 `figgenie-paper-diagram`；
3. 已存在时复用，不重复下载；
4. 仓库含 `vendor/figgenie-paper-diagram` 时优先离线部署；
5. 否则从官方仓库获取并部署；
6. 输出两个 Skill 的最终路径和安装状态。

可用 `--without-figgenie` 跳过，或用 `--offline` 禁止网络。覆盖本地 `assignment-polishing` 前自动备份旧版本。

## 4. 运行时检测

需要架构、流程、机制或状态图时：

1. 检查已发现的 Skills 中是否有 `$figgenie-paper-diagram`；
2. 存在时按其完整规范运行；
3. 不存在时告知用户，并提供联合安装器或其他矢量方案；
4. 不因缺少 FigGenie 阻塞数据图、报告或其他不依赖它的工作。

## 5. 论文参考到原创图的流程

```text
定义当前图的论证目标
→ 搜索同领域原始论文
→ 核验venue权威性（期刊影响因子/JCR；会议CCF/CORE/领域等级）
→ 记录论文、年份、venue、权威依据、figure编号和可借鉴的布局/编码
→ 不复制具体内容或受保护素材
→ 用当前项目事实写brief
→ 用户确认
→ FigGenie spec/plan/SVG
→ lint、渲染、视觉复核
→ SVG/PDF/PNG/caption交付
```

报告引用相关论文时按正常学术引用处理；视觉参考记录不能替代对当前项目架构和数据的验证。
