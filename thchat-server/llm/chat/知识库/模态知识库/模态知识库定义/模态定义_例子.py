# 定义各个子结构变量
# 定义IP地址信息
ip_addresses = {
    "source_ip": "192.168.1.1",  # 示例源IP地址
    "destination_ip": "192.168.1.2"  # 示例目的IP地址
}
application_scenario = "智慧生活场景，如AR/VR/XR业务"
network_qos_constraints = {
    "bandwidth_requirement": "至少 100 Mbps",
    "latency_requirement": "小于 20 毫秒",
    "loss_requirement": "null"
}
computational_constraints = {
    "cpu_power": "至少 8 核心，主频不低于 3.0 GHz",
    "gpu_power": "至少 1 TFLOPS"
}
storage_constraints = {
    "storage_capacity": "至少 1 TB",
    "storage_performance": "读写速度至少 500 MB/s"
}

# 使用定义的变量构建字典
modality_info = {
    "ip_addresses": ip_addresses,
    "modality": "低时延转发模态",
    "application_scenario": application_scenario,
    "network_qos_constraints": network_qos_constraints,
    "computational_constraints": computational_constraints,
    "storage_constraints": storage_constraints
}

# 打印构建的字典
print(modality_info)