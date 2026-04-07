
VIDEO_DAG_TEMPLATE = {
    "job_id": "job-video-resource-guarantee-uuid",
    "submit_ts_ms": None,
    "policy_type": "RESOURCE_GUARANTEE",
    "job_name": "视频AI推理",
    "constraints": {"deadline_ms": None, "budget": None},
    "nodes": [
        {"node_id": "video", "resources": {"cpu_units": 20, "gpu_units": 0, "mem_mb": 1024,"disk_mb":1024}, "exec": {"est_runtime_ms": None}},
        {"node_id": "infer", "resources": {"cpu_units": 10, "gpu_units": 1, "mem_mb": 1024,"disk_mb":1024}, "exec": {"est_runtime_ms": None}},
    ],
    "edges": [
        {"from": "video", "to": "infer", "data_mb": 20},
        {"from": "infer", "to": "video", "data_mb": 20},
    ],
    "_comment": "资源保障策略：首次适应分配 + 最短路径路由",
}

TRAIN_DAG_TEMPLATE = {
    "job_id": "job-video-resource-guarantee-uuid",
    "submit_ts_ms": None,
    "policy_type": "RESOURCE_GUARANTEE",
    "job_name": "模型训练",
    "constraints": {"deadline_ms": None, "budget": None},
    "nodes": [
        {"node_id": "data", "resources": {"cpu_units": 20, "gpu_units": 0, "mem_mb": 1024,"disk_mb": 2048}, "exec": {"est_runtime_ms": None}},
        {"node_id": "infer", "resources": {"cpu_units": 10, "gpu_units": 1, "mem_mb": 1024,"disk_mb":1024}, "exec": {"est_runtime_ms": None}},
    ],
    "edges": [
        {"from": "data", "to": "infer", "data_mb": 8},
        {"from": "infer", "to": "data", "data_mb": 8},
    ],
    "_comment": "资源保障策略：首次适应分配 + 最短路径路由",
}

 