# 意图解析后端模块文档

## 概述

意图解析模块负责解析用户的业务意图，提取关键参数，并生成任务DAG。本模块是前后端对接的核心，后端每次代码改动后需运行测试确保正确性。

## 目录结构

```
server/
├── parser/
│   ├── state.py          # State 数据模型
│   ├── state_parser.py   # 意图解析核心逻辑
│   └── dag_template.py   # DAG模板定义（类实现）
├── prompt/
│   ├── prompt_template.py      # 业务参数提示词模板
│   ├── workflow_parse_intent.py # 意图解析工作流提示词
│   └── workflow_dag.py          # DAG生成提示词
└── test_parser.py        # 测试套件
```

## 业务类型

| 业务类型 | 说明 | 预设模态 |
|---------|------|----------|
| 视频AI推理 | 视频AI推理业务 | LOW_LATENCY (低延时转发模态) |
| 模型训练 | AI模型训练业务 | INTELLIGENT_CENTER (智算中心模态) |

## 视频AI推理参数

| 参数名 | 说明 | 约束 |
|--------|------|------|
| 模型名称 | yolov8 | 可选值固定 |
| 延迟 | 延迟秒数 | 必须 >0 |
| 视频帧率 | 帧率 | 必须 >0 |
| 分辨率 | 视频分辨率 | 可选: 1920x1080, 1280x720, 3840x2160 |
| 开始时间 | 开始时间 | YYYY-MM-DD HH:MM 格式，不早于当前时间 |
| 期望运行时间 | 运行时长 | 最少5分钟 |

## 模型训练参数

| 参数名 | 说明 | 约束 |
|--------|------|------|
| 模型名称 | resnet/mobilenet/vgg | 可选值固定 |
| 数据集 | CIFAR-100 | 可选值固定 |
| 训练轮次 | 训练轮数 | 必须 >0 整数 |
| 开始时间 | 开始时间 | YYYY-MM-DD HH:MM 格式，不早于当前时间 |
| 期望运行时间 | 运行时长 | 最少30分钟 |
| 训练完成时间 | 完成时间 | 必须与期望运行时间相同 |

## DAG模板类

### DAGNode

```python
@dataclass
class DAGNode:
    node_id: str           # 节点ID
    cpu_units: int        # CPU核数
    mem_mb: int           # 内存MB
    disk_mb: int         # 磁盘MB
    est_runtime_ms: int   # 预估运行时长（毫秒）
```

### DAGEdge

```python
@dataclass
class DAGEdge:
    from_node: str       # 起始节点
    to_node: str         # 目标节点
    data_mb: int         # 数据传输MB
```

### VideoInferenceDAG / ModelTrainingDAG

```python
# 创建DAG实例
dag = VideoInferenceDAG(session_id="session_123")
dag.set_submit_ts_ms(1777082400000)  # 设置提交时间戳
dag.set_runtime(600000)  # 设置运行时长（毫秒）
dag_dict = dag.to_dict()  # 转换为字典
```

**注意**：所有DAG节点的 `gpu_units` 固定为 0（不使用GPU）。

## 运行测试

```bash
cd server
python test_parser.py
```

## 测试覆盖

| 测试类 | 说明 |
|--------|------|
| TestTimeParsing | 时间解析测试 |
| TestDAGTemplate | DAG模板类测试 |
| TestIntentParsing | 意图解析测试 |
| TestDAGFill | DAG填充测试 |
| TestBackwardCompatibility | 向后兼容测试 |

## 常见问题

### 1. dateparser 相对时间解析失败

如果 `test_parse_start_time_relative` 被跳过，说明 dateparser 库不支持该相对时间格式。可选方案：
- 使用确切日期时间格式
- 扩展 dateparser 支持的语言

### 2. 测试时间过期

所有测试使用动态未来时间 `(datetime.now() + timedelta(days=7))`，避免时间过期问题。

### 3. DAG中gpu_units为0

所有节点固定不使用GPU，若需要GPU支持请修改 `DAGNode` 类。
