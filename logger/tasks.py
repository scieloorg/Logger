from celery import Celery

from logger import scielo
import utils
import os

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

celery_broker = settings.get('celery', 'amqp://guest@localhost//')
app = Celery('tasks', broker=celery_broker)

@app.task
def readlog(logfile, collection):
    with scielo.Bulk(collection) as bk:
        bk.read_log(logfile)
        os.remove(logfile)

    return 'read log: %s' % logfile
