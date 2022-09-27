from django.contrib import admin
from django.urls import include, path

from todolist.core.views import health_check

urlpatterns = [
    path('core/', include('todolist.core.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('ping/', health_check, name='health-check'),
    path('admin/', admin.site.urls),
]
