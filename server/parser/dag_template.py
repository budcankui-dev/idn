from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class DAGNode:
    """DAG节点定义"""
    node_id: str
    cpu_units: int
    mem_mb: int
    disk_mb: int
    est_runtime_ms: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "resources": {
                "cpu_units": self.cpu_units,
                "gpu_units": 0,
                "mem_mb": self.mem_mb,
                "disk_mb": self.disk_mb,
            },
            "exec": {
                "est_runtime_ms": self.est_runtime_ms,
            }
        }


@dataclass
class DAGEdge:
    """DAG边定义"""
    from_node: str
    to_node: str
    data_mb: int

    def to_dict(self) -> dict:
        return {
            "from": self.from_node,
            "to": self.to_node,
            "data_mb": self.data_mb,
        }


@dataclass
class DAGTemplate:
    """DAG模板基类"""
    job_name: str
    policy_type: str
    nodes: List[DAGNode] = field(default_factory=list)
    edges: List[DAGEdge] = field(default_factory=list)
    submit_ts_ms: Optional[int] = None
    deadline_ms: Optional[int] = None
    budget: Optional[int] = None
    job_id: str = ""
    _comment: str = ""

    def set_job_id(self, job_id: str):
        self.job_id = job_id

    def set_submit_ts_ms(self, ts_ms: int):
        self.submit_ts_ms = ts_ms

    def set_deadline_ms(self, ts_ms: int):
        self.deadline_ms = ts_ms

    def set_runtime(self, runtime_ms: int):
        """设置所有节点的运行时长"""
        for node in self.nodes:
            node.est_runtime_ms = runtime_ms
        if self.submit_ts_ms:
            self.deadline_ms = self.submit_ts_ms + runtime_ms

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "submit_ts_ms": self.submit_ts_ms,
            "policy_type": self.policy_type,
            "job_name": self.job_name,
            "constraints": {
                "deadline_ms": self.deadline_ms,
                "budget": self.budget,
            },
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "_comment": self._comment,
        }


class VideoInferenceDAG(DAGTemplate):
    """视频AI推理DAG模板"""
    POLICY_TYPE = "LOW_LATENCY"  # 低延时转发模态

    def __init__(self, session_id: str = ""):
        super().__init__(
            job_name="视频AI推理",
            policy_type=self.POLICY_TYPE,
            job_id=f"视频AI推理_低延时转发模态_{session_id}",
            _comment="低延时转发策略：优先保证低延迟",
            nodes=[
                DAGNode(node_id="video", cpu_units=20, mem_mb=1024, disk_mb=1024),
                DAGNode(node_id="infer", cpu_units=10, mem_mb=1024, disk_mb=1024),
            ],
            edges=[
                DAGEdge(from_node="video", to_node="infer", data_mb=20),
                DAGEdge(from_node="infer", to_node="video", data_mb=20),
            ]
        )


class ModelTrainingDAG(DAGTemplate):
    """模型训练DAG模板"""
    POLICY_TYPE = "INTELLIGENT_CENTER"  # 智算中心模态

    def __init__(self, session_id: str = ""):
        super().__init__(
            job_name="模型训练",
            policy_type=self.POLICY_TYPE,
            job_id=f"模型训练_智算中心模态_{session_id}",
            _comment="智算中心策略：智能分配计算资源",
            nodes=[
                DAGNode(node_id="data", cpu_units=20, mem_mb=1024, disk_mb=2048),
                DAGNode(node_id="train", cpu_units=20, mem_mb=2048, disk_mb=2048),
            ],
            edges=[
                DAGEdge(from_node="data", to_node="train", data_mb=8),
                DAGEdge(from_node="train", to_node="data", data_mb=8),
            ]
        )


# 保留旧的字典格式以保持向后兼容
VIDEO_DAG_TEMPLATE = {
    "job_id": "job-video-uuid",
    "submit_ts_ms": None,
    "policy_type": "LOW_LATENCY",
    "job_name": "视频AI推理",
    "constraints": {"deadline_ms": None, "budget": None},
    "nodes": [
        {"node_id": "video", "resources": {"cpu_units": 20, "gpu_units": 0, "mem_mb": 1024, "disk_mb": 1024}, "exec": {"est_runtime_ms": None}},
        {"node_id": "infer", "resources": {"cpu_units": 10, "gpu_units": 0, "mem_mb": 1024, "disk_mb": 1024}, "exec": {"est_runtime_ms": None}},
    ],
    "edges": [
        {"from": "video", "to": "infer", "data_mb": 20},
        {"from": "infer", "to": "video", "data_mb": 20},
    ],
    "_comment": "低延时转发策略",
}

TRAIN_DAG_TEMPLATE = {
    "job_id": "job-train-uuid",
    "submit_ts_ms": None,
    "policy_type": "INTELLIGENT_CENTER",
    "job_name": "模型训练",
    "constraints": {"deadline_ms": None, "budget": None},
    "nodes": [
        {"node_id": "data", "resources": {"cpu_units": 20, "gpu_units": 0, "mem_mb": 1024, "disk_mb": 2048}, "exec": {"est_runtime_ms": None}},
        {"node_id": "train", "resources": {"cpu_units": 20, "gpu_units": 0, "mem_mb": 2048, "disk_mb": 2048}, "exec": {"est_runtime_ms": None}},
    ],
    "edges": [
        {"from": "data", "to": "train", "data_mb": 8},
        {"from": "train", "to": "data", "data_mb": 8},
    ],
    "_comment": "智算中心策略",
}
