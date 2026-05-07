"""
Management command: python manage.py seed_data
Seeds the database with demo departments, doctors, services, and testimonials.
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from clinic.models import Department, Doctor, DoctorSchedule, Testimonial, Service


DEPARTMENTS = [
    {'name': 'Cardiology', 'description': 'Heart and cardiovascular care by expert cardiologists.', 'icon': 'fas fa-heartbeat'},
    {'name': 'Neurology', 'description': 'Brain, spine and nervous system treatment.', 'icon': 'fas fa-brain'},
    {'name': 'Orthopedics', 'description': 'Bone, joint and musculoskeletal care.', 'icon': 'fas fa-bone'},
    {'name': 'Pediatrics', 'description': "Specialized care for children's health.", 'icon': 'fas fa-baby'},
    {'name': 'Oncology', 'description': 'Advanced cancer detection and treatment.', 'icon': 'fas fa-ribbon'},
    {'name': 'Dermatology', 'description': 'Skin, hair and nail conditions treated by specialists.', 'icon': 'fas fa-user-md'},
    {'name': 'Gynecology', "description": "Women's reproductive health and wellness.", 'icon': 'fas fa-female'},
    {'name': 'General Surgery', 'description': 'Minimally invasive and open surgical procedures.', 'icon': 'fas fa-procedures'},
    {'name': 'Ophthalmology', 'description': 'Eye care, vision correction and surgery.', 'icon': 'fas fa-eye'},
    {'name': 'ENT', 'description': 'Ear, Nose and Throat treatment specialists.', 'icon': 'fas fa-head-side-mask'},
]

DOCTORS = [
    {'name': 'Sarah Chen', 'dept': 'Cardiology', 'qual': 'MD, DM Cardiology', 'spec': 'Interventional Cardiology', 'exp': 15, 'fee': 150, 'rating': 4.9},
    {'name': 'James Lim', 'dept': 'Neurology', 'qual': 'MD, DM Neurology', 'spec': 'Stroke & Epilepsy', 'exp': 12, 'fee': 130, 'rating': 4.8},
    {'name': 'Priya Sharma', 'dept': 'Orthopedics', 'qual': 'MBBS, MS Ortho', 'spec': 'Joint Replacement', 'exp': 10, 'fee': 120, 'rating': 4.7},
    {'name': 'Michael Tan', 'dept': 'Pediatrics', 'qual': 'MBBS, MD Pediatrics', 'spec': 'Child Development', 'exp': 8, 'fee': 100, 'rating': 4.9},
    {'name': 'Aisha Rahman', 'dept': 'Oncology', 'qual': 'MD, DM Oncology', 'spec': 'Medical Oncology', 'exp': 14, 'fee': 200, 'rating': 4.8},
    {'name': 'David Wong', 'dept': 'Dermatology', 'qual': 'MBBS, MD Dermatology', 'spec': 'Cosmetic Dermatology', 'exp': 9, 'fee': 110, 'rating': 4.6},
    {'name': 'Meera Nair', 'dept': 'Gynecology', 'qual': 'MBBS, MS OBG', 'spec': "Women's Health", 'exp': 11, 'fee': 125, 'rating': 4.9},
    {'name': 'Robert Kumar', 'dept': 'General Surgery', 'qual': 'MBBS, MS Surgery', 'spec': 'Laparoscopic Surgery', 'exp': 13, 'fee': 140, 'rating': 4.7},
]

SERVICES = [
    {'title': '24/7 Emergency Care', 'description': 'Round-the-clock emergency services with rapid response teams.', 'icon': 'fas fa-ambulance', 'order': 1},
    {'title': 'Advanced Diagnostics', 'description': 'State-of-the-art MRI, CT scan, PET scan and lab services.', 'icon': 'fas fa-microscope', 'order': 2},
    {'title': 'Online Appointment', 'description': 'Book appointments online anytime with instant confirmation.', 'icon': 'fas fa-calendar-check', 'order': 3},
    {'title': 'Pharmacy Services', 'description': 'In-house pharmacy with all major medications available.', 'icon': 'fas fa-pills', 'order': 4},
    {'title': 'ICU & Critical Care', 'description': 'Fully equipped ICU with specialist intensivists 24/7.', 'icon': 'fas fa-procedures', 'order': 5},
    {'title': 'Health Packages', 'description': 'Comprehensive health checkup packages for all age groups.', 'icon': 'fas fa-clipboard-list', 'order': 6},
]

TESTIMONIALS = [
    {'name': 'Amanda Lee', 'rating': 5, 'msg': 'Excellent service! The doctors are highly professional and caring. Booking was seamless and the staff made me feel at ease throughout my visit.'},
    {'name': 'Raj Patel', 'rating': 5, 'msg': 'Dr. Sarah Chen is amazing. She explained my condition clearly and the treatment was very effective. Highly recommend MediCare Clinic.'},
    {'name': 'Linda Goh', 'rating': 5, 'msg': 'The online appointment system is very convenient. I got an SMS and email confirmation instantly. World-class facility!'},
    {'name': 'Thomas Ng', 'rating': 4, 'msg': 'Very good experience overall. The waiting time was minimal and the doctors are thorough. Will definitely come back.'},
    {'name': 'Fatimah Ibrahim', 'rating': 5, 'msg': 'Best clinic in the area! The pediatric team is wonderful with children. My son felt comfortable throughout the consultation.'},
    {'name': 'Kevin Tan', 'rating': 5, 'msg': 'Professional, clean and modern facility. The appointment reminder SMS was very helpful. Impressed with the overall experience.'},
]


class Command(BaseCommand):
    help = 'Seed database with demo clinic data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding MediCare Clinic data...')

        # Create Departments
        dept_map = {}
        for dept_data in DEPARTMENTS:
            dept, created = Department.objects.get_or_create(
                name=dept_data['name'],
                defaults={
                    'slug': slugify(dept_data['name']),
                    'description': dept_data['description'],
                    'icon': dept_data['icon'],
                }
            )
            dept_map[dept_data['name']] = dept
            status = '✅ Created' if created else '⏭️  Exists'
            self.stdout.write(f'  {status}: {dept.name}')

        # Create Doctors
        for doc_data in DOCTORS:
            dept = dept_map.get(doc_data['dept'])
            if not dept:
                continue
            doctor, created = Doctor.objects.get_or_create(
                name=doc_data['name'],
                defaults={
                    'department': dept,
                    'qualification': doc_data['qual'],
                    'specialization': doc_data['spec'],
                    'experience_years': doc_data['exp'],
                    'consultation_fee': doc_data['fee'],
                    'rating': doc_data['rating'],
                    'total_patients': 100 + doc_data['exp'] * 50,
                    'is_available': True,
                }
            )
            if created:
                # Add weekly schedule Mon-Fri
                for day in range(5):
                    DoctorSchedule.objects.create(
                        doctor=doctor,
                        day_of_week=day,
                        start_time='09:00',
                        end_time='17:00',
                        slot_duration_minutes=30,
                        max_patients=16,
                    )
                # Saturday morning
                DoctorSchedule.objects.create(
                    doctor=doctor,
                    day_of_week=5,
                    start_time='09:00',
                    end_time='13:00',
                    slot_duration_minutes=30,
                    max_patients=8,
                )
            status = '✅ Created' if created else '⏭️  Exists'
            self.stdout.write(f'  {status}: Dr. {doctor.name}')

        # Create Services
        for svc_data in SERVICES:
            svc, created = Service.objects.get_or_create(
                title=svc_data['title'],
                defaults={
                    'description': svc_data['description'],
                    'icon': svc_data['icon'],
                    'order': svc_data['order'],
                }
            )
            status = '✅ Created' if created else '⏭️  Exists'
            self.stdout.write(f'  {status}: {svc.title}')

        # Create Testimonials
        for t_data in TESTIMONIALS:
            t, created = Testimonial.objects.get_or_create(
                patient_name=t_data['name'],
                defaults={
                    'rating': t_data['rating'],
                    'message': t_data['msg'],
                    'is_approved': True,
                }
            )
            if created:
                self.stdout.write(f'  ✅ Created testimonial: {t.patient_name}')

        self.stdout.write(self.style.SUCCESS('\n✨ Seed completed successfully!'))
        self.stdout.write('   Run: python manage.py runserver')
