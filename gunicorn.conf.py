bind: str = "127.0.0.1:8000"
proxy_allow_ips: str = "*"
chdir: str = "/web/dsn/"
workers: int = 5
reload: bool = True
errorlog: str = "/web/dsn/logs/gunicorn_error.log"
loglevel: str = "debug"
timeout: int = 300
