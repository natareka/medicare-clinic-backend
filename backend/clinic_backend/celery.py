import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_backend.settings')

app = Celery('clinic_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic task schedule
app.conf.beat_schedule = {
    'send-reminders-daily': {
        'task': 'clinic.tasks.send_appointment_reminders',
        'schedule': 3600.0,  # every hour
    },
    'mark-no-shows': {
        'task': 'clinic.tasks.mark_no_show_appointments',
        'schedule': 900.0,  # every 15 min
    },
    'cleanup-pending': {
        'task': 'clinic.tasks.cleanup_old_pending_appointments',
        'schedule': 86400.0,  # daily
    },
}
