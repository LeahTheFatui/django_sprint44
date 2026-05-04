from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler403, handler404, handler500
from users import views as users_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/', include('users.urls')),
    path('auth/registration/', users_views.RegistrationView.as_view(), name='registration'),
    path('auth/profile/<str:username>/', users_views.ProfileView.as_view(), name='profile'),
]

handler403 = 'pages.views.csrf_failure'
handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
