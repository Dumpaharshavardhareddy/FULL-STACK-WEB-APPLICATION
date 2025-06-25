from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/movies/', include('movies.urls')),
    path('api/theaters/', include('theaters.urls')),
    path('api/bookings/', include('bookings.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = 'MovieBook Administration'
admin.site.site_title = 'MovieBook Admin'
admin.site.index_title = 'Welcome to MovieBook Administration'