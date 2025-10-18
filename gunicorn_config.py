import multiprocessing

# 服务器socket
bind = '127.0.0.1:8000'
backlog = 2048

# Worker进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# 日志
accesslog = '/var/log/software_copyright/gunicorn_access.log'
errorlog = '/var/log/software_copyright/gunicorn_error.log'
loglevel = 'info'

# 进程命名
proc_name = 'software_copyright_web'

# 守护进程
daemon = False

# 环境变量
raw_env = [
    'FLASK_CONFIG=production',
]
