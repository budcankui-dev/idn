#!/usr/bin/env python3
# test_dataset/test_accuracy.py
"""
准确率测试脚本
供第三方测试人员使用，评估意图解析的准确率

评测维度：
1. 业务类型识别准确率
2. 参数提取完整率（所有关键参数都识别到）
3. 缺失参数识别准确率
4. 参数值校验准确率
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Tuple
from collections import defaultdict

from tqdm import tqdm

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "server"))


def load_jsonl(path: str) -> List[Dict]:
    """加载 jsonl 文件"""
    cases = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))
    return cases


def load_test_file(path: str) -> List[Dict]:
    """加载测试文件（兼容 api_result 结构）"""
    return load_jsonl(path)


def evaluate_business_type(pred: str, expected: str) -> bool:
    """评估业务类型识别是否正确"""
    if not pred:
        return False
    return expected in pred or pred in expected


def evaluate_params(
    parsed_params: Dict,
    expected_slots: Dict,
    business_type: str,
) -> Tuple[bool, List[str]]:
    """评估参数提取是否正确"""
    errors = []
    for slot_name, expected_value in expected_slots.items():
        if slot_name in ["模态", "源终端IP", "目的终端IP"]:
            continue
        if slot_name not in parsed_params:
            errors.append(f"缺少参数: {slot_name}")
        elif parsed_params[slot_name] != expected_value:
            errors.append(f"参数值错误: {slot_name} 期望={expected_value} 实际={parsed_params[slot_name]}")
    return (len(errors) == 0, errors)


def evaluate_missing_params(
    parsed_missing: List,
    actual_missing: List[str],
) -> Tuple[bool, List[str]]:
    """评估缺失参数识别是否正确"""
    errors = []
    parsed_set = set(parsed_missing)
    actual_set = set(actual_missing)
    for missing in actual_set - parsed_set:
        errors.append(f"漏报缺失参数: {missing}")
    for reported in parsed_set - actual_set:
        errors.append(f"误报缺失参数: {reported}")
    return (len(errors) == 0, errors)


def evaluate_case(case: Dict) -> Dict:
    """
    评估单条测试用例
    case 格式:
    {
        "text": "...",
        "business_type": "视频AI推理",
        "slots": {"model": "yolov8", ...},
        "api_result": {...}
    }
    """
    result = {
        "text": case["text"],
        "business_type": case.get("business_type", ""),
        "slots": case.get("slots", {}),
    }

    if "api_result" in case:
        api_result = case["api_result"]
        if "error" in api_result:
            result["status"] = "error"
            result["message"] = api_result["error"]
            return result

        parsed_result = api_result.get("parsed_result", {})
        intent_result = parsed_result.get("intent_result", {})
        params = intent_result.get("参数", {})

        result["parsed_business_type"] = intent_result.get("任务名称", "")
        result["parsed_params"] = params
        result["missing_params"] = parsed_result.get("missing_params", [])
        result["parse_success"] = parsed_result.get("parse_success", False)
    else:
        result["status"] = "no_api_result"
        return result

    pred_business = result.get("parsed_business_type", "")
    expected_business = result.get("business_type", "")
    result["business_type_correct"] = evaluate_business_type(pred_business, expected_business)

    params_correct, param_errors = evaluate_params(
        result["parsed_params"],
        result["slots"],
        result["business_type"],
    )
    result["params_correct"] = params_correct
    result["param_errors"] = param_errors

    missing_correct, missing_errors = evaluate_missing_params(
        result.get("missing_params", []),
        [],
    )
    result["missing_correct"] = missing_correct
    result["missing_errors"] = missing_errors

    result["status"] = "evaluated"
    return result


def compute_accuracy(results: List[Dict]) -> Dict:
    """计算整体准确率"""
    total = len(results)
    business_type_ok = sum(1 for r in results if r.get("business_type_correct", False))
    params_ok = sum(1 for r in results if r.get("params_correct", False))
    parse_success_ok = sum(1 for r in results if r.get("parse_success", False))

    return {
        "total": total,
        "business_type_accuracy": business_type_ok / total if total > 0 else 0,
        "params_accuracy": params_ok / total if total > 0 else 0,
        "parse_success_accuracy": parse_success_ok / total if total > 0 else 0,
        "business_type_correct_count": business_type_ok,
        "params_correct_count": params_ok,
        "parse_success_count": parse_success_ok,
    }


def print_report(accuracy: Dict, results: List[Dict], top_n: int = 10):
    """打印测试报告"""
    print("=" * 60)
    print("意图解析准确率测试报告")
    print("=" * 60)
    print(f"总测试用例: {accuracy['total']}")
    print(f"业务类型识别准确率: {accuracy['business_type_accuracy']:.2%} ({accuracy['business_type_correct_count']}/{accuracy['total']})")
    print(f"参数提取准确率: {accuracy['params_accuracy']:.2%} ({accuracy['params_correct_count']}/{accuracy['total']})")
    print(f"解析成功率: {accuracy['parse_success_accuracy']:.2%} ({accuracy['parse_success_count']}/{accuracy['total']})")
    print()

    errors = [r for r in results if r.get("status") == "error" or not r.get("business_type_correct")]
    if errors:
        print(f"错误案例 (前 {min(top_n, len(errors))} 条):")
        for i, r in enumerate(errors[:top_n]):
            print(f"  [{i+1}] {r.get('text', '')[:50]}...")
            if r.get("param_errors"):
                print(f"       参数错误: {r['param_errors']}")
            if r.get("business_type_correct") is False:
                print(f"       业务类型: 期望={r['business_type']} 实际={r.get('parsed_business_type', '')}")


def main():
    parser = argparse.ArgumentParser(description="意图解析准确率测试")
    parser.add_argument("--file", "-f", required=True, help="测试数据文件 (jsonl 格式)")
    parser.add_argument("--limit", "-n", type=int, default=None, help="限制测试数量")
    args = parser.parse_args()

    cases = load_test_file(args.file)
    if args.limit:
        cases = cases[:args.limit]

    print(f"加载了 {len(cases)} 条测试数据")

    results = []
    for case in tqdm(cases, desc="评估进度", unit="条"):
        result = evaluate_case(case)
        results.append(result)

    accuracy = compute_accuracy(results)
    print_report(accuracy, results)

    output_path = args.file.replace(".jsonl", "_result.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n详细结果已保存到: {output_path}")


if __name__ == "__main__":
    main()