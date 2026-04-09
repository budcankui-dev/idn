# 评测slot_extract参数解析准确率（对比接口返回和标签）
# 用法：python eval_slot_extract_with_api.py --dataset data.jsonl --url http://localhost:6000/chat/slot_extract

import argparse
import requests
import json
from tqdm import tqdm

def extract_label(record):
    """
    从数据集标签中提取槽位信息
    """
    try:
        label = record.get('label', {})
        return label
    except Exception:
        return None

def extract_prompt(record):
    # 支持两种格式
    if 'prompt' in record:
        return record['prompt'], record.get('history', [])
    elif 'messages' in record:
        return record['messages'], record.get('history', [])
    else:
        return '', []

def call_api(prompt, history, url):
    data = {
        "prompt": prompt,
        "history": history,
        "files": [],
        "state": {"type": "state", "stage": "intent_parsing", "workflow": "intent_parsing", "parse_success": False, "session_id": ""}
    }
    try:
        resp = requests.post(url, json=data, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        state = result.get("slot_state") or result.get("state") or {}
        pred = {
            "intent_result": state.get("intent_result", {}),
            "missing_params": state.get("missing_params", []),
            "reason_params": state.get("reason_params", [])
        }
        return pred
    except Exception as e:
        print(f"Error for prompt: {prompt}\n{e}")
        return None

def compare_label(pred, label):
    # 只要intent_result、missing_params、reason_params都相等就算对
    return pred == label

def evaluate(dataset_file, url):
    total = 0
    correct = 0
    with open(dataset_file, 'r', encoding='utf-8') as fin:
        for line in tqdm(fin, desc='Evaluating'):
            record = json.loads(line)
            label = extract_label(record)
            prompt, history = extract_prompt(record)
            pred = call_api(prompt, history, url)
            if pred is not None:
                total += 1
                if compare_label(pred, label):
                    correct += 1
    print(f"总样本数: {total}")
    print(f"准确样本数: {correct}")
    print(f"准确率: {correct/total if total else 0:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='评测slot_extract参数解析准确率（对比接口返回和标签）')
    parser.add_argument('--dataset', default='/Users/yanjia/codes/IDN/意图解析/server/dataset.jsonl'   , help='数据集文件（jsonl）')
    parser.add_argument('--url', default='http://localhost:6000/chat/slot_extract', help='接口URL')
    args = parser.parse_args()
    evaluate(args.dataset, args.url)
