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
from django.views.generic import TemplateView
from . import views
from . import ai_views
from . import souvenir_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap as sitemap_xml
from accounts.sitemaps import (
    StaticViewSitemap, TourSitemap, BlogPostSitemap, 
    PageSitemap, CategorySitemap, CitySitemap, 
    CountrySitemap, DestinationRegionSitemap
)

sitemaps = {
    'static': StaticViewSitemap,
    'tours': TourSitemap,
    'blogs': BlogPostSitemap,
    'pages': PageSitemap,
    'categories': CategorySitemap,
    'cities': CitySitemap,
    'countries': CountrySitemap,
    'regions': DestinationRegionSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    path('set-language/<str:lang_code>/', views.set_language, name='set_language'),
    path('sitemap/', views.sitemap, name='sitemap'),
    path('sitemap.xml', sitemap_xml, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('contact-us/', views.contactus, name='contactus'),
    path('find-tour/', views.find_tour_page, name='find_tour'),
    path('tour-list/', views.tour_list, name='tour_list_fronted'),
    path('tours/filter/', views.tour_list_type_filtered, name='tour_list_type_filtered'),
    path('tour-detail/<str:tour_id>/', views.tour_detail, name='tour_detail'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
    path('tour-detail/payment/accept/<str:booking_number>/', views.tour_payment_accept, name='tour_payment_accept'),
    path('tour-detail/payment/cancel/<str:booking_number>/', views.tour_payment_cancel, name='tour_payment_cancel'),
    path('tour-providers/', views.tour_providers, name='tour_providers_fronted'),
    path('booking-confirmation/<str:booking_number>/', views.booking_confirmation, name='booking_confirmation'),
    path('blog-list/', views.blog_list, name='blog_list_fronted'),
    path('blog-detail/<str:blog_id>/', views.blog_detail, name='blog_detail_fronted'),
    path('tour-countries/', views.tour_countries, name='tour_countries_fronted'),
    path('tour-cities/', views.tour_cities, name='tour_cities_fronted'),
    path('tour-destination-regions/', views.tour_destination_regions, name='tour_destination_regions_fronted'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('page-view/<int:page_id>/<str:page_slug>/', views.page_view, name='page_view_fronted'),
    path('tour-feature-section/<int:feature_id>/', views.tour_feature_section, name='tour_feature_section_fronted'),
    path('ai-chat/', ai_views.ai_chat_proxy, name='ai_chat_proxy'),
    path('rent-bike/', views.rent_bike, name='rent_bike'),
    path('rent-bike/confirmation/<str:booking_number>/', views.rent_bike_confirmation, name='rent_bike_confirmation'),
    path('rent-bike/payment/accept/<str:booking_number>/', views.rent_bike_payment_accept, name='rent_bike_payment_accept'),
    path('rent-bike/payment/cancel/<str:booking_number>/', views.rent_bike_payment_cancel, name='rent_bike_payment_cancel'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),

    path('todo/', include('todo.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    path('system-developer/', views.system_developer, name='system_developer'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),
    path('send-test-email-smtp/', views.send_test_email_smtp, name='send_test_email_smtp'),
    path('send-test-email-template/', views.send_test_email_template, name='send_test_email_template'),
    
    # Souvenirs Frontend
    path('souvenirs/', souvenir_views.souvenirs_list, name='souvenirs_list_frontend'),
    path('souvenir-detail/<str:souvenir_id>/', souvenir_views.souvenir_detail, name='souvenir_detail_frontend'),
    
    # Cart
    path('cart/', souvenir_views.cart_view, name='cart_view'),
    path('cart/payment/accept/<str:order_number>/', souvenir_views.cart_payment_accept, name='cart_payment_accept'),
    path('cart/payment/cancel/<str:order_number>/', souvenir_views.cart_payment_cancel, name='cart_payment_cancel'),
    path('add-to-cart/<int:souvenir_id>/', souvenir_views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:souvenir_id>/', souvenir_views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:souvenir_id>/', souvenir_views.remove_from_cart, name='remove_from_cart'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
