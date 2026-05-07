from django.contrib import admin
from .models import Department, Doctor, DoctorSchedule, Patient, Appointment, Testimonial, ContactMessage, Service


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


class DoctorScheduleInline(admin.TabularInline):
    model = DoctorSchedule
    extra = 1


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'specialization', 'experience_years', 'consultation_fee', 'rating', 'is_available']
    list_filter = ['department', 'is_available', 'gender']
    search_fields = ['name', 'specialization']
    inlines = [DoctorScheduleInline]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'gender', 'blood_group', 'city', 'created_at']
    list_filter = ['gender', 'blood_group', 'city']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['patient_id', 'created_at', 'updated_at']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'patient', 'doctor', 'department', 'appointment_date', 'appointment_time', 'status', 'is_paid', 'email_sent', 'sms_sent']
    list_filter = ['status', 'appointment_type', 'department', 'appointment_date', 'is_paid']
    search_fields = ['patient__first_name', 'patient__last_name', 'doctor__name']
    readonly_fields = ['appointment_id', 'created_at', 'updated_at']
    date_hierarchy = 'appointment_date'

    def reference(self, obj):
        return f"APT-{str(obj.appointment_id)[:8].upper()}"
    reference.short_description = 'Reference'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'rating', 'department', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'department']
    actions = ['approve_testimonials']

    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_testimonials.short_description = "Approve selected testimonials"


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read']
    readonly_fields = ['created_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'icon', 'is_active', 'order']
    list_filter = ['is_active']
    ordering = ['order']
