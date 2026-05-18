# Multi-Agent Orchestration 执行手册

本手册用于把一个长期、可拆分的软件任务交给多个 agent 协作完成，同时严格约束
`master agent` 的职责边界：

- `master agent`
  只负责拆分任务、维护和更新 checklist、启动和关闭 subagent、验收结果。
- `master agent`
  不直接修改实现代码，不补小修，不顺手改文档逻辑，不替 worker 收尾。
- 如果验收失败，`master agent`
  的动作是更新 checklist、记录失败原因、关闭当前 agent、重新指派新的 agent，而不是自己下场修复。

这份文档偏执行手册，重点不是“理念正确”，而是“如何稳定落地”。

## 1. 整体架构与角色分工

推荐把 multi-agent 协作拆成 4 个角色，其中 `explorer` 和验证用 `worker`
可以按需启用，不必每次都开。

所有 subagent 都遵循 4 条执行护栏：显式说明关键假设和阻塞、选择当前角色下最简单够用的路径、严格遵守分配边界、提供具体验证或 blocker。

`$karpathy-guidelines` 保持独立：实现 `worker` 默认显式带；`explorer` / 验证用
`worker` 只在高风险、歧义大或易越角色边界时显式带。

角色分工：

- `master`：常驻。接收目标、拆分任务、维护 checklist、分配 agent、关闭
  agent、做最终验收。禁止直接改实现代码或替 worker 修 bug。
- `explorer`：按需启用。做影响面分析、依赖梳理、拆分建议、风险识别。禁止
  提交最终实现或扩大写入范围。
- `worker`：按任务启用。在指定写入边界内完成代码/测试/文档改动，自跑最小
  验证。禁止擅自改 checklist 或跨边界改其他模块。
- 验证用 `worker`：按需启用。运行独立验证、复核验收命令、整理证据。禁止
  接管实现或在未授权时修改代码。

### 1.1 `master` 的职责边界

`master` 需要长期保持 session 干净，只保留对调度和验收真正有用的信息。

`master` 应该做的事：

- 把需求改写成可验收的 checklist item。
- 给每个 item 指定 `write_allowlist`、`acceptance_commands`、`done_definition`。
- 按阶段启动和关闭对应 agent。
- 查看交付摘要、检查 diff、运行最终验收。
- 根据结果把 item 更新为 `accepted`、`redo`、`blocked` 等状态。

`master` 不应该做的事：

- 直接打开文件修改实现。
- 在验收失败后自己补丁式修复。
- 把本来应该结构化记录进 checklist 的信息塞进大量自由文本。
- 长时间保留“万能 worker”不关闭，导致上下文和责任边界失控。

### 1.2 `explorer` 的适用场景

适合下面几类任务：

- 需求范围不清，先要摸清影响面。
- 老代码耦合复杂，不能直接拆 worker。
- checklist 还不够清晰，需要先识别依赖、风险和建议的拆分顺序。

`explorer` 的典型产物：

- 受影响模块清单
- 推荐拆分方案
- 并发可行性判断
- 依赖/阻塞项清单
- 建议的验收命令

`explorer` 默认只用内建执行护栏；高风险、歧义大或易 scope drift 时再显式带
`$karpathy-guidelines`。

### 1.3 `worker` 的默认工作方式

推荐让 `worker` 只领取一个 checklist
item，或者只领取同一阶段内写入范围完全不重叠的一组 item。

`worker` 默认显式带 `$karpathy-guidelines`，避免过度实现、顺手重构或验证不足。

`worker` 的交付必须包含：

- `changed_files`
- `commands_run`
- `result`
- `remaining_risks`
- `ready_for_acceptance`

如果 `worker` 没跑任何验证，也必须明确写出“未验证”以及原因，不能默认由 `master`
自行推断。

### 1.4 验证用 `worker` 的适用场景

当下面任一条件成立时，建议启用验证用 `worker`：

- 变更风险高，不能只依赖 `worker` 的自测。
- 验收命令耗时长，适合由独立 agent 处理。
- 同一阶段有多个 worker 并发交付，需要统一收集验证证据。

验证用 `worker`
可以是“只读验证者”，也可以被授权写少量测试基线或验证脚本；但如果它开始承担实现职责，就不再是验证任务，而是另一个实现
`worker`。

