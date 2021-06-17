"""elearning URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
# Use include() to add paths from the catalog application 
from django.urls import include
#Add URL maps to redirect the base URL to our application
from django.views.generic import RedirectView
# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.utils.translation import gettext_lazy as _
from gogoedu.views import change_language
import notifications.urls


urlpatterns = [
    path('change_language/', change_language, name='change_language'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('gogoedu/', include('gogoedu.urls')),
    path('memory/', include('memory.urls')),
    path('', RedirectView.as_view(url='gogoedu/')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    prefix_default_language=False,
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
