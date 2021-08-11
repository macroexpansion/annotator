import os
import subprocess


def _get_bool(key, default_value):
    if key in os.environ:
        value = os.environ[key]
        if value == 'True' or value == 'true' or value == '1':
            return True
        return False
    return default_value

class Config:
    NAME = os.getenv("NAME", "Annotator")
    VERSION = '0.1.2'

    ### File Watcher
    FILE_WATCHER = os.getenv("FILE_WATCHER", False)
    IGNORE_DIRECTORIES = ["_thumbnail", "_settings"]

    # Flask/Gunicorn
    #
    #   LOG_LEVEL - The granularity of log output
    #
    #       A string of "debug", "info", "warning", "error", "critical"
    #
    #   WORKER_CONNECTIONS - limits the maximum number of simultaneous
    #       clients that a single process can handle.
    #
    #       A positive integer generally set to around 1000.
    #
    #   WORKER_TIMEOUT - If a worker does not notify the master process
    #       in this number of seconds it is killed and a new worker is
    #       spawned to replace it.
    #
    SWAGGER_UI_JSONEDITOR = True
    DEBUG = os.getenv("DEBUG", 'false').lower() == 'true'
    PRELOAD = False

    MAX_CONTENT_LENGTH = os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024 * 1024)  # 16Gb

    MONGODB_HOST = os.getenv("MONGODB_HOST", "mongodb://localhost:27017/flask")
    MONGODB_CONNECT = False
    SECRET_KEY = os.getenv("SECRET_KEY", "<--- CHANGE THIS KEY --->")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "debug")
    WORKER_CONNECTIONS = 1000

    TESTING = os.getenv("TESTING", False)

    ### Worker
    CELERY_ACCEPT_CONTENT = ['application/x-python-serialize', 'json']
    BROKER_URL = os.getenv("BROKER_URL", "amqp://user:password@localhost:5672/%2f")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "mongodb://localhost:27017/flask")

    ### Dataset Options
    DATASET_DIRECTORY = os.getenv("DATASET_DIRECTORY", "datasets")
    INITIALIZE_FROM_FILE = os.getenv("INITIALIZE_FROM_FILE")

    ### User Options
    LOGIN_DISABLED = _get_bool("LOGIN_DISABLED", False)
    ALLOW_REGISTRATION = _get_bool('ALLOW_REGISTRATION', True)

    ### Models
    MASK_RCNN_FILE = os.getenv("MASK_RCNN_FILE", "")
    MASK_RCNN_CLASSES = os.getenv("MASK_RCNN_CLASSES", "BG")

    DEXTR_FILE = os.getenv("DEXTR_FILE", "/models/dextr_pascal-sbd.h5")


__all__ = ["Config"]
