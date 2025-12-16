"""
URL configuration for Yourtourguide project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from . import views
from . import ai_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('set-language/<str:lang_code>/', views.set_language, name='set_language'),
    path('sitemap/', views.sitemap, name='sitemap'),
    path('contact-us/', views.contactus, name='contactus'),
    path('find-tour/', views.find_tour_page, name='find_tour'),
    path('tour-list/', views.tour_list, name='tour_list_fronted'),
    path('tours/filter/', views.tour_list_type_filtered, name='tour_list_type_filtered'),
    path('tour-detail/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tour-providers/', views.tour_providers, name='tour_providers_fronted'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('blog-list/', views.blog_list, name='blog_list_fronted'),
    path('blog-detail/<int:blog_id>/', views.blog_detail, name='blog_detail_fronted'),
    path('tour-countries/', views.tour_countries, name='tour_countries_fronted'),
    path('tour-cities/', views.tour_cities, name='tour_cities_fronted'),
    path('tour-destination-regions/', views.tour_destination_regions, name='tour_destination_regions_fronted'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('page-view/<int:page_id>/<str:page_slug>/', views.page_view, name='page_view_fronted'),
    path('tour-feature-section/<int:feature_id>/', views.tour_feature_section, name='tour_feature_section_fronted'),
    path('ai-chat/', ai_views.ai_chat_proxy, name='ai_chat_proxy'),

    path('todo/', include('todo.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('system-developer/', views.system_developer, name='system_developer'),
    
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
