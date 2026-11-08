from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # 1. Config & Navigation
    path('config/', views.site_config, name='site_config'),
    path('home/', views.home_page_data, name='home_page_data'),
    path('faqs/', views.faq_list, name='faq_list'),
    path('team/', views.team_members, name='team_members'),
    path('testimonials/', views.testimonials, name='testimonials'),

    # 2. CMS Pages
    path('pages/', views.page_list, name='page_list'),
    path('pages/<str:page_slug>/', views.page_detail, name='page_detail'),

    # 3. Tours
    path('tours/', views.tour_list, name='tour_list'),
    path('tours/<str:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tours/<str:tour_id>/reviews/', views.submit_tour_review, name='submit_tour_review'),
    path('feature-sections/', views.feature_sections, name='feature_sections'),
    path('feature-sections/<int:feature_id>/', views.feature_section_detail, name='feature_section_detail'),

    # 4. Taxonomies & Destinations
    path('categories/', views.category_list, name='category_list'),
    path('destinations/countries/', views.country_list, name='country_list'),
    path('destinations/cities/', views.city_list, name='city_list'),
    path('destinations/regions/', views.region_list, name='region_list'),
    path('suppliers/', views.supplier_list, name='supplier_list'),

    # 5. Coupons & Tour Bookings
    path('coupons/validate/', views.validate_coupon, name='validate_coupon'),
    path('bookings/', views.create_booking, name='create_booking'),
    path('bookings/<str:booking_number>/', views.booking_detail, name='booking_detail'),
    path('bookings/<str:booking_number>/payment/accept/', views.booking_payment_accept, name='booking_payment_accept'),
    path('bookings/<str:booking_number>/payment/cancel/', views.booking_payment_cancel, name='booking_payment_cancel'),

    # 6. Blog
    path('blogs/', views.blog_list, name='blog_list'),
    path('blogs/<str:blog_id>/', views.blog_detail, name='blog_detail'),

    # 7. Bike Rentals
    path('bikes/', views.bike_list, name='bike_list'),
    path('bikes/<str:bike_id>/', views.bike_detail, name='bike_detail'),
    path('bikes/book/', views.create_bike_booking, name='create_bike_booking'),
    path('bikes/booking/<str:booking_number>/', views.bike_booking_detail, name='bike_booking_detail'),
    path('bikes/booking/<str:booking_number>/payment/accept/', views.bike_payment_accept, name='bike_payment_accept'),
    path('bikes/booking/<str:booking_number>/payment/cancel/', views.bike_payment_cancel, name='bike_payment_cancel'),

    # 8. Souvenirs & Shop
    path('souvenirs/', views.souvenir_list, name='souvenir_list'),
    path('souvenirs/<str:souvenir_id>/', views.souvenir_detail, name='souvenir_detail'),
    path('souvenirs/pickup-locations/', views.souvenir_pickup_locations, name='souvenir_pickup_locations'),

    # Cart endpoints
    path('cart/', views.cart_get, name='cart_get'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/clear/', views.cart_clear, name='cart_clear'),
    path('cart/checkout/', views.cart_checkout, name='cart_checkout'),
    path('orders/<str:order_number>/', views.order_detail, name='order_detail'),

    # 9. Contact & Newsletter
    path('contact/', views.contact_submit, name='contact_submit'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),

    # 10. AI Assistant
    path('ai-chat/', views.ai_chat, name='ai_chat'),

    # 11. Customer Authentication & User Account
    path('auth/register/', views.customer_register, name='customer_register'),
    path('auth/login/', views.customer_login, name='customer_login'),
    path('auth/logout/', views.customer_logout, name='customer_logout'),
    path('auth/profile/', views.customer_profile, name='customer_profile'),
    path('customer/bookings/', views.customer_bookings, name='customer_bookings'),
    path('customer/bike-bookings/', views.customer_bike_bookings, name='customer_bike_bookings'),
    path('customer/orders/', views.customer_orders, name='customer_orders'),
    path('customer/wishlist/', views.customer_wishlist, name='customer_wishlist'),
    path('customer/wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
]