验证用 `worker`
默认只用内建执行护栏；验证歧义大、环境敏感或易演变成诊断/修复时再显式带
`$karpathy-guidelines`。

## 2. Checklist 设计原则与状态流转

checklist 不是开发动作列表，而是验收协议。每个 item 都应该让 `master`
能够在不介入实现的前提下做出通过/驳回判断。

### 2.1 设计原则

每个 checklist item 至少包含以下字段：

| 字段                  | 说明                                  |
| --------------------- | ------------------------------------- |
| `id`                  | 稳定 ID，便于追踪和重试               |
| `title`               | 简短目标                              |
| `goal`                | 结果导向描述，说明最终要达到什么行为  |
| `write_allowlist`     | 允许修改的文件/目录边界               |
| `write_blocklist`     | 明确禁止修改的范围                    |
| `dependencies`        | 前置 item 或外部依赖                  |
| `owner`               | 当前负责的 agent 标识                 |
| `status`              | 当前状态                              |
| `acceptance_commands` | `master` 或验证用 `worker` 要跑的命令 |
| `done_definition`     | 验收通过的具体标准                    |
| `evidence`            | 结果链接、命令输出摘要、截图说明等    |
| `retry_count`         | 已重试次数                            |
| `failure_reason`      | 最近一次失败原因                      |
| `notes`               | 补充约束、风险备注                    |

设计时遵循以下规则：

- 用“达到什么结果”描述 item，不要只写“修改某文件”。
- 一个 item 只对应一个可清晰判定的完成条件。
- `write_allowlist` 必须具体到目录、模块或文件级别。
- `acceptance_commands` 只写真正决定是否通过的命令。
- `done_definition` 要能被第三方接手，不依赖口头上下文。

### 2.2 推荐状态

推荐使用下面这组状态：

- `todo`：已定义，尚未分配
- `assigned`：已分配给某个 agent
- `submitted`：worker 已提交结果，等待验收
- `accepted`：验收通过
- `redo`：验收失败，等待新 agent 接手
- `blocked`：被外部依赖、缺信息或环境问题阻塞
- `cancelled`：需求取消或合并到其他 item

### 2.3 状态流转

推荐流转如下：

```text
todo -> assigned -> submitted -> accepted
                     |
                     v
                    redo -> assigned -> submitted

todo/assigned/submitted -> blocked
blocked -> todo/assigned
todo/assigned/redo -> cancelled
```

关键约束：

- `master` 只在 `submitted` 后做验收，不在 `assigned` 阶段代替 worker 补实现。
- 验收失败时不要把 item 直接退回 `assigned`，先标记为
  `redo`，这样失败事实不会丢失。
- `blocked` 必须写清阻塞条件和解除条件。

## 3. 并发与写入边界规则

并发不是越多越好。稳定的 multi-agent 协作依赖清晰的写入边界，而不是“多开几个 agent 试试看”。

### 3.1 写入边界规则

推荐遵循以下硬规则：

- 同一时刻，一个文件只能有一个写入 owner。
- 同一时刻，一个高耦合目录尽量只让一个 worker 写入。
- 可以共享读取上下文，但不能共享写入责任。
- 文档、测试、核心逻辑可以拆分并发，但前提是边界不重叠。
- 如果同一 item 需要跨多个高耦合区域，优先串行分阶段，而不是并发硬拆。

### 3.2 推荐的并发上限

经验上，常规仓库里同时活跃的 `worker` 以 2 到 3 个为宜：

- 1 个负责核心实现
- 1 个负责配套测试或文档
- 1 个负责额外的独立区域

超过这个数量后，`master` 的验收、协调、冲突处理成本通常会明显上升。

### 3.3 边界划分方法

推荐按下面顺序划分边界：

1. 先按“验收结果”拆 item。
2. 再按“写入区域”切分 worker。
3. 最后才考虑是否并发。

优先级示例：

- 好拆法：`scripts/commands/`、`tests/`、`README/文档` 分开
- 坏拆法：多个 worker 同时改同一个入口文件、同一套共享测试夹具、同一个公共配置

### 3.4 `master` 的并发调度原则

