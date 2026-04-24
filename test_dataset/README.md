# 测试数据集

用于意图解析系统的测试数据集生成和准确率评估。

## 目录结构

```
testdataset/
├── templates.py        # 模板定义和槽位值域
├── generate_dataset.py # 数据集生成脚本
├── test_accuracy.py    # 准确率测试脚本
├── README.md           # 本文件
```

## 生成数据集

### 基本用法

```bash
# 生成 800 训练 + 200 验证数据（需要后端运行在 localhost:6000）
python generate_dataset.py

# 指定输出目录
python generate_dataset.py --output-dir ./data

# 指定数量
python generate_dataset.py --train 1000 --val 200

# 只生成文本，不调用 API（可用于离线分析）
python generate_dataset.py --no-api
```

### 输出格式

生成的 `train.jsonl` 和 `val.jsonl` 每行一条 JSON：

```json
{
    "text": "我想在h1部署视频AI推理业务，使用yolov8模型，延迟2秒，帧率30，分辨率1080p，从2026-04-21 10:00开始运行1小时",
    "business_type": "视频AI推理",
    "slots": {
        "model": "yolov8",
        "src_terminal": "h1",
        "latency": "2",
        "framerate": "30",
        "resolution": "1080p",
        "start_time": "2026-04-21 10:00",
        "duration": "1小时"
    },
    "api_result": {
        "input": "...",
        "parsed_result": {...}
    }
}
```

## 准确率测试

### 基本用法

```bash
# 测试验证集
python test_accuracy.py -f val.jsonl

# 限制测试数量
python test_accuracy.py -f val.jsonl --limit 50
```

### 输出报告

测试脚本会输出：
1. **业务类型识别准确率** - 是否正确识别视频AI推理/模型训练
2. **参数提取准确率** - 所有关键参数是否完整提取
3. **解析成功率** - parse_success 是否为 true

详细结果会保存到 `val_result.jsonl`。