# 测试意图解析接口
# 用法：python test_api.py --input examples.jsonl --url http://localhost:6000/chat/slot_extract

import argparse
import requests
import json
import time

def test_api(input_file, url):
    """读取示例数据，调用接口并打印结果"""
    with open(input_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            prompt = record.get("input", "")
            expected = record.get("expected_output", {})

            print(f"\n{'='*60}")
            print(f"输入: {prompt}")
            print(f"期望输出: {json.dumps(expected, ensure_ascii=False, indent=2)}")

            data = {
                "prompt": prompt,
                "history": [],
                "files": [],
                "state": {
                    "type": "state",
                    "stage": "intent_parsing",
                    "workflow": "intent_parsing",
                    "parse_success": False,
                    "session_id": ""
                }
            }

            try:
                resp = requests.post(url, json=data, timeout=30)
                resp.raise_for_status()
                result = resp.json()

                actual = {
                    "intent_result": result["state"].get("intent_result", {}),
                    "missing_params": result["state"].get("missing_params", []),
                    "reason_params": result["state"].get("reason_params", []),
                    "parse_success": result["state"].get("parse_success", False),
                    "stage": result["state"].get("stage", "")
                }

                print(f"实际输出: {json.dumps(actual, ensure_ascii=False, indent=2)}")

                # 简单对比
                if expected.get("business_type") == actual.get("intent_result", {}).get("业务类型"):
                    print("✓ 业务类型匹配")
                else:
                    print("✗ 业务类型不匹配")

            except Exception as e:
                print(f"Error: {e}")

            time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='测试意图解析接口')
    parser.add_argument('--input', default='examples.jsonl', help='输入示例文件')
    parser.add_argument('--url', default='http://localhost:6000/chat/slot_extract', help='接口URL')
    args = parser.parse_args()
    test_api(args.input, args.url)