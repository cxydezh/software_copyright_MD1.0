#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速迁移本地数据库
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop_app.migrate_local_db import migrate_database
from config.config import LOCAL_CONFIG

if __name__ == '__main__':
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    print(f"数据库路径: {db_path}")
    migrate_database(db_path)

