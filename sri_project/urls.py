from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),

    # Routes de l'application agent_service
    path('api/', include('agent_service.urls')),
]

