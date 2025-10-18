#!/bin/bash
# Web应用部署脚本

set -e

echo "========================================="
echo "软著管理系统 - Web应用部署"
echo "========================================="

# 配置变量
APP_DIR="/var/www/software_copyright"
VENV_DIR="$APP_DIR/venv"
BACKUP_DIR="/var/backups/software_copyright"

# 1. 创建备份
echo "[1/8] 创建备份..."
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
if [ -d "$APP_DIR" ]; then
    tar -czf $BACKUP_FILE -C /var/www software_copyright
    echo "备份已创建: $BACKUP_FILE"
fi

# 2. 创建应用目录
echo "[2/8] 创建应用目录..."
sudo mkdir -p $APP_DIR
sudo mkdir -p $APP_DIR/uploads
sudo mkdir -p $APP_DIR/logs
sudo mkdir -p /var/log/software_copyright

# 3. 复制应用文件
echo "[3/8] 复制应用文件..."
sudo cp -r web_app $APP_DIR/
sudo cp -r database $APP_DIR/
sudo cp -r config $APP_DIR/
sudo cp -r templates $APP_DIR/
sudo cp -r static $APP_DIR/
sudo cp -r migrate $APP_DIR/
sudo cp wsgi.py $APP_DIR/
sudo cp gunicorn_config.py $APP_DIR/
sudo cp requirements.txt $APP_DIR/

# 4. 创建虚拟环境
echo "[4/8] 创建Python虚拟环境..."
sudo python3 -m venv $VENV_DIR
sudo $VENV_DIR/bin/pip install --upgrade pip
sudo $VENV_DIR/bin/pip install -r $APP_DIR/requirements.txt
sudo $VENV_DIR/bin/pip install gunicorn

# 5. 设置环境变量
echo "[5/8] 配置环境变量..."
sudo tee $APP_DIR/.env > /dev/null <<EOF
FLASK_CONFIG=production
SECRET_KEY=$(openssl rand -hex 32)
DB_HOST=localhost
DB_PORT=3306
DB_USER=webuser
DB_PASSWORD=your_db_password
DB_NAME=software_copyright
APP_URL=https://your-domain.com
APPEMAILACCOUNT=your_email@example.com
APPEMAILSMTP=your_smtp_password
EOF

# 6. 数据库迁移
echo "[6/8] 执行数据库迁移..."
cd $APP_DIR
sudo -u www-data $VENV_DIR/bin/python init_mysql.py

# 7. 设置权限
echo "[7/8] 设置文件权限..."
sudo chown -R www-data:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod -R 775 $APP_DIR/uploads
sudo chmod -R 775 $APP_DIR/logs

# 8. 启动服务
echo "[8/8] 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable software_copyright
sudo systemctl restart software_copyright
sudo systemctl restart nginx

echo "========================================="
echo "Web应用部署完成！"
echo "访问地址: https://your-domain.com"
echo "========================================="
