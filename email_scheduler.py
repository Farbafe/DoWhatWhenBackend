from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

scheduler = None

def deadline_reached(event_id, email, question):
    # send to email the question with url for results
    print('send email to {} for question {}, and url is {}'.format(email, question, event_id))

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
