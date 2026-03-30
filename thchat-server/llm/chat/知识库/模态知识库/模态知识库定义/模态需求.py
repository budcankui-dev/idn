def get_storage_requirements(mode, level):
    # 定义中间等级的基础存储需求
    modes = {
        "低时延转发模态": {"capacity": "1TB", "performance": "500MB/s"},
        "分布式存算模态": {"capacity": "10TB", "performance": "500MB/s"},
        "高通量计算模态": {"capacity": "100PB", "performance": "1GB/s"}
    }

    if mode not in modes:
        raise ValueError("模式必须为：低时延转发模态、分布式存算模态 或 高通量计算模态")
    if level not in ["低", "中", "高"]:
        raise ValueError("需求等级必须为：低、中 或 高")

    base = modes[mode]
    result = {}

    scale = 1
    if level == "低":
        scale = 0.5
    elif level == "高":
        scale = 5

    # capacity
    cap_value = float(base["capacity"].rstrip("TBP"))
    result["capacity"] = f"{cap_value * scale}{'TB' if mode != '高通量计算模态' else 'PB'}"

    # performance
    perf_unit = "MB/s" if mode != "高通量计算模态" else "GB/s"
    perf_value = float(base["performance"].rstrip(perf_unit))
    result["performance"] = f"{perf_value * scale}{perf_unit}"

    return result

def get_compute_requirements(mode, level):
    # 定义中间等级的基础算力需求
    modes = {
        "低时延转发模态": {"CPU": "8 cores 3GHz", "GPU": "1 TFLOPS"},
        "分布式存算模态": {"CPU": "16 cores 2GHz", "GPU": "2 TFLOPS"},
        "高通量计算模态": {"CPU": "64 cores 2.5GHz", "GPU": "10 TFLOPS"}
    }

    if mode not in modes:
        raise ValueError("模式必须为：低时延转发模态、分布式存算模态 或 高通量计算模态")
    if level not in ["低", "中", "高"]:
        raise ValueError("需求等级必须为：低、中 或 高")

    base = modes[mode]
    result = {}

    scale = 1
    if level == "低":
        scale = 0.5
    elif level == "高":
        scale = 5

    # CPU
    cpu_parts = base["CPU"].split()
    cpu_cores = int(cpu_parts[0])
    cpu_freq = float(cpu_parts[2].rstrip("GHz"))
    result["CPU"] = f"{int(cpu_cores * scale)} cores {cpu_freq * scale}GHz"

    # GPU
    gpu_value = float(base["GPU"].rstrip(" TFLOPS"))
    result["GPU"] = f"{gpu_value * scale} TFLOPS"

    return result

def get_qos_network_requirements(mode, level):
    # 定义中间等级的基础 QoS 网络需求
    modes = {
        "低时延转发模态": {"bandwidth": "100Mbps", "latency": "20ms", "loss": "0.10%"},
        "分布式存算模态": {"bandwidth": "500Mbps", "latency": "10ms", "loss": "0.10%"},
        "高通量计算模态": {"bandwidth": "10Gbps", "latency": "100ms", "loss": "1%"}
    }

    if mode not in modes:
        raise ValueError("模式必须为：低时延转发模态、分布式存算模态 或 高通量计算模态")
    if level not in ["低", "中", "高"]:
        raise ValueError("需求等级必须为：低、中 或 高")

    base = modes[mode]
    result = {}

    scale = 1
    if level == "低":
        scale = 0.5
    elif level == "高":
        scale = 5

    # bandwidth
    bw_unit = "Mbps" if mode != "高通量计算模态" else "Gbps"
    bw_value = float(base["bandwidth"].rstrip(bw_unit))
    result["bandwidth"] = f"{bw_value * scale}{bw_unit}"

    # latency
    latency_value = float(base["latency"].rstrip("ms"))
    result["latency"] = f"{latency_value * scale}ms"

    # loss
    loss_value = float(base["loss"].rstrip("%"))
    result["loss"] = f"{loss_value * scale}%"

    return result

# 示例调用
if __name__ == "__main__":
    print(get_storage_requirements("低时延转发模态", "高")['capacity'])
    print(get_storage_requirements("低时延转发模态", "高")['performance'])

    print(get_compute_requirements("低时延转发模态", "高")['CPU'])
    print(get_compute_requirements("低时延转发模态", "高")['GPU'])

    print(get_qos_network_requirements("低时延转发模态", "高")['bandwidth'])
    print(get_qos_network_requirements("低时延转发模态", "高")['latency'])
    print(get_qos_network_requirements("低时延转发模态", "高")['loss'])