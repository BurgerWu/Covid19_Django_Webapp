from django.contrib import admin
from django.urls import path

# Use include() to add URLS from the catalog application and authentication system
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('home/', include('home.urls')),
]

# Use static() to add url mapping to serve static files during development (only)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns+= static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

#Add URL maps to redirect the base URL to our application
from django.views.generic import RedirectView
urlpatterns += [
    path('', RedirectView.as_view(url='/home/', permanent=True)),
]


