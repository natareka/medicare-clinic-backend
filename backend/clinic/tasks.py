"""
Celery Tasks — Background jobs for appointment reminders
Run with: celery -A clinic_backend worker --beat -l info
"""
import logging
from datetime import date, timedelta
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('clinic')


@shared_task
def send_appointment_reminders():
    """Send SMS/email reminders for tomorrow's appointments."""
    from clinic.models import Appointment
    from clinic.notifications import send_reminder_sms, send_appointment_confirmation_email

    tomorrow = date.today() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status='CONFIRMED',
        reminder_sent=False
    ).select_related('patient', 'doctor', 'department')

    sent = 0
    for appt in appointments:
        try:
            send_reminder_sms(appt)
            sent += 1
        except Exception as e:
            logger.error(f"Reminder failed for {appt.appointment_id}: {e}")

    logger.info(f"Sent {sent} appointment reminders for {tomorrow}")
    return f"Sent {sent} reminders"


@shared_task
def mark_no_show_appointments():
    """Mark past confirmed appointments as No Show after 2 hours."""
    from clinic.models import Appointment
    from datetime import datetime, time as dtime

    today = date.today()
    two_hours_ago = (timezone.now() - timedelta(hours=2)).time()

    no_shows = Appointment.objects.filter(
        appointment_date=today,
        appointment_time__lt=two_hours_ago,
        status='CONFIRMED'
    )
    count = no_shows.update(status='NO_SHOW')
    logger.info(f"Marked {count} appointments as NO_SHOW")
    return f"Marked {count} as no-show"


@shared_task
def cleanup_old_pending_appointments():
    """Cancel PENDING appointments older than 24 hours."""
    from clinic.models import Appointment

    cutoff = timezone.now() - timedelta(hours=24)
    cancelled = Appointment.objects.filter(
        status='PENDING',
        created_at__lt=cutoff
    ).update(status='CANCELLED')

    logger.info(f"Auto-cancelled {cancelled} stale pending appointments")
    return f"Cancelled {cancelled} stale appointments"
