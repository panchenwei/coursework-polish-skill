# 实验设计与证据链

## 1. 预注册式实验卡

每个重要实验先写：

| Field | Content |
|---|---|
| Question | 要回答什么 |
| Hypothesis | 预期及理由 |
| Inputs | 数据和选择规则 |
| Independent variables | 主动改变什么 |
| Dependent variables | 测量什么 |
| Controls | 固定什么 |
| Correctness gate | 什么情况下停止 |
| Repetitions | 预热、pilot、formal次数 |
| Statistics | mean/median/IQR/SD等 |
| Raw output | 保存位置和schema |
| Expected limitation | 能说明什么、不能说明什么 |

## 2. 正确性先于计时

性能实验前必须验证：

- 所有算法结果正确；
- 多个实现输出一致；
- 排序或变换未丢失/复制记录；
- 查询路径和分量合法；
- 输入副本、I/O、验证、输出和绘图不进入不应计时的区域。

若正确性失败，正式计时无效。

## 3. 计时实验

在 JVM、解释器或有 JIT/GC 的环境中：

- 使用预热；
- 做 pilot 检查漂移和分辨率；
- 正式实验重复多次；
- 保留所有 raw values；
- 明确使用的集中趋势和离散指标；
- 使用同一机器、运行时和条件；
- 轮换算法顺序，避免固定顺序偏差；
- 不把不同平台的 wall-clock 值混在同一正式比较中。

操作计数、访问节点、检查边数、写入次数、递归深度等平台无关指标可以补充 wall-clock，但必须明确定义计数口径。

## 4. 受控实验与观察性比较

不同数据集之间的差异通常同时包含规模、分布和顺序，属于观察性证据。若要声称某个因素造成结果，尽量对同一记录集合只改变一个变量。

报告中区分：observed result、controlled result、theoretical expectation、inference和unverified claim。

## 5. Scaling与复杂度

真实 scaling 数据用于说明当前范围内的增长趋势，Big-O用于理论外推。小规模实验不能证明渐近复杂度。

复杂度推导应连接实际实现：

1. 定义变量；
2. 指出主循环、递归或数据结构操作；
3. 计算执行次数或访问上界；
4. 合并并化简；
5. 区分 best/average/worst；
6. 区分输入存储和 auxiliary space；
7. 说明实现选择如何影响边界。

## 6. Raw-to-summary验证

汇总文件不是独立真相。表图生成前应从 raw data 重新计算关键统计，并与 summary 比较。

验证行数和分组、缺失或重复trial、单位、统计口径、rounding tolerance、异常值保留和版本一致性。

## 7. 图表选择

- 精确 required output：表格；
- 分布和离群值：boxplot；
- 随规模变化：line chart；
- 多维相对比较：适量 heatmap；
- 组成分布：bar chart通常优于饼图；
- 路径或拓扑：graph/tree/layer visual；
- 不制作重复表达相同结论的装饰图。

每张图记录：source artifact and rows、metric and unit、transformation、question supported、direct conclusion、limitations和使用位置。

## 8. 失败实验处理

- 记录失败条件；
- 判断是实现错误、协议错误还是环境噪声；
- 修复原因，不美化结果；
- 若改变协议，记录前后差异和理由；
- 新旧运行不能混合；
- 未通过 pilot 时不得继续正式结论。
