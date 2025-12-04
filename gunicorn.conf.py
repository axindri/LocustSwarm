import multiprocessing
import os

bind = "0.0.0.0:3000"
worker_class = "sync"
timeout = 120
max_requests = 1000
max_requests_jitter = 100
preload_app = True
accesslog = "-"
errorlog = "-"
loglevel = "info"