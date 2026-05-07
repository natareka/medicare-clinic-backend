import logging
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Department, Doctor, DoctorSchedule, Patient, Appointment, Testimonial, ContactMessage, Service
from .serializers import (
    DepartmentSerializer, DoctorSerializer, DoctorListSerializer,
    PatientSerializer, AppointmentSerializer, AppointmentCreateSerializer,
    TestimonialSerializer, ContactMessageSerializer, ServiceSerializer
)
from .notifications import (
    send_appointment_confirmation_email,
    send_appointment_confirmation_sms,
    send_appointment_cancellation_email,
    send_contact_acknowledgement_email,
)

logger = logging.getLogger('clinic')


# ─── DEPARTMENTS ──────────────────────────────────────────────────────────────
@api_view(['GET'])
def department_list(request):
    departments = Department.objects.filter(is_active=True)
    serializer = DepartmentSerializer(departments, many=True, context={'request': request})
    return Response({'success': True, 'data': serializer.data})


@api_view(['GET'])
def department_detail(request, pk):
    try:
        department = Department.objects.get(pk=pk, is_active=True)
        serializer = DepartmentSerializer(department, context={'request': request})
        return Response({'success': True, 'data': serializer.data})
    except Department.DoesNotExist:
        return Response({'success': False, 'message': 'Department not found'}, status=404)


# ─── DOCTORS ──────────────────────────────────────────────────────────────────
@api_view(['GET'])
def doctor_list(request):
    doctors = Doctor.objects.filter(is_available=True).select_related('department')
    department_id = request.GET.get('department')
    if department_id:
        doctors = doctors.filter(department_id=department_id)
    search = request.GET.get('search')
    if search:
        doctors = doctors.filter(name__icontains=search) | doctors.filter(specialization__icontains=search)
    serializer = DoctorListSerializer(doctors, many=True, context={'request': request})
    return Response({'success': True, 'data': serializer.data})


@api_view(['GET'])
def doctor_detail(request, pk):
    try:
        doctor = Doctor.objects.get(pk=pk)
        serializer = DoctorSerializer(doctor, context={'request': request})
        return Response({'success': True, 'data': serializer.data})
    except Doctor.DoesNotExist:
        return Response({'success': False, 'message': 'Doctor not found'}, status=404)


