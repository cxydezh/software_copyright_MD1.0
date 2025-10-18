#!/bin/bash
BACKUP_DIR="/var/backups/software_copyright"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
mysqldump -u webuser -p software_copyright > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/software_copyright/uploads

# 删除30天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
