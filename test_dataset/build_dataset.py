# 批量调用接口打标签，生成数据集
# 用法：python build_dataset.py --input examples.jsonl --output dataset.jsonl --url http://localhost:6000/chat/slot_extract

import argparse
import requests
import json
import time

def build_dataset(input_file, output_file, url):
    """读取输入文件，调用接口打标签，输出到jsonl"""
    with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            prompt = record.get("input", "")

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
            except Exception as e:
                print(f"Error for prompt: {prompt}\n{e}")
                result = {"error": str(e)}

            label = {
                "intent_result": result.get("state", {}).get("intent_result", {}),
                "missing_params": result.get("state", {}).get("missing_params", []),
                "reason_params": result.get("state", {}).get("reason_params", []),
                "parse_success": result.get("state", {}).get("parse_success", False),
                "stage": result.get("state", {}).get("stage", "")
            }

            output_record = {
                "input": prompt,
                "expected_output": record.get("expected_output", {}),
                "actual_output": label,
                "correct": label.get("intent_result", {}).get("业务类型") == record.get("expected_output", {}).get("business_type")
            }

            fout.write(json.dumps(output_record, ensure_ascii=False) + '\n')
            time.sleep(0.5)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='批量调用接口打标签生成数据集')
    parser.add_argument('--input', default='examples.jsonl', help='输入文本文件（jsonl格式）')
    parser.add_argument('--output', default='dataset.jsonl', help='输出数据集文件（jsonl）')
    parser.add_argument('--url', default='http://localhost:6000/chat/slot_extract', help='接口URL')
    args = parser.parse_args()
    build_dataset(args.input, args.output, args.url)