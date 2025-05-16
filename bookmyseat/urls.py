from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movies import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('users/', include('users.urls')),
#     path('',include('users.urls')),
#     path('movies/', include('movies.urls')),
#     path('', include('staticpages.urls')),
#     path('', views.home, name='home'),

# ]
urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),  # Add this line

    path('users/', include('users.urls')),
    path('movies/', include('movies.urls')),
    path('',views.home, name='home'),  # Set the home view for the root URL
    path('staticpages/', include('staticpages.urls')),  # Optional: Explicitly define static pages
    path('test-email/', views.test_email, name='test_email'),  # ✅ Add here
    #path('admin/dashboard/', admin_site.urls),  # Custom admin dashboard URL

    

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