@api_view(['GET'])
def doctor_available_slots(request, pk):
    """Get available time slots for a doctor on a given date."""
    try:
        doctor = Doctor.objects.get(pk=pk)
        date_str = request.GET.get('date')
        if not date_str:
            return Response({'success': False, 'message': 'Date parameter required'}, status=400)

        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_of_week = date.weekday()

        schedules = DoctorSchedule.objects.filter(
            doctor=doctor, day_of_week=day_of_week, is_active=True
        )

        if not schedules.exists():
            return Response({'success': True, 'data': [], 'message': 'Doctor not available on this day'})

        booked_times = set(
            Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                status__in=['PENDING', 'CONFIRMED']
            ).values_list('appointment_time', flat=True)
        )

        available_slots = []
        for schedule in schedules:
            current = datetime.combine(date, schedule.start_time)
            end = datetime.combine(date, schedule.end_time)
            while current < end:
                slot_time = current.time()
                if slot_time not in booked_times:
                    available_slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'display': current.strftime('%I:%M %p'),
                        'available': True
                    })
                else:
                    available_slots.append({
                        'time': slot_time.strftime('%H:%M'),
                        'display': current.strftime('%I:%M %p'),
                        'available': False
                    })
                current += timedelta(minutes=schedule.slot_duration_minutes)

        return Response({'success': True, 'data': available_slots})
    except Doctor.DoesNotExist:
        return Response({'success': False, 'message': 'Doctor not found'}, status=404)
    except ValueError:
        return Response({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD'}, status=400)


# ─── APPOINTMENTS ─────────────────────────────────────────────────────────────
@api_view(['POST'])
def book_appointment(request):
    """Create appointment with patient registration if new."""
    serializer = AppointmentCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({'success': False, 'errors': serializer.errors}, status=400)

    data = serializer.validated_data

    try:
        doctor = Doctor.objects.get(pk=data['doctor_id'], is_available=True)
        department = Department.objects.get(pk=data['department_id'])
    except Doctor.DoesNotExist:
        return Response({'success': False, 'message': 'Doctor not found or not available'}, status=404)
    except Department.DoesNotExist:
        return Response({'success': False, 'message': 'Department not found'}, status=404)

    # Check slot availability
    if Appointment.objects.filter(
        doctor=doctor,
        appointment_date=data['appointment_date'],
        appointment_time=data['appointment_time'],
        status__in=['PENDING', 'CONFIRMED']
    ).exists():
        return Response({'success': False, 'message': 'This time slot is already booked. Please choose another.'}, status=409)

    # Get or create patient
    patient, created = Patient.objects.get_or_create(
        email=data['email'],
        defaults={
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone': data['phone'],
            'date_of_birth': data.get('date_of_birth'),
            'gender': data['gender'],
            'address': data.get('address', ''),
            'city': data.get('city', ''),
            'blood_group': data.get('blood_group', ''),
        }
    )

    if not created:
        # Update patient info
        patient.first_name = data['first_name']
        patient.last_name = data['last_name']
        patient.phone = data['phone']
        patient.save()

    # Create appointment
    appointment = Appointment.objects.create(
        patient=patient,
        doctor=doctor,
        department=department,
        appointment_date=data['appointment_date'],
        appointment_time=data['appointment_time'],
        appointment_type=data.get('appointment_type', 'CONSULTATION'),
        symptoms=data.get('symptoms', ''),
        consultation_fee=doctor.consultation_fee,
        status='CONFIRMED',
    )

    # Update doctor patient count
    doctor.total_patients += 1
    doctor.save(update_fields=['total_patients'])

    # Send notifications
    email_sent = send_appointment_confirmation_email(appointment)
    sms_sent = send_appointment_confirmation_sms(appointment)

    return Response({
        'success': True,
        'message': 'Appointment booked successfully!',
        'data': {
            'appointment_id': str(appointment.appointment_id),
            'reference': f"APT-{str(appointment.appointment_id)[:8].upper()}",
            'patient_name': patient.full_name,
            'doctor': f"Dr. {doctor.name}",
            'department': department.name,
            'date': appointment.appointment_date.strftime('%B %d, %Y'),
            'time': appointment.appointment_time.strftime('%I:%M %p'),
            'status': appointment.status,
            'email_sent': email_sent,
            'sms_sent': sms_sent,
        }
    }, status=201)


@api_view(['GET'])
def appointment_detail(request, appointment_id):
    """Get appointment by UUID reference."""
    try:
        appointment = Appointment.objects.get(appointment_id=appointment_id)
        serializer = AppointmentSerializer(appointment)
        return Response({'success': True, 'data': serializer.data})
    except Appointment.DoesNotExist:
        return Response({'success': False, 'message': 'Appointment not found'}, status=404)


@api_view(['GET'])
def patient_appointments(request):
    """Get appointments by patient email."""
    email = request.GET.get('email')
    if not email:
        return Response({'success': False, 'message': 'Email required'}, status=400)
    try:
        patient = Patient.objects.get(email=email)
        appointments = patient.appointments.all().order_by('-appointment_date', '-appointment_time')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({'success': True, 'data': serializer.data, 'patient': PatientSerializer(patient).data})
    except Patient.DoesNotExist:
        return Response({'success': False, 'message': 'No patient found with this email'}, status=404)


@api_view(['POST'])
def cancel_appointment(request, appointment_id):
    """Cancel an appointment."""
    try:
        appointment = Appointment.objects.get(appointment_id=appointment_id)
        if appointment.status in ['COMPLETED', 'CANCELLED']:
            return Response({'success': False, 'message': f'Cannot cancel a {appointment.status.lower()} appointment'}, status=400)
        appointment.status = 'CANCELLED'
        appointment.save()
        send_appointment_cancellation_email(appointment)
        return Response({'success': True, 'message': 'Appointment cancelled successfully.'})
    except Appointment.DoesNotExist:
        return Response({'success': False, 'message': 'Appointment not found'}, status=404)


# ─── TESTIMONIALS ─────────────────────────────────────────────────────────────
@api_view(['GET'])
def testimonial_list(request):
    testimonials = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:12]
    serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
    return Response({'success': True, 'data': serializer.data})


# ─── CONTACT ──────────────────────────────────────────────────────────────────
@api_view(['POST'])
def contact_submit(request):
    serializer = ContactMessageSerializer(data=request.data)
    if serializer.is_valid():
        contact = serializer.save()
        send_contact_acknowledgement_email(contact)
        return Response({'success': True, 'message': 'Message sent! We will contact you within 24 hours.'}, status=201)
    return Response({'success': False, 'errors': serializer.errors}, status=400)


# ─── SERVICES ─────────────────────────────────────────────────────────────────
@api_view(['GET'])
def service_list(request):
    services = Service.objects.filter(is_active=True)
    serializer = ServiceSerializer(services, many=True)
    return Response({'success': True, 'data': serializer.data})


# ─── DASHBOARD STATS ──────────────────────────────────────────────────────────
@api_view(['GET'])
def clinic_stats(request):
    stats = {
        'total_doctors': Doctor.objects.filter(is_available=True).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'total_patients': Patient.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'appointments_today': Appointment.objects.filter(
            appointment_date=timezone.now().date(),
            status='CONFIRMED'
        ).count(),
    }
    return Response({'success': True, 'data': stats})
