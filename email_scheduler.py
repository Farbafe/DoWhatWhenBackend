from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os

scheduler = None

def deadline_reached(event_id, email, question):
    # send to email the question with url for results
    result = os.popen('python3 send_email.py -data_event_id "{}" -email "{}" -question "{}"'.format(event_id, email, question)).read()

def start_scheduler(database_url):
    global scheduler
    jobstores = {
        'default': SQLAlchemyJobStore(url=database_url)
    }
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.start()

def add_job(event_id, timestamp, email, question):
    global scheduler
    scheduler.add_job(deadline_reached, 'date', run_date=timestamp, id=event_id, replace_existing=True, coalesce=True, args=[event_id, email, question])

def shutdown_scheduler():
    global scheduler
    scheduler.shutdown()
