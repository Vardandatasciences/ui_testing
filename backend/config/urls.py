from django.urls import path, include

urlpatterns = [
    path('', include('grc.urls')),  # This will make all GRC urls available at root
    # Remove the duplicate api prefix
    # path('api/', include('grc.urls')),  # This will prefix all URLs with /api/
] 