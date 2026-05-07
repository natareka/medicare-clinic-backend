"""
Notification utilities for Email (SMTP) and SMS (Twilio)
"""
import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger('clinic')


def send_appointment_confirmation_email(appointment):
    """Send HTML email confirmation to patient."""
    try:
        subject = f"✅ Appointment Confirmed | Ref: APT-{str(appointment.appointment_id)[:8].upper()}"
        
        context = {
            'appointment': appointment,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
            'clinic_name': 'MediCare Clinic',
            'clinic_phone': '+65 6XXX XXXX',
            'clinic_email': 'info@medicare-clinic.com',
            'clinic_address': '123 Medical Drive, Singapore 123456',
        }

        html_content = render_to_string('email/appointment_confirmation.html', context)
        text_content = (
            f"Dear {appointment.patient.full_name},\n\n"
            f"Your appointment has been confirmed.\n"
            f"Reference: APT-{str(appointment.appointment_id)[:8].upper()}\n"
            f"Doctor: Dr. {appointment.doctor.name}\n"
            f"Date: {appointment.appointment_date.strftime('%B %d, %Y')}\n"
            f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n\n"
            f"Please arrive 15 minutes early.\n\n"
            f"MediCare Clinic Team"
        )

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=f"MediCare Clinic <{settings.DEFAULT_FROM_EMAIL}>",
            to=[appointment.patient.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)

        appointment.email_sent = True
        appointment.save(update_fields=['email_sent'])
        logger.info(f"Confirmation email sent to {appointment.patient.email}")
        return True

    except Exception as e:
        logger.error(f"Email error for appointment {appointment.appointment_id}: {e}")
        return False


def send_appointment_confirmation_sms(appointment):
    """Send SMS confirmation via Twilio."""
    try:
        from twilio.rest import Client
        
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message_body = (
            f"✅ MediCare Clinic\n"
            f"Appointment Confirmed!\n"
            f"Ref: APT-{str(appointment.appointment_id)[:8].upper()}\n"
            f"Dr. {appointment.doctor.name}\n"
            f"Date: {appointment.appointment_date.strftime('%d %b %Y')}\n"
            f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n"
            f"Please arrive 15 mins early.\n"
            f"Helpline: +65 6XXX XXXX"
        )

        patient_phone = appointment.patient.phone
        if not patient_phone.startswith('+'):
            patient_phone = '+65' + patient_phone.lstrip('0')

        message = client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=patient_phone
        )

        appointment.sms_sent = True
        appointment.save(update_fields=['sms_sent'])
        logger.info(f"SMS sent to {patient_phone}, SID: {message.sid}")
        return True

    except ImportError:
        logger.warning("Twilio not installed. Run: pip install twilio")
        return False
    except Exception as e:
        logger.error(f"SMS error: {e}")
        return False


def send_appointment_cancellation_email(appointment):
    """Send cancellation notification email."""
    try:
        subject = f"❌ Appointment Cancelled | Ref: APT-{str(appointment.appointment_id)[:8].upper()}"
        body = (
            f"Dear {appointment.patient.full_name},\n\n"
            f"Your appointment has been cancelled.\n"
            f"Reference: APT-{str(appointment.appointment_id)[:8].upper()}\n"
            f"Doctor: Dr. {appointment.doctor.name}\n"
            f"Date: {appointment.appointment_date.strftime('%B %d, %Y')}\n\n"
            f"To reschedule, please visit our website or call +65 6XXX XXXX.\n\n"
            f"MediCare Clinic Team"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[appointment.patient.email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        logger.error(f"Cancellation email error: {e}")
        return False


def send_contact_acknowledgement_email(contact):
    """Acknowledge contact form submission."""
    try:
        subject = "Thank you for contacting MediCare Clinic"
        body = (
            f"Dear {contact.name},\n\n"
            f"Thank you for reaching out to MediCare Clinic.\n"
            f"We have received your message and will respond within 24 hours.\n\n"
            f"Subject: {contact.subject}\n\n"
            f"For urgent matters, call: +65 6XXX XXXX\n\n"
            f"MediCare Clinic Team"
        )
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            fail_silently=True,
        )
        return True
    except Exception as e:
        logger.error(f"Contact acknowledgement email error: {e}")
        return False


def send_reminder_sms(appointment):
    """Send appointment reminder SMS 24hrs before."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message_body = (
            f"⏰ REMINDER - MediCare Clinic\n"
            f"Tomorrow: Appt with Dr. {appointment.doctor.name}\n"
            f"Time: {appointment.appointment_time.strftime('%I:%M %p')}\n"
            f"Ref: APT-{str(appointment.appointment_id)[:8].upper()}\n"
            f"Questions? Call: +65 6XXX XXXX"
        )

        patient_phone = appointment.patient.phone
        if not patient_phone.startswith('+'):
            patient_phone = '+65' + patient_phone.lstrip('0')

        client.messages.create(
            body=message_body,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=patient_phone
        )
        appointment.reminder_sent = True
        appointment.save(update_fields=['reminder_sent'])
        return True
    except Exception as e:
        logger.error(f"Reminder SMS error: {e}")
        return False
