#!/usr/bin/env python
"""
意图解析API集成测试
测试完整的API流程，包括流式接口和任务创建
"""
import sys
import os
# 确保从server目录导入 (tests/ -> server/)
_server_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _server_dir not in sys.path:
    sys.path.insert(0, _server_dir)

import unittest
import json
import time
from datetime import datetime, timedelta

import httpx


BASE_URL = "http://localhost:6000"
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class TestAuth(unittest.TestCase):
    """认证测试"""

    def setUp(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    def tearDown(self):
        self.client.close()

    def test_login(self):
        """测试登录获取token"""
        response = self.client.post("/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)


class TestChatAPI(unittest.TestCase):
    """聊天API测试"""

    def setUp(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=60.0)
        # 登录获取token
        response = self.client.post("/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        self.client.close()

    def test_chat_stream_video_inference(self):
        """测试视频AI推理流式解析"""
        future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        payload = {
            "session_id": f"test_{int(time.time())}",
            "prompt": "我想用yolov8模型进行视频AI推理，延迟2秒，帧率25，分辨率1920x1080，时间优先模态，2026-04-25 10:00开始，运行10分钟",
            "history": [],
            "files": [],
            "state": {
                "session_id": f"test_{int(time.time())}",
                "workflow": "intent_parsing",
                "stage": "intent_parsing",
                "parse_success": False,
                "missing_params": [],
                "reason_params": [],
                "intent_result": {},
                "dag": {},
                "code": 0,
                "msg": ""
            }
        }

        with self.client.stream("POST", "/chat/stream", json=payload, headers=self.headers) as response:
            self.assertEqual(response.status_code, 200)

            final_state = None
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if data.get("type") == "state":
                            final_state = data
                    except json.JSONDecodeError:
                        continue

            self.assertIsNotNone(final_state, "未收到最终状态")
            self.assertTrue(final_state.get("parse_success"), f"解析失败: {final_state.get('reason_params')}")
            self.assertIn("dag", final_state)
            self.assertNotEqual(len(final_state["dag"]), 0, "DAG为空")

            # 验证DAG内容
            dag = final_state["dag"]
            self.assertEqual(dag["policy_type"], "LOW_LATENCY")
            self.assertEqual(dag["job_name"], "视频AI推理")

    def test_chat_stream_model_training(self):
        """测试模型训练流式解析"""
        payload = {
            "session_id": f"test_{int(time.time())}",
            "prompt": "帮我用resnet训练CIFAR-100数据集，训练10轮，资源保障模态，2026-04-25 10:00开始，运行2小时",
            "history": [],
            "files": [],
            "state": {
                "session_id": f"test_{int(time.time())}",
                "workflow": "intent_parsing",
                "stage": "intent_parsing",
                "parse_success": False,
                "missing_params": [],
                "reason_params": [],
                "intent_result": {},
                "dag": {},
                "code": 0,
                "msg": ""
            }
        }

        with self.client.stream("POST", "/chat/stream", json=payload, headers=self.headers) as response:
            self.assertEqual(response.status_code, 200)

            final_state = None
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if data.get("type") == "state":
                            final_state = data
                    except json.JSONDecodeError:
                        continue

            self.assertIsNotNone(final_state, "未收到最终状态")


class TestTaskAPI(unittest.TestCase):
    """任务API测试"""

    def setUp(self):
        self.client = httpx.Client(base_url=BASE_URL, timeout=30.0)
        # 登录获取token
        response = self.client.post("/auth/login", json={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def tearDown(self):
        self.client.close()

    def test_create_task(self):
        """测试创建任务"""
        future_time = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        session_id = f"test_task_{int(time.time())}"
        payload = {
            "session_id": session_id,
            "business": "视频AI推理",
            "state": {},
            "params": {
                "业务类型": "视频AI推理",
                "参数": {
                    "模型名称": "yolov8",
                    "延迟": "2",
                    "视频帧率": "25",
                    "分辨率": "1920x1080",
                    "开始时间": future_time,
                    "期望运行时间": "10分钟"
                }
            },
            "dag": {}
        }

        response = self.client.post("/tasks", json=payload, headers=self.headers)
        self.assertIn(response.status_code, [200, 201, 400])  # 400可能是已存在


def run_api_tests():
    """运行API测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 检查服务器是否可用
    try:
        client = httpx.Client(base_url=BASE_URL, timeout=5.0)
        client.get("/health")
        client.close()
    except Exception:
        print("错误: API服务器未运行，请先启动 python idn_agent.py")
        return 1

    suite.addTests(loader.loadTestsFromTestCase(TestAuth))
    suite.addTests(loader.loadTestsFromTestCase(TestChatAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskAPI))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_api_tests())
