#!/usr/bin/env python
"""
意图解析后端测试套件
测试参数解析、DAG生成等功能，便于每次代码改动后验证正确性
"""
import sys
import os
# 确保从server目录导入 (tests/ -> server/)
_server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _server_dir not in sys.path:
    sys.path.insert(0, _server_dir)

import unittest
import json
from datetime import datetime, timedelta

from parser.state import State
from parser.state_parser import (
    parse_intent_output,
    parse_start_time,
    parse_duration,
    VIDEO_KEY_PARAMS,
    TRAIN_KEY_PARAMS,
    VIDEO_RESOLUTIONS,
)
from parser.dag_template import (
    DAGNode,
    DAGEdge,
    DAGTemplate,
    VideoInferenceDAG,
    ModelTrainingDAG,
    VIDEO_DAG_TEMPLATE,
    TRAIN_DAG_TEMPLATE,
)


class TestTimeParsing(unittest.TestCase):
    """时间解析测试"""

    def test_parse_start_time_valid(self):
        """测试有效的开始时间解析"""
        # 使用未来时间
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d 10:00")
        ts = parse_start_time(future_date)
        self.assertIsInstance(ts, int)
        self.assertGreater(ts, 0)

    def test_parse_start_time_relative(self):
        """测试相对时间解析 - 注意：依赖于dateparser库的能力"""
        try:
            ts = parse_start_time("明天上午10点")
            self.assertIsInstance(ts, int)
            self.assertGreater(ts, datetime.now().timestamp() * 1000)
        except ValueError:
            # dateparser可能不支持该格式，跳过测试
            self.skipTest("dateparser不支持该相对时间格式")

    def test_parse_start_time_invalid(self):
        """测试无效时间"""
        with self.assertRaises(ValueError):
            parse_start_time("invalid-time")

    def test_parse_duration_valid(self):
        """测试有效的运行时长解析"""
        ms = parse_duration("2小时30分钟", "视频AI推理")
        self.assertEqual(ms, 2 * 3600 * 1000 + 30 * 60 * 1000)

    def test_parse_duration_short(self):
        """测试运行时长过短"""
        with self.assertRaises(ValueError):
            parse_duration("1分钟", "视频AI推理")

    def test_parse_duration_model_training(self):
        """测试模型训练最小运行时长"""
        with self.assertRaises(ValueError):
            parse_duration("10分钟", "模型训练")


class TestDAGTemplate(unittest.TestCase):
    """DAG模板测试"""

    def test_dag_node_to_dict(self):
        """测试节点转换为字典"""
        node = DAGNode(node_id="test", cpu_units=10, mem_mb=1024, disk_mb=1024)
        d = node.to_dict()
        self.assertEqual(d["node_id"], "test")
        self.assertEqual(d["resources"]["cpu_units"], 10)
        self.assertEqual(d["resources"]["gpu_units"], 0)  # 无GPU
        self.assertIsNone(d["exec"]["est_runtime_ms"])

    def test_dag_edge_to_dict(self):
        """测试边转换为字典"""
        edge = DAGEdge(from_node="a", to_node="b", data_mb=100)
        d = edge.to_dict()
        self.assertEqual(d["from"], "a")
        self.assertEqual(d["to"], "b")
        self.assertEqual(d["data_mb"], 100)

    def test_video_inference_dag(self):
        """测试视频AI推理DAG"""
        dag = VideoInferenceDAG(session_id="test_session")
        self.assertEqual(dag.policy_type, "LOW_LATENCY")
        self.assertEqual(dag.job_name, "视频AI推理")
        self.assertEqual(len(dag.nodes), 2)
        self.assertEqual(len(dag.edges), 2)

        # 验证无GPU
        for node in dag.nodes:
            self.assertEqual(node.to_dict()["resources"]["gpu_units"], 0)

    def test_model_training_dag(self):
        """测试模型训练DAG"""
        dag = ModelTrainingDAG(session_id="test_session")
        self.assertEqual(dag.policy_type, "INTELLIGENT_CENTER")
        self.assertEqual(dag.job_name, "模型训练")
        self.assertEqual(len(dag.nodes), 2)

        # 验证无GPU
        for node in dag.nodes:
            self.assertEqual(node.to_dict()["resources"]["gpu_units"], 0)

    def test_video_inference_dag_runtime(self):
        """测试视频AI推理DAG运行时长设置"""
        dag = VideoInferenceDAG(session_id="test")
        dag.set_submit_ts_ms(1000000000000)
        dag.set_runtime(600000)  # 10分钟

        self.assertEqual(dag.submit_ts_ms, 1000000000000)
        self.assertEqual(dag.deadline_ms, 1000000000000 + 600000)
        for node in dag.nodes:
            self.assertEqual(node.est_runtime_ms, 600000)

    def test_video_inference_dag_to_dict(self):
        """测试DAG转换为字典"""
        dag = VideoInferenceDAG(session_id="test_session")
        dag.set_submit_ts_ms(1000000000000)
        dag.set_runtime(600000)

        d = dag.to_dict()
        self.assertEqual(d["policy_type"], "LOW_LATENCY")
        self.assertEqual(d["job_name"], "视频AI推理")
        self.assertIn("job_id", d)
        self.assertIn("submit_ts_ms", d)
        self.assertIn("constraints", d)
        self.assertIn("nodes", d)
        self.assertIn("edges", d)


