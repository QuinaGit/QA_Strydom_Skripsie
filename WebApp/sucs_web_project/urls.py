"""sucs_web_project URL Configuration

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
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from users import views as user_views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),                    #admin web app
    path('register/', user_views.register, name='register'),    #register web app
    path('profile/', user_views.profile, name='profile'),    #profile class base views
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),    #login class base views
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),    #logout class base views
    path('', include('attendance.urls')),    #attendance web app
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)