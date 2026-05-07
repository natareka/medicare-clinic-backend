from django.urls import path
from . import views

urlpatterns = [
    # Departments
    path('departments/', views.department_list, name='department-list'),
    path('departments/<int:pk>/', views.department_detail, name='department-detail'),

    # Doctors
    path('doctors/', views.doctor_list, name='doctor-list'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor-detail'),
    path('doctors/<int:pk>/slots/', views.doctor_available_slots, name='doctor-slots'),

    # Appointments
    path('appointments/book/', views.book_appointment, name='book-appointment'),
    path('appointments/<uuid:appointment_id>/', views.appointment_detail, name='appointment-detail'),
    path('appointments/<uuid:appointment_id>/cancel/', views.cancel_appointment, name='cancel-appointment'),
    path('appointments/patient/', views.patient_appointments, name='patient-appointments'),

    # Misc
    path('testimonials/', views.testimonial_list, name='testimonial-list'),
    path('contact/', views.contact_submit, name='contact-submit'),
    path('services/', views.service_list, name='service-list'),
    path('stats/', views.clinic_stats, name='clinic-stats'),
]
