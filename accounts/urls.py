from django.urls import path
from . import views
from accounts.admin_panel import views as admin_views
from accounts.customer_panel import views as customer_views
from accounts.admin_panel import views_toursupplier as tour_supplier_views
from accounts.admin_panel import views_categories as category_views
from accounts.admin_panel import views_sliders as slider_views
from accounts.admin_panel import views_newsletters as newsletter_views
from accounts.admin_panel import views_contactus as contactus_views
from accounts.admin_panel import views_groups as group_views
from accounts.admin_panel import views_admins as admin_user_views
from accounts.admin_panel import views_reviews as review_views
from accounts.admin_panel import views_pages as page_views
from accounts.admin_panel import views_tours as tour_views
from accounts.admin_panel import views_bookings as booking_views
from accounts.admin_panel import views_payments as payment_views
from accounts.admin_panel import views_coupons as coupon_views
from accounts.admin_panel import views_cities as city_views
from accounts.admin_panel import views_blog as blog_views
from accounts.admin_panel import views_messages as message_views
from accounts.admin_panel import views_feature_section as feature_section_views
from accounts.admin_panel import views_website_menu as website_menu_views
from accounts.admin_panel import views_faq as faq_views
from accounts import views_frontend

urlpatterns = [
    path('newsletter/subscribe/', views_frontend.newsletter_subscribe, name='newsletter_subscribe'),
    path('register/customer/', customer_views.register_customer, name='register_customer'),
    path('register/admin/', admin_views.register_admin, name='register_admin'),
    path('login/customer/', customer_views.login_view, name='customer_login'),
    path('login/admin/', admin_views.login_view, name='admin_login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/customer/', customer_views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/customer/bookings/', customer_views.customer_booking_list, name='customer_my_bookings'),
    path('dashboard/customer/bookings/<int:booking_id>/', customer_views.customer_booking_detail, name='customer_booking_detail'),
    path('dashboard/customer/profile/', customer_views.customer_profile_update, name='customer_profile'),
    path('dashboard/customer/messages/', customer_views.customer_messages, name='customer_messages'),
    path('dashboard/customer/reviews/', customer_views.customer_reviews, name='customer_reviews'),
    path('dashboard/customer/reviews/delete/<int:review_id>/', customer_views.customer_review_delete, name='customer_review_delete'),
    path('dashboard/customer/wishlist/', customer_views.customer_wishlist_page, name='customer_wishlist_page'),
    path('dashboard/customer/wishlist/toggle/', customer_views.toggle_wishlist, name='toggle_wishlist'),
    path('dashboard/customer/chat/messages/', customer_views.get_chat_messages, name='customer_chat_messages'),
    path('dashboard/customer/chat/send/', customer_views.send_chat_message, name='customer_chat_send'),
    path('dashboard/admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    
    # Destination Region CRUD
    path('admin/destination-regions/', admin_views.destination_region_list, name='destination_region_list'),
    path('admin/destination-regions/create/', admin_views.destination_region_create, name='destination_region_create'),
    path('admin/destination-regions/<int:pk>/edit/', admin_views.destination_region_edit, name='destination_region_edit'),
    path('admin/destination-regions/<int:pk>/delete/', admin_views.destination_region_delete, name='destination_region_delete'),
    
    # Country CRUD
    path('admin/countries/', admin_views.country_list, name='country_list'),
    path('admin/countries/create/', admin_views.country_create, name='country_create'),
    path('admin/countries/<int:pk>/edit/', admin_views.country_edit, name='country_edit'),
    path('admin/countries/<int:pk>/delete/', admin_views.country_delete, name='country_delete'),
    
    # Customer CRUD
    path('admin/customers/', admin_views.customer_list, name='customer_list'),
    path('admin/customers/create/', admin_views.customer_create, name='customer_create'),
    path('admin/customers/<int:pk>/edit/', admin_views.customer_edit, name='customer_edit'),
    path('admin/customers/<int:pk>/delete/', admin_views.customer_delete, name='customer_delete'),
    path('admin/customers/<int:pk>/bookings/', admin_views.customer_booking_list, name='customer_booking_list'),
    path('admin/customers/<int:pk>/wishlist/', admin_views.customer_wishlist, name='customer_wishlist'),
    
    # Site Settings
    path('admin/settings/', admin_views.site_settings, name='site_settings'),

    # Tour Supplier CRUD
    path('admin/tour-suppliers/', tour_supplier_views.tour_supplier_list, name='tour_supplier_list'),
    path('admin/tour-suppliers/create/', tour_supplier_views.tour_supplier_create, name='tour_supplier_create'),
    path('admin/tour-suppliers/<int:pk>/edit/', tour_supplier_views.tour_supplier_edit, name='tour_supplier_edit'),
    path('admin/tour-suppliers/<int:pk>/delete/', tour_supplier_views.tour_supplier_delete, name='tour_supplier_delete'),

    # Category CRUD
    path('admin/categories/', category_views.category_list, name='category_list'),
    path('admin/categories/create/', category_views.category_create, name='category_create'),
    path('admin/categories/<int:pk>/edit/', category_views.category_edit, name='category_edit'),
    path('admin/categories/<int:pk>/delete/', category_views.category_delete, name='category_delete'),

    # Slider CRUD
    path('admin/sliders/', slider_views.slider_list, name='slider_list'),
    path('admin/sliders/create/', slider_views.slider_create, name='slider_create'),
    path('admin/sliders/<int:pk>/edit/', slider_views.slider_edit, name='slider_edit'),
    path('admin/sliders/<int:pk>/delete/', slider_views.slider_delete, name='slider_delete'),

    # Newsletter CRUD
    path('admin/newsletters/', newsletter_views.newsletter_list, name='newsletter_list'),
    path('admin/newsletters/create/', newsletter_views.newsletter_create, name='newsletter_create'),
    path('admin/newsletters/<int:pk>/edit/', newsletter_views.newsletter_edit, name='newsletter_edit'),
    path('admin/newsletters/<int:pk>/delete/', newsletter_views.newsletter_delete, name='newsletter_delete'),

    # Contact Us CRUD
    path('admin/contactus/', contactus_views.contactus_list, name='contactus_list'),
    path('admin/contactus/create/', contactus_views.contactus_create, name='contactus_create'),
    path('admin/contactus/<int:pk>/edit/', contactus_views.contactus_edit, name='contactus_edit'),
    path('admin/contactus/<int:pk>/delete/', contactus_views.contactus_delete, name='contactus_delete'),

    # Group CRUD
    path('admin/groups/', group_views.group_list, name='group_list'),
    path('admin/groups/create/', group_views.group_create, name='group_create'),
    path('admin/groups/<int:pk>/edit/', group_views.group_edit, name='group_edit'),
    path('admin/groups/<int:pk>/delete/', group_views.group_delete, name='group_delete'),

    # Admin User CRUD
    path('admin/admins/', admin_user_views.admin_list, name='admin_list'),
    path('admin/admins/create/', admin_user_views.admin_create, name='admin_create'),
    path('admin/admins/<int:pk>/edit/', admin_user_views.admin_edit, name='admin_edit'),
    path('admin/admins/<int:pk>/delete/', admin_user_views.admin_delete, name='admin_delete'),

    # Customer Review CRUD
    path('admin/reviews/', review_views.review_list, name='review_list'),
    path('admin/reviews/create/', review_views.review_create, name='review_create'),
    path('admin/reviews/<int:pk>/edit/', review_views.review_edit, name='review_edit'),
    path('admin/reviews/<int:pk>/delete/', review_views.review_delete, name='review_delete'),

    # Page CRUD
    path('admin/pages/', page_views.page_list, name='page_list'),
    path('admin/pages/create/', page_views.page_create, name='page_create'),
    path('admin/pages/<int:pk>/edit/', page_views.page_edit, name='page_edit'),
    path('admin/pages/<int:pk>/delete/', page_views.page_delete, name='page_delete'),
    # Tour CRUD
    path('admin/tours/', tour_views.tour_list, name='tour_list'),
    path('admin/tours/create/', tour_views.tour_create, name='tour_create'),
    path('admin/tours/<int:pk>/edit/', tour_views.tour_edit, name='tour_edit'),
    path('admin/tours/<int:pk>/delete/', tour_views.tour_delete, name='tour_delete'),
    path('admin/tours/<int:pk>/view/', tour_views.tour_view, name='tour_view'),
    path('admin/tours/<int:tour_id>/images/', tour_views.tour_image_list, name='tour_image_list'),
    path('admin/tours/<int:tour_id>/images/create/', tour_views.tour_image_create, name='tour_image_create'),
    path('admin/tours/<int:tour_id>/images/<int:image_id>/edit/', tour_views.tour_image_edit, name='tour_image_edit'),
    path('admin/tours/<int:tour_id>/images/<int:image_id>/delete/', tour_views.tour_image_delete, name='tour_image_delete'),
    path('admin/tours/<int:tour_id>/images/<int:image_id>/set-primary/', tour_views.tour_image_set_primary, name='tour_image_set_primary'),
    path('admin/tours/<int:tour_id>/highlights/', tour_views.tour_highlights_list, name='tour_highlights_list'),
    path('admin/tours/<int:tour_id>/highlights/create/', tour_views.tour_highlight_create, name='tour_highlight_create'),
    path('admin/tours/<int:tour_id>/highlights/<int:highlight_id>/edit/', tour_views.tour_highlight_edit, name='tour_highlight_edit'),
    path('admin/tours/<int:tour_id>/highlights/<int:highlight_id>/delete/', tour_views.tour_highlight_delete, name='tour_highlight_delete'),

    # Tour Included
    path('admin/tours/<int:tour_id>/included/', tour_views.tour_included_list, name='tour_included_list'),
    path('admin/tours/<int:tour_id>/included/create/', tour_views.tour_included_create, name='tour_included_create'),
    path('admin/tours/<int:tour_id>/included/<int:item_id>/edit/', tour_views.tour_included_edit, name='tour_included_edit'),
    path('admin/tours/<int:tour_id>/included/<int:item_id>/delete/', tour_views.tour_included_delete, name='tour_included_delete'),

    # Tour Excluded
    path('admin/tours/<int:tour_id>/excluded/', tour_views.tour_excluded_list, name='tour_excluded_list'),
    path('admin/tours/<int:tour_id>/excluded/create/', tour_views.tour_excluded_create, name='tour_excluded_create'),
    path('admin/tours/<int:tour_id>/excluded/<int:item_id>/edit/', tour_views.tour_excluded_edit, name='tour_excluded_edit'),
    path('admin/tours/<int:tour_id>/excluded/<int:item_id>/delete/', tour_views.tour_excluded_delete, name='tour_excluded_delete'),

    # Tour Itinerary
    path('admin/tours/<int:tour_id>/itinerary/', tour_views.tour_itinerary_list, name='tour_itinerary_list'),
    path('admin/tours/<int:tour_id>/itinerary/create/', tour_views.tour_itinerary_create, name='tour_itinerary_create'),
    path('admin/tours/<int:tour_id>/itinerary/<int:step_id>/edit/', tour_views.tour_itinerary_edit, name='tour_itinerary_edit'),
    path('admin/tours/<int:tour_id>/itinerary/<int:step_id>/delete/', tour_views.tour_itinerary_delete, name='tour_itinerary_delete'),

    # Tour Requirements
    path('admin/tours/<int:tour_id>/requirements/', tour_views.tour_requirement_list, name='tour_requirement_list'),
    path('admin/tours/<int:tour_id>/requirements/create/', tour_views.tour_requirement_create, name='tour_requirement_create'),
    path('admin/tours/<int:tour_id>/requirements/<int:req_id>/edit/', tour_views.tour_requirement_edit, name='tour_requirement_edit'),
    path('admin/tours/<int:tour_id>/requirements/<int:req_id>/delete/', tour_views.tour_requirement_delete, name='tour_requirement_delete'),

    # Tour FAQs
    path('admin/tours/<int:tour_id>/faqs/', tour_views.tour_faq_list, name='tour_faq_list'),
    path('admin/tours/<int:tour_id>/faqs/create/', tour_views.tour_faq_create, name='tour_faq_create'),
    path('admin/tours/<int:tour_id>/faqs/<int:faq_id>/edit/', tour_views.tour_faq_edit, name='tour_faq_edit'),
    path('admin/tours/<int:tour_id>/faqs/<int:faq_id>/delete/', tour_views.tour_faq_delete, name='tour_faq_delete'),

    # Tour Pricing
    path('admin/tours/<int:tour_id>/pricing/', tour_views.tour_pricing_list, name='tour_pricing_list'),
    path('admin/tours/<int:tour_id>/pricing/create/', tour_views.tour_pricing_create, name='tour_pricing_create'),
    path('admin/tours/<int:tour_id>/pricing/<int:pricing_id>/edit/', tour_views.tour_pricing_edit, name='tour_pricing_edit'),
    path('admin/tours/<int:tour_id>/pricing/<int:pricing_id>/delete/', tour_views.tour_pricing_delete, name='tour_pricing_delete'),

    # Tour Schedule
    path('admin/tours/<int:tour_id>/schedule/', tour_views.tour_schedule_list, name='tour_schedule_list'),
    path('admin/tours/<int:tour_id>/schedule/create/', tour_views.tour_schedule_create, name='tour_schedule_create'),
    path('admin/tours/<int:tour_id>/schedule/<int:schedule_id>/edit/', tour_views.tour_schedule_edit, name='tour_schedule_edit'),
    path('admin/tours/<int:tour_id>/schedule/<int:schedule_id>/delete/', tour_views.tour_schedule_delete, name='tour_schedule_delete'),

    # Tour Blackout Dates
    path('admin/tours/<int:tour_id>/blackout/', tour_views.tour_blackout_list, name='tour_blackout_list'),
    path('admin/tours/<int:tour_id>/blackout/create/', tour_views.tour_blackout_create, name='tour_blackout_create'),
    path('admin/tours/<int:tour_id>/blackout/<int:blackout_id>/edit/', tour_views.tour_blackout_edit, name='tour_blackout_edit'),
    path('admin/tours/<int:tour_id>/blackout/<int:blackout_id>/delete/', tour_views.tour_blackout_delete, name='tour_blackout_delete'),

    # Booking CRUD
    path('admin/bookings/', booking_views.booking_list, name='booking_list'),
    path('admin/bookings/create/', booking_views.booking_create, name='booking_create'),
    path('admin/bookings/<int:pk>/', booking_views.booking_detail, name='booking_detail'),
    path('admin/bookings/<int:pk>/edit/', booking_views.booking_edit, name='booking_edit'),
    path('admin/bookings/<int:pk>/status/', booking_views.booking_status_update, name='booking_status_update'),
    path('admin/bookings/<int:booking_id>/participants/', booking_views.booking_participants_list, name='booking_participants_list'),
    path('admin/bookings/<int:pk>/invoice/', booking_views.booking_invoice, name='booking_invoice'),
    path('admin/bookings/<int:pk>/add-payment/', booking_views.booking_add_payment, name='booking_add_payment'),
    path('admin/bookings/<int:pk>/send-invoice/', booking_views.booking_send_invoice, name='booking_send_invoice'),

    # Payment CRUD
    path('admin/payments/', payment_views.payment_list, name='payment_list'),
    path('admin/payments/<int:pk>/', payment_views.payment_detail, name='payment_detail'),
    path('admin/payments/<int:pk>/status/', payment_views.payment_status_update, name='payment_status_update'),

    # Tour Review CRUD
    path('admin/tour-reviews/', review_views.tour_review_list, name='tour_review_list'),
    path('admin/tour-reviews/<int:pk>/', review_views.tour_review_detail, name='tour_review_detail'),
    path('admin/tour-reviews/<int:pk>/status/', review_views.tour_review_status_update, name='tour_review_status_update'),
    path('admin/tour-reviews/<int:pk>/feature/', review_views.tour_review_feature_toggle, name='tour_review_feature_toggle'),

    # Coupon CRUD
    path('admin/coupons/', coupon_views.coupon_list, name='coupon_list'),
    path('admin/coupons/create/', coupon_views.coupon_create, name='coupon_create'),
    path('admin/coupons/<int:pk>/edit/', coupon_views.coupon_edit, name='coupon_edit'),
    path('admin/coupons/<int:pk>/delete/', coupon_views.coupon_delete, name='coupon_delete'),
    path('admin/coupons/<int:pk>/', coupon_views.coupon_detail, name='coupon_detail'),
    path('admin/coupons/<int:pk>/toggle/', coupon_views.coupon_toggle_active, name='coupon_toggle_active'),

    # City CRUD
    path('admin/cities/', city_views.city_list, name='city_list'),
    path('admin/cities/create/', city_views.city_create, name='city_create'),
    path('admin/cities/<int:pk>/edit/', city_views.city_edit, name='city_edit'),
    path('admin/cities/<int:pk>/delete/', city_views.city_delete, name='city_delete'),
    path('admin/cities/<int:pk>/', city_views.city_detail, name='city_detail'),
    path('admin/cities/<int:pk>/toggle/', city_views.city_toggle_active, name='city_toggle_active'),
    path('admin/cities/<int:pk>/toggle-popular/', city_views.city_toggle_popular, name='city_toggle_popular'),

    # Blog CRUD
    path('admin/blog/', blog_views.blog_list, name='blog_list'),
    path('admin/blog/create/', blog_views.blog_create, name='blog_create'),
    path('admin/blog/<int:pk>/edit/', blog_views.blog_edit, name='blog_edit'),
    path('admin/blog/<int:pk>/delete/', blog_views.blog_delete, name='blog_delete'),
    path('admin/blog/<int:pk>/', blog_views.blog_detail, name='blog_detail'),
    path('admin/blog/<int:pk>/status/', blog_views.blog_status_update, name='blog_status_update'),
    path('admin/blog/<int:pk>/feature/', blog_views.blog_feature_toggle, name='blog_feature_toggle'),

    # Customer Messages
    path('admin/messages/', message_views.message_list, name='message_list'),
    path('admin/messages/customer/<int:customer_id>/', message_views.message_thread, name='message_thread'),
    path('admin/messages/send/<int:customer_id>/', message_views.message_send, name='message_send'),
    path('admin/messages/<int:message_id>/mark-read/', message_views.message_mark_read, name='message_mark_read'),
    path('admin/messages/<int:message_id>/delete/', message_views.message_delete, name='message_delete'),

    # Feature Section CRUD
    path('admin/feature-sections/', feature_section_views.feature_section_list, name='feature_section_list'),
    path('admin/feature-sections/create/', feature_section_views.feature_section_create, name='feature_section_create'),
    path('admin/feature-sections/<int:pk>/edit/', feature_section_views.feature_section_edit, name='feature_section_edit'),
    path('admin/feature-sections/<int:pk>/delete/', feature_section_views.feature_section_delete, name='feature_section_delete'),
    path('admin/feature-sections/<int:pk>/tours/', feature_section_views.feature_section_tours, name='feature_section_tours'),
    path('admin/feature-sections/<int:pk>/tours/add/', feature_section_views.feature_section_add_tour, name='feature_section_add_tour'),
    path('admin/feature-sections/<int:pk>/tours/<int:tour_id>/remove/', feature_section_views.feature_section_remove_tour, name='feature_section_remove_tour'),
    path('admin/api/tours/search/', feature_section_views.search_tours_ajax, name='search_tours_ajax'),

    # Website Menu CRUD
    path('admin/website-menus/', website_menu_views.website_menu_list, name='website_menu_list'),
    path('admin/website-menus/create/', website_menu_views.website_menu_create, name='website_menu_create'),
    path('admin/website-menus/<int:pk>/edit/', website_menu_views.website_menu_edit, name='website_menu_edit'),
    path('admin/website-menus/<int:pk>/delete/', website_menu_views.website_menu_delete, name='website_menu_delete'),
    
    # Website SubMenu CRUD
    path('admin/website-menus/<int:menu_id>/submenus/', website_menu_views.website_submenu_list, name='website_submenu_list'),
    path('admin/website-menus/<int:menu_id>/submenus/create/', website_menu_views.website_submenu_create, name='website_submenu_create'),
    path('admin/website-submenus/<int:pk>/edit/', website_menu_views.website_submenu_edit, name='website_submenu_edit'),
    path('admin/website-submenus/<int:pk>/delete/', website_menu_views.website_submenu_delete, name='website_submenu_delete'),

    # FAQ CRUD
    path('admin/faqs/', faq_views.faq_list, name='faq_list'),
    path('admin/faqs/create/', faq_views.faq_create, name='faq_create'),
    path('admin/faqs/<int:pk>/edit/', faq_views.faq_edit, name='faq_edit'),
    path('admin/faqs/<int:pk>/delete/', faq_views.faq_delete, name='faq_delete'),
]