`master` 在启动并发 worker 前，应先判断：

- 它们的 `write_allowlist` 是否重叠
- 它们的 `acceptance_commands` 是否会互相污染结果
- 是否存在显式依赖关系
- 是否会争用同一环境或同一临时资源

只要其中一项答案不清楚，就先串行再说。

## 4. 失败回收、交接与替换 agent 规则

验收失败本身不是问题；失败后没有标准化回收和替换，才是问题。

### 4.1 失败后的标准动作

当 `master` 验收不通过时，应按下面顺序执行：

1. 将 item 状态改为 `redo`
2. 记录 `failure_reason`
3. 记录失败发生时的验收命令和关键结果摘要
4. 要求当前 worker 提交结构化交接摘要
5. 关闭当前 worker
6. 启动新的 worker 接手

注意：`master` 不应在第 4 步和第 6 步之间插入自己的实现修改。

### 4.2 强制交接摘要

关闭失败 worker 之前，至少要收集下面这份交接摘要：

```text
changed_files:
commands_run:
what_passed:
what_failed:
suspected_root_cause:
next_agent_starting_point:
```

这份交接摘要的目的不是保留长日志，而是让下一个 agent 避免从零开始。

### 4.3 替换规则

推荐采用以下替换规则：

- 同一个 item 首次失败，可以直接换新 worker。
- 如果怀疑拆分错误而不是实现错误，先开 `explorer` 复核，再拆新 worker。
- 同一个 item 连续两次失败，`master`
  应优先检查 checklist 是否写错、边界是否冲突、验收标准是否不完整。
- 如果失败原因来自环境、外部依赖或缺失信息，转为 `blocked`，不要无意义重试。

### 4.4 关闭 agent 的时机

为了保持 master session 整洁，agent 应尽早关闭：

- `worker` 提交并被 `accepted` 后关闭
- `worker` 被驳回并完成交接后关闭
- `explorer` 输出拆分建议后关闭
- 验证用 `worker` 提交验证证据后关闭

不要保留长期闲置的 agent；它们只会增加上下文噪音和责任不清。

## 5. 推荐的阶段化执行流程

下面是一套可落地的阶段化流程，适合大多数需要拆分执行的任务。

### Phase 0: Intake

目标：明确任务目标和不可违反的硬约束。

`master` 输出：

- 目标说明
- 不可修改范围
- 可接受的交付形式
- 是否允许启用 `explorer` / 验证用 `worker`

### Phase 1: Exploration

当需求复杂、边界不明或风险较高时，先启用 `explorer`。

`explorer` 输出：

- 影响面分析
- 风险点
- 推荐拆分
- 推荐的 `write_allowlist`
- 推荐的 `acceptance_commands`

如果任务很清楚，这一阶段可以跳过。

### Phase 2: Checklist Normalization

`master` 把需求整理成正式 checklist：

- 每个 item 都有 `id`
- 每个 item 都有 `done_definition`
- 每个 item 都有 `write_allowlist`
- 每个 item 都有 `acceptance_commands`
- 每个 item 都有初始状态

只有 checklist 足够清晰时，才进入下一阶段。

### Phase 3: Dispatch

`master` 为每个 item 指派 `worker`，并明确：

- 只允许改哪些文件
- 不允许动哪些文件
- 需要先跑哪些最小验证
- 完成后必须按什么格式回报

如果多个 item 写入边界不重叠，可以并发指派。实现 `worker` 默认显式带
`$karpathy-guidelines`；`explorer` / 验证用 `worker` 按风险决定是否显式带。

### Phase 4: Submission

`worker` 完成改动后提交结构化结果，item 状态从 `assigned` 变为 `submitted`。

此时 `master` 只接收结果，不直接修代码。

### Phase 5: Acceptance

`master` 或验证用 `worker` 执行验收：

- 查看改动摘要
- 检查是否越界改动
- 运行 `acceptance_commands`
- 对照 `done_definition` 做通过/驳回判断

如果通过，状态改为 `accepted`；如果不通过，进入 `redo` 或 `blocked`。

### Phase 6: Recovery and Closure

对未通过的 item：

- 记录失败原因
- 收交接摘要
- 关闭当前 worker
- 重新指派新 worker 或 explorer

