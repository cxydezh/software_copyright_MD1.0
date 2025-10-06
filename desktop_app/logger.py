#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面应用统一日志模块
 - 采用 RotatingFileHandler 滚动日志
 - 默认日志路径: D:/SoftwareCopyrightMS/logs/desktop_app.log
 - 级别: INFO (可通过环境变量 DESKTOP_LOG_LEVEL 调整)
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass


def get_log_file_path() -> str:
    base_dir = os.environ.get('DESKTOP_LOG_BASE', 'D:/SoftwareCopyrightMS')
    log_dir = os.path.join(base_dir, 'logs')
    _ensure_dir(log_dir)
    return os.path.join(log_dir, 'desktop_app.log')


def get_logger(name: str = 'desktop_app') -> logging.Logger:
    level_name = os.environ.get('DESKTOP_LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    if logger.handlers:
        # 已初始化
        logger.setLevel(level)
        return logger

    logger.setLevel(level)

    # 控制台
    console = logging.StreamHandler()
    console.setLevel(level)
    fmt = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s - %(message)s')
    console.setFormatter(fmt)
    logger.addHandler(console)

    # 文件滚动
    log_file = get_log_file_path()
    file_handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=5, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    logger.propagate = False
    logger.debug('Logger initialized, level=%s, file=%s', level_name, log_file)
    return logger


