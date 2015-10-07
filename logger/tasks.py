from celery import Celery
import cProfile, pstats

from logger import scielo
import utils
import os

config = utils.Configuration.from_env()
settings = dict(config.items())['app:main']

celery_broker = settings.get('celery', 'amqp://guest@localhost//')
app = Celery('tasks', broker=celery_broker)

@app.task
def readlog(logfile, collection):
    pr = cProfile.Profile()
    pr.enable()

    file_profile = open('profile.txt', 'w')
    with scielo.Bulk(collection) as bk:
        bk.read_log(logfile)
        os.remove(logfile)

    pr.disable()
    ps = pstats.Stats(pr, stream=file_profile).sort_stats('cumulative')

    return 'read log: %s' % logfile
