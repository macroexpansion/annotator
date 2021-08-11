from celery import Celery
from database import connect_mongo
from config import Config

import os, stat


st = os.stat('./script.sh')
os.chmod('./script.sh', st.st_mode | stat.S_IEXEC)

connect_mongo('Celery_Worker')

class CeleryConfig:
    NAME = Config.NAME
    CELERY_ACCEPT_CONTENT = Config.CELERY_ACCEPT_CONTENT
    BROKER_URL = Config.BROKER_URL
    CELERY_RESULT_BACKEND = Config.CELERY_RESULT_BACKEND

celery = Celery()
celery.config_from_object(CeleryConfig)

celery.autodiscover_tasks(['workers.tasks'])


if __name__ == '__main__':
    celery.start()
