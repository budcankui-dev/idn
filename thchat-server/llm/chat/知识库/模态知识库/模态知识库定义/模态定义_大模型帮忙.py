import json
# 定义各个子结构变量
# 定义IP地址信息
ip_addresses = {
    "source_ip": "请帮我结合用户的业务特征提取对应的参数约束",  
    "destination_ip": "请帮我结合用户的业务特征提取对应的参数约束" 
}
application_scenario = "请帮我结合用户的业务特征提取对应的参数约束"
network_qos_constraints = {
    "bandwidth_requirement": "请帮我结合用户的业务特征提取对应的参数约束",
    "latency_requirement": "请帮我结合用户的业务特征提取对应的参数约束",
    "loss_requirement": "请帮我结合用户的业务特征提取对应的参数约束"
}
computational_constraints = {
    "cpu_power": "请帮我结合用户的业务特征提取对应的参数约束",
    "gpu_power": "请帮我结合用户的业务特征提取对应的参数约束"
}
storage_constraints = {
    "storage_capacity": "请帮我结合用户的业务特征提取对应的参数约束",
    "storage_performance": "请帮我结合用户的业务特征提取对应的参数约束"
}
modality = "请帮我结合用户的业务特征提取对应的参数约束"

# 使用定义的变量构建字典
modality_info = {
    "ip_addresses": ip_addresses,
    "modality": modality,
    "application_scenario": application_scenario,
    "network_qos_constraints": network_qos_constraints,
    "computational_constraints": computational_constraints,
    "storage_constraints": storage_constraints
}

# 打印构建的字典
print(modality_info)
# print(json.dumps(modality_info))