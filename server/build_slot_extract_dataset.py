# 批量调用 /chat/slot_extract 接口，生成数据集
# 用法：python build_slot_extract_dataset.py --input input.txt --output dataset.jsonl --url http://localhost:6000/chat/slot_extract

import argparse
import requests
import json
import time
from tqdm import tqdm

def build_dataset(input_file, output_file, url):
    with open(input_file, 'r', encoding='utf-8') as fin, open(output_file, 'w', encoding='utf-8') as fout:
        for line in tqdm(fin, desc='Processing'):
            prompt = line.strip()
            if not prompt:
                continue
            data = {
                "prompt": prompt,
                "history": [],
                "files": [],
                "state": {"type": "state", "stage": "intent_parsing", "workflow": "intent_parsing", "parse_success": False, "session_id": ""}
            }
            try:
                resp = requests.post(url, json=data, timeout=30)
                resp.raise_for_status()
                result = resp.json()
                # print(result)
            except Exception as e:
                print(f"Error for prompt: {prompt}\n{e}")
                result = {"error": str(e)}
            label={}
            label["intent_result"] = result["state"].get("intent_result", {})  # 确保有这个字段
            label["missing_params"] = result["state"].get("missing_params", [])
            label["reason_params"] = result["state"].get("reason_params", [])   

            record = {"messages": prompt, "label": label}
            fout.write(json.dumps(record, ensure_ascii=False) + '\n')
            time.sleep(0.5)  # 防止接口压力过大

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='批量调用slot_extract接口生成数据集')
    parser.add_argument('--input', default="/Users/yanjia/codes/IDN/意图解析/server/data.jsonl", help='输入文本文件，每行一个prompt')
    parser.add_argument('--output', default="dataset.jsonl", help='输出数据集文件（jsonl）')
    parser.add_argument('--url', default='http://localhost:6000/chat/slot_extract', help='接口URL')
    args = parser.parse_args()
    build_dataset(args.input, args.output, args.url)