当所有 item 进入 `accepted`、`cancelled` 或有明确说明的 `blocked`
后，这一轮编排结束。

## 6. 可直接复用的模板

下面的模板故意保留了少量英文状态和字段名，方便直接复制到 checklist、issue、prompt 或脚本配置中。模板默认内建 4 条执行护栏；实现
`worker` 默认显式带 `$karpathy-guidelines`，`explorer` / 验证用 `worker`
按风险显式带。

### 6.1 `master checklist` 模板

```md
# Checklist

## Meta

- objective:
- owner: master
- updated_at:
- acceptance_owner: master
- notes:

## Items

### ITEM-001

- title:
- goal:
- status: todo
- owner:
- dependencies:
- write_allowlist:
  - path/
- write_blocklist:
  - path/
- acceptance_commands:
  - command 1
  - command 2
- done_definition:
  - condition 1
  - condition 2
- evidence:
- retry_count: 0
- failure_reason:
- notes:

### ITEM-002

- title:
- goal:
- status: todo
- owner:
- dependencies:
- write_allowlist:
  - path/
- write_blocklist:
  - path/
- acceptance_commands:
  - command
- done_definition:
  - condition
- evidence:
- retry_count: 0
- failure_reason:
- notes:
```

推荐补充规则：

- `status` 只能使用预定义枚举值
- `retry_count` 由 `master` 更新，worker 不改
- `evidence` 只记录摘要和定位信息，不贴整段长日志

### 6.2 `worker` 指派提示词模板

```text
请按 `$karpathy-guidelines` 执行这个 item。

你负责处理 checklist item: <ITEM-ID>

角色要求：
- 你只负责实现和与实现强相关的最小验证
- 不要修改 checklist
- 不要修改 write_allowlist 之外的文件
- 不要接管其他 item

执行护栏：
- 先写出会影响实现的假设、歧义或阻塞，不要静默猜测
- 优先选择最简单够用的方案，不做额外抽象、清理或顺手重构
- 改动只限于当前 item 直接需要的文件和行
- 先给出简短计划，再执行要求的最小验证

任务目标：
<goal>

完成定义：
<done_definition>

允许修改范围（write_allowlist）：
- <path-or-file>
- <path-or-file>

禁止修改范围（write_blocklist）：
- <path-or-file>
- <path-or-file>

前置依赖：
- <dependency or none>

提交前最小验证：
- <command>
- <command>

最终回报必须使用以下结构：
changed_files:
commands_run:
result:
remaining_risks:
ready_for_acceptance:

额外要求：
- 如果某个关键歧义会改变实现，不要自行脑补；直接报告给 `master`
- 如果发现 checklist 本身有问题，不要自行改规则；直接在结果里指出
- 如果无法完成，请明确说明阻塞点和建议下一位 agent 的切入点
```

使用建议：

- 一个 prompt 只绑定一个 item，或者绑定一组写入边界完全不重叠的 item。
- `master` 每次派发前都应重写 `<goal>`、`<done_definition>`、`write_allowlist`
  和验证命令，避免 worker 沿用过期上下文。

### 6.3 `explorer` 指派提示词模板

默认做法：先用内建执行护栏；只有在分析任务歧义大、风险高或容易越角色边界时，才在 prompt 顶部补一句：请按
`$karpathy-guidelines` 执行这个 item。

```text
你负责处理 checklist item: <ITEM-ID> 的 exploration。

角色要求：
- 你只负责影响面分析、依赖梳理、拆分建议和验收建议
- 不要实现功能，也不要接管交付工作
- 不要修改 checklist
- 除非 prompt 明确授权，否则不要修改文件

执行护栏：
- 先写出会影响分析结论的假设、未知项或阻塞
- 优先给出最简单可执行的建议，必要时直接建议缩小范围
- 严格遵守分配给你的读取/写入边界
- 用具体文件、命令或依赖证据支撑结论，证据不足就直接说明

分析目标：
<goal>

需要回答的问题：
- <question>
- <question>

重点阅读范围：
- <path-or-file>
- <path-or-file>

允许修改范围（默认无）：
- none by default

最终回报必须使用以下结构：
assumptions:
commands_run:
findings:
recommended_next_steps:
remaining_risks:
ready_for_dispatch:

额外要求：
- 如果证据不足以支持结论，直接说明缺了什么，不要脑补
- 如果最佳建议是减少复杂度或回退拆分，也要直接说
```

