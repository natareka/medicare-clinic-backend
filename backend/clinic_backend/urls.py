from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to MediCare Clinic API - System is Live!")

urlpatterns = [
    path('', home), # Add this line to serve the frontend index.html at the root URL
    path('admin/', admin.site.urls),
    path('api/', include('clinic.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "MediCare Clinic Admin"
admin.site.site_title = "MediCare Admin Portal"
admin.site.index_title = "Welcome to MediCare Admin Dashboard"
