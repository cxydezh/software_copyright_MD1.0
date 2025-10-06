"""
数据库迁移脚本：创建流程日志表 process_logs（用于记录所有项目的流程行为）

执行步骤：
1. 备份数据库
2. 运行：python migrate_process_log.py
"""

from web_app.app import create_app
from database.models import db
from sqlalchemy import text


def migrate_process_log():
    app = create_app()
    with app.app_context():
        print("开始检查并创建流程日志表 process_logs ...")
        with db.engine.connect() as conn:
            # 按方言分别处理 DDL
            dialect = db.engine.dialect.name
            try:
                if 'mysql' in dialect:
                    ddl = (
                        """
                        CREATE TABLE IF NOT EXISTS process_logs (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            project_type VARCHAR(10) NOT NULL,
                            project_id INT NOT NULL,
                            action VARCHAR(100) NOT NULL,
                            actor_id INT,
                            actor_role VARCHAR(10),
                            from_status VARCHAR(50),
                            to_status VARCHAR(50),
                            note TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                else:
                    # 兼容 SQLite 等
                    ddl = (
                        """
                        CREATE TABLE IF NOT EXISTS process_logs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            project_type VARCHAR(10) NOT NULL,
                            project_id INTEGER NOT NULL,
                            action VARCHAR(100) NOT NULL,
                            actor_id INTEGER,
                            actor_role VARCHAR(10),
                            from_status VARCHAR(50),
                            to_status VARCHAR(50),
                            note TEXT,
                            created_at DATETIME
                        )
                        """
                    )
                conn.execute(text(ddl))
                conn.commit()
                print("✓ process_logs 表已存在或创建成功")
            except Exception as e:
                print(f"✗ 创建表失败：{e}")
                raise

        print("\n完成。")


if __name__ == '__main__':
    migrate_process_log()