### 6.4 验证用 `worker` 指派提示词模板

默认做法：用 `worker`
agent_type 启动一个验证专用 subagent，并先用内建执行护栏；只有在验证任务歧义大、风险高或容易演变成诊断/修复时，才在 prompt 顶部补一句：请按
`$karpathy-guidelines` 执行这个 item。

```text
你负责处理 checklist item: <ITEM-ID> 的 validation。
你是验证用 worker，不是独立的 `validator` agent_type。

角色要求：
- 你只负责独立验证和整理证据
- 不要修实现，不要顺手扩 scope
- 不要修改 checklist
- 除非 prompt 明确授权，否则不要修改文件

执行护栏：
- 先写出会影响验收判断的环境前提、限制或阻塞
- 只跑足够判断通过/失败的最小验证面，不做无关扩展
- 严格遵守分配给你的读取/写入边界
- 明确写出支持结论的命令和观察结果；证据不足就直接报 blocker

验证目标：
<goal>

验收命令：
- <command>
- <command>

完成定义：
<done_definition>

允许修改范围（默认无）：
- none by default

最终回报必须使用以下结构：
assumptions:
commands_run:
evidence:
failed_checks:
remaining_risks:
ready_for_acceptance:

额外要求：
- 如果验证失败，只描述失败点和证据，不要自己补修复
- 如果环境不足以得出可靠结论，明确说明阻塞和缺少的前提
```

### 6.5 `验收/驳回/重试` 流程模板

```md
# Acceptance Flow

## Input

- item_id:
- current_status: submitted
- assigned_worker:
- acceptance_commands:
  - command 1
  - command 2
- done_definition:
  - condition 1
  - condition 2

## Step 1: Review

- check changed_files against write_allowlist
- review worker summary
- confirm no forbidden file changes

## Step 2: Validate

- run acceptance_commands
- capture concise evidence

## Step 3A: Accept

条件：

- done_definition 全部满足
- 验收命令通过
- 无越界改动

动作：

- set status = accepted
- update evidence
- close current worker

## Step 3B: Reject

触发条件：

- 验收命令失败
- done_definition 未满足
- 存在越界改动
- 风险超出可接受范围

动作：

- set status = redo
- increment retry_count
- fill failure_reason
- collect handoff summary
- close current worker
- assign replacement worker

## Step 3C: Block

触发条件：

- 外部依赖缺失
- 环境问题导致无法验收
- checklist 信息不足，无法做有效判断

动作：

- set status = blocked
- record unblock_condition
- close or pause current worker
```

如果想进一步标准化，可在 `Reject` 时强制附加下面的回报片段：

```text
rejection_reason:
failed_command:
failed_condition:
required_next_action:
replacement_agent_type:
```

## 7. 最佳实践与反模式

### 7.1 最佳实践

- 把 checklist 写成验收协议，而不是想到什么记什么。
- 让 `master` 只维护调度信息和验收结果，避免实现细节淹没 session。
- 优先按写入边界拆 worker，再决定是否并发。
- 要求每个 worker 自跑最小验证，减少明显失败流入验收阶段。
- 验收失败后先收交接摘要，再关闭 agent，再派新 agent。
- 对高风险任务启用 `explorer` 或验证用
  `worker`，不要把所有风险都压给单个 worker。

### 7.2 常见反模式

- `master` 验收失败后自己顺手改一行。
- 多个 worker 同时改同一个入口文件或共享测试夹具。
- checklist 只有“做什么”，没有“如何算完成”。
- 失败后直接口头重试，不记录 `failure_reason` 和 `retry_count`。
- 一个 worker 长期存活，先后接多个无关 item，导致责任边界和上下文污染。
- 验证用 `worker` 一边验收一边偷偷补实现，最后角色失真。

## 8. 一句话落地原则

如果要把这套方案执行稳，记住一句话就够：

> `master`
> 负责拆分、派发、验收、更新 checklist；实现问题永远交给 worker 解决，失败就替换，不由
> `master` 亲自下场修。
