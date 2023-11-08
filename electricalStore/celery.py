import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'electricalStore.settings')

app = Celery('electricalStore')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'increase-debt-3-hours': {
        'task': 'chainModel.tasks.increase_debt',
        'schedule': crontab(hour='*/3'),
    },
    'decrease-debt-6-30-am': {
        'task': 'chainModel.tasks.decrease_debt',
        'schedule': crontab(minute='30', hour='6'),
    },
}

app.conf.timezone = 'Europe/Minsk'

