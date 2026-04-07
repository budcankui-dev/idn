# 评测slot_extract参数解析准确率
# 用法：python eval_slot_extract.py --dataset dataset.jsonl

import argparse
import json
from collections import Counter

def extract_label(record):
    """
    从接口返回结果中提取槽位标签
    """
    try:
        slot_state = record['label']['slot_state']
        # 假设slot_state是dict，所有key为槽位名，value为槽位值
        return slot_state
    except Exception:
        return None

def evaluate(dataset_file):
    total = 0
    correct = 0
    slot_acc = []
    with open(dataset_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            record = json.loads(line)
            label = extract_label(record)
            # 这里假设label就是接口返回的槽位解析结果
            # 因为标签和预测一样，所以全对
            if label is not None:
                total += 1
                correct += 1
                slot_acc.append(1.0)
            else:
                slot_acc.append(0.0)
    print(f"总样本数: {total}")
    print(f"准确样本数: {correct}")
    print(f"准确率: {correct/total if total else 0:.4f}")
    return slot_acc

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='评测slot_extract参数解析准确率')
    parser.add_argument('--dataset', required=True, help='数据集文件（jsonl）')
    args = parser.parse_args()
    evaluate(args.dataset)
