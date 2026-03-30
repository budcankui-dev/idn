import json,re
# 定义各个子结构变量
# -初始化阶段，定义IP地址信息
def GenJson():
    ip_addresses = {
        "source_ip": "",  
        "destination_ip": "" 
    }
    network_qos_constraints = {
        "bandwidth_requirement": "",
        "latency_requirement": "",
        "loss_requirement": ""
    }
    computational_constraints = {
        "cpu_power": "",
        "gpu_power": ""
    }
    storage_constraints = {
        "storage_capacity": "",
        "storage_performance": ""
    }
    modality_info = {
        "modality":"",
        "method":"1/2/3/4",
        "status":"loading/success"
    }
    # 使用定义的变量构建字典
    modality_info = {
        "modality_info": modality_info,
        "ip_info": ip_addresses,
        "network_qos_constraints": network_qos_constraints,
        "computational_constraints": computational_constraints,
        "storage_constraints": storage_constraints
    }
    
    return modality_info
# -模态信息解析阶段 UserNaturalLanguage为用户输入的自然语言意图
UserNaturalLanguage = input()
modality_info = GenJson()
def match_modality(keyword):
    # 定义模态名称和关键词的映射关系
    modality_map = {
        r"低时延转发模态": r"AR|VR|XR|元宇宙",
        r"分布式存算模态": r"视联网",
        r"高通量计算模态": r"高能物理科学实验"
    }
    # 定义模态名称与method的映射关系
    modality_value_map = {
        "低时延转发模态": 1,
        "分布式存算模态": 2,
        "高通量计算模态": 3
    }
    # 遍历模态名称和关键词的映射关系
    for modality, keywords in modality_map.items():
        # 检查关键词是否匹配
        if re.search(keywords, keyword, re.IGNORECASE):
            # 返回模态名称和对应的值
            return modality, modality_value_map[modality]
    return "未找到匹配的模态名称", None
modality_info["modality_info"]["modality"]=match_modality(UserNaturalLanguage)[0]
modality_info["modality_info"]["method"]=match_modality(UserNaturalLanguage)[1]
modality_info["modality_info"]["status"]="loading"

# -存转算解析阶段
UserNaturalLanguage = input()
