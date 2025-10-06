#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面端-服务器 集成测试：登录与项目同步
账号：admin@yiqichuang.com / admin123
"""

import os
import sys
import unittest
import requests


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from desktop_app.server_client import ServerClient


SERVER_HOST = os.environ.get('TEST_SERVER_HOST', 'http://192.168.31.56')
SERVER_PORT = int(os.environ.get('TEST_SERVER_PORT', '5000'))
API_BASE = f"{SERVER_HOST}:{SERVER_PORT}/api/desktop"

ADMIN_EMAIL = os.environ.get('TEST_ADMIN_EMAIL', 'admin@yiqichuang.com')
ADMIN_PASS = os.environ.get('TEST_ADMIN_PASS', 'admin123')


class TestDesktopApiIntegration(unittest.TestCase):
    def test_01_api_login_via_requests(self):
        payload = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASS,
            'user_type': 'staff'
        }
        resp = requests.post(f"{API_BASE}/login", json=payload, timeout=10)
        self.assertEqual(resp.status_code, 200, msg=f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertEqual(data.get('user', {}).get('email'), ADMIN_EMAIL)

    def test_02_api_sync_projects_via_requests(self):
        payload = {
            'email': ADMIN_EMAIL,
            'password': ADMIN_PASS,
            'user_type': 'staff'
        }
        resp = requests.post(f"{API_BASE}/sync_projects", json=payload, timeout=15)
        self.assertEqual(resp.status_code, 200, msg=f"HTTP {resp.status_code}: {resp.text}")
        data = resp.json()
        self.assertTrue(data.get('success'), msg=data)
        self.assertIsInstance(data.get('projects'), list)

    def test_03_client_login_and_sync(self):
        client = ServerClient(SERVER_HOST, SERVER_PORT)
        ok, msg, user = client.login(ADMIN_EMAIL, ADMIN_PASS, 'staff')
        self.assertTrue(ok, msg)
        self.assertEqual(user.get('email'), ADMIN_EMAIL)

        ok, msg, projects = client.get_all_projects_for_sync()
        self.assertTrue(ok, msg)
        self.assertIsInstance(projects, list)


if __name__ == '__main__':
    unittest.main(verbosity=2)


