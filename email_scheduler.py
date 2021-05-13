from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os
# import logging

scheduler = None

def deadline_reached(event_id, email, question):
    os.system('python3 send_email.py --data_event_id "{}" --to_email "{}" --question "{}" &'.format(event_id, email, question))

def start_scheduler(database_url):
    global scheduler
    jobstores = {
        'default': SQLAlchemyJobStore(url=database_url)
    }
    scheduler = BackgroundScheduler(jobstores=jobstores, job_defaults={'misfire_grace_time':3600})
    scheduler.start()
    # logging.basicConfig()
    # log = logging.getLogger('apscheduler')
    # log.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(fmt='%(asctime)s|%(levelname)s%(name)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # stream_handler = logging.StreamHandler()
    # file_handler = logging.FileHandler('apscheduler.log', encoding='utf-8')
    # stream_handler.setFormatter(formatter)
    # file_handler.setFormatter(formatter)
    # log.addHandler(stream_handler)
    # log.addHandler(file_handler)

def add_job(event_id, timestamp, email, question):
    global scheduler
    scheduler.add_job(deadline_reached, 'date', run_date=timestamp, id=event_id, replace_existing=True, args=[event_id, email, question])

def shutdown_scheduler():
    global scheduler
    scheduler.shutdown()
