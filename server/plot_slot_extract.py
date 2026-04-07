# 画图展示准确率分布
# 用法：python plot_slot_extract.py --dataset dataset.jsonl
import argparse
import json
import matplotlib.pyplot as plt
from eval_slot_extract import extract_label

def get_acc_list(dataset_file):
    acc_list = []
    with open(dataset_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            record = json.loads(line)
            label = extract_label(record)
            acc_list.append(1.0 if label is not None else 0.0)
    return acc_list

def plot_acc(acc_list):
    plt.figure(figsize=(6,4))
    plt.hist(acc_list, bins=[-0.5,0.5,1.5], rwidth=0.8)
    plt.xticks([0,1], ['错误','正确'])
    plt.xlabel('样本准确性')
    plt.ylabel('样本数')
    plt.title('slot_extract参数解析准确率分布')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='画图展示slot_extract准确率分布')
    parser.add_argument('--dataset', required=True, help='数据集文件（jsonl）')
    args = parser.parse_args()
    acc_list = get_acc_list(args.dataset)
    plot_acc(acc_list)