class TestIntentParsing(unittest.TestCase):
    """意图解析测试"""

    def setUp(self):
        self.state = State()
        self.state.session_id = "test_session_123"
        # 使用未来时间避免时间过期的测试问题
        self.future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d 10:00")

    def test_parse_video_inference_success(self):
        """测试视频AI推理成功解析"""
        llm_output = json.dumps({
            "业务类型": "视频AI推理",
            "参数": {
                "模型名称": "yolov8",
                "延迟": "2",
                "视频帧率": "25",
                "分辨率": "1920x1080",
                "开始时间": self.future_time,
                "期望运行时间": "10分钟"
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertTrue(state.parse_success, f"parse_success=False, missing={state.missing_params}, reason={state.reason_params}")
        self.assertEqual(state.stage, "complete")
        self.assertEqual(len(state.missing_params), 0)
        self.assertEqual(len(state.reason_params), 0)
        self.assertIsNotNone(state.dag)
        self.assertEqual(state.dag["policy_type"], "LOW_LATENCY")

    def test_parse_video_inference_missing_params(self):
        """测试视频AI推理缺失参数"""
        llm_output = json.dumps({
            "业务类型": "视频AI推理",
            "参数": {
                "模型名称": "yolov8",
                # 缺失延迟、视频帧率等
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertFalse(state.parse_success)
        self.assertIn("延迟", state.missing_params)
        self.assertIn("视频帧率", state.missing_params)

    def test_parse_video_inference_invalid_resolution(self):
        """测试无效分辨率"""
        llm_output = json.dumps({
            "业务类型": "视频AI推理",
            "参数": {
                "模型名称": "yolov8",
                "延迟": "2",
                "视频帧率": "25",
                "分辨率": "invalid",
                "开始时间": self.future_time,
                "期望运行时间": "10分钟"
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertFalse(state.parse_success)
        self.assertTrue(any("分辨率" in r["param"] for r in state.reason_params))

    def test_parse_video_inference_valid_resolutions(self):
        """测试所有有效的分辨率"""
        for res in VIDEO_RESOLUTIONS:
            llm_output = json.dumps({
                "业务类型": "视频AI推理",
                "参数": {
                    "模型名称": "yolov8",
                    "延迟": "2",
                    "视频帧率": "25",
                    "分辨率": res,
                    "开始时间": self.future_time,
                    "期望运行时间": "10分钟"
                }
            })
            state = parse_intent_output(llm_output, self.state)
            self.assertTrue(state.parse_success, f"分辨率 {res} 应该有效")

    def test_parse_model_training_success(self):
        """测试模型训练成功解析"""
        llm_output = json.dumps({
            "业务类型": "模型训练",
            "参数": {
                "模型名称": "resnet",
                "数据集": "CIFAR-100",
                "训练轮次": "10",
                "开始时间": self.future_time,
                "期望运行时间": "1小时",
                "训练完成时间": "1小时"
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertTrue(state.parse_success)
        self.assertEqual(state.dag["policy_type"], "INTELLIGENT_CENTER")

    def test_parse_model_training_flexible_param_names(self):
        """测试灵活参数名推断"""
        # 测试"训练轮数" -> "训练轮次"
        llm_output = json.dumps({
            "业务类型": "模型训练",
            "参数": {
                "模型名称": "resnet",
                "数据集": "CIFAR-100",
                "训练轮数": "10",
                "开始时间": self.future_time,
                "期望运行时间": "1小时",
                "训练完成时间": "1小时"
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertTrue(state.parse_success)

    def test_parse_model_training_mismatched_finish_time(self):
        """测试训练完成时间与期望运行时间不匹配"""
        llm_output = json.dumps({
            "业务类型": "模型训练",
            "参数": {
                "模型名称": "resnet",
                "数据集": "CIFAR-100",
                "训练轮次": "10",
                "开始时间": self.future_time,
                "期望运行时间": "1小时",
                "训练完成时间": "2小时"  # 不匹配
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertFalse(state.parse_success)
        self.assertTrue(any("训练完成时间" in r["param"] for r in state.reason_params))

    def test_parse_unknown_business_type(self):
        """测试未知业务类型"""
        llm_output = json.dumps({
            "业务类型": "未知业务",
            "参数": {}
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertFalse(state.parse_success)

    def test_parse_json_error(self):
        """测试JSON解析错误"""
        state = parse_intent_output("not valid json", self.state)
        self.assertEqual(state.code, -1)
        self.assertIn("JSON解析失败", state.msg)

    def test_video_inference_no_modality_in_params(self):
        """测试视频AI推理不包含模态参数（系统预设）"""
        llm_output = json.dumps({
            "业务类型": "视频AI推理",
            "参数": {
                "模型名称": "yolov8",
                "延迟": "2",
                "视频帧率": "25",
                "分辨率": "1920x1080",
                "开始时间": self.future_time,
                "期望运行时间": "10分钟"
            }
        })
        state = parse_intent_output(llm_output, self.state)
        self.assertTrue(state.parse_success)
        # DAG中policy_type应该是系统预设的LOW_LATENCY，而不是从参数读取
        self.assertEqual(state.dag["policy_type"], "LOW_LATENCY")


class TestDAGFill(unittest.TestCase):
    """DAG填充测试"""

    def setUp(self):
        self.state = State()
        self.state.session_id = "test_session_123"
        # 使用未来时间避免时间过期的测试问题
        self.future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d 10:00")

    def test_video_dag_filled_correctly(self):
        """测试视频DAG正确填充"""
        llm_output = json.dumps({
            "业务类型": "视频AI推理",
            "参数": {
                "模型名称": "yolov8",
                "延迟": "2",
                "视频帧率": "25",
                "分辨率": "1920x1080",
                "开始时间": self.future_time,
                "期望运行时间": "10分钟"
            }
        })
        state = parse_intent_output(llm_output, self.state, fill_dag=True)
        dag = state.dag

        self.assertEqual(dag["policy_type"], "LOW_LATENCY")
        self.assertEqual(dag["job_name"], "视频AI推理")
        self.assertIn("submit_ts_ms", dag)
        self.assertIn("constraints", dag)
        self.assertEqual(len(dag["nodes"]), 2)

        # 验证无GPU
        for node in dag["nodes"]:
            self.assertEqual(node["resources"]["gpu_units"], 0)

    def test_model_training_dag_filled_correctly(self):
        """测试模型训练DAG正确填充"""
        llm_output = json.dumps({
            "业务类型": "模型训练",
            "参数": {
                "模型名称": "resnet",
                "数据集": "CIFAR-100",
                "训练轮次": "10",
                "开始时间": self.future_time,
                "期望运行时间": "1小时",
                "训练完成时间": "1小时"
            }
        })
        state = parse_intent_output(llm_output, self.state, fill_dag=True)
        dag = state.dag

        self.assertEqual(dag["policy_type"], "INTELLIGENT_CENTER")
        self.assertEqual(dag["job_name"], "模型训练")

        # 验证无GPU
        for node in dag["nodes"]:
            self.assertEqual(node["resources"]["gpu_units"], 0)


class TestBackwardCompatibility(unittest.TestCase):
    """向后兼容性测试"""

    def test_old_dag_template_still_works(self):
        """测试旧的DAG模板格式仍然可用"""
        # 验证旧模板格式的完整性
        self.assertIn("job_id", VIDEO_DAG_TEMPLATE)
        self.assertIn("nodes", VIDEO_DAG_TEMPLATE)
        self.assertIn("edges", VIDEO_DAG_TEMPLATE)

        # 验证gpu_units为0
        for node in VIDEO_DAG_TEMPLATE["nodes"]:
            self.assertEqual(node["resources"]["gpu_units"], 0)


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTimeParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestDAGTemplate))
    suite.addTests(loader.loadTestsFromTestCase(TestIntentParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestDAGFill))
    suite.addTests(loader.loadTestsFromTestCase(TestBackwardCompatibility))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
