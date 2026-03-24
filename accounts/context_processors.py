from .models import SiteSetting, WebsiteMenu
from datetime import datetime

def site_settings(request):
    """
    Context processor to make site settings available to all templates
    """
    settings = SiteSetting.get_settings()
    website_menus = WebsiteMenu.objects.filter(status='active', section_type='header').prefetch_related('submenus').order_by('rank', '-created_at')

    website_menus_footer = WebsiteMenu.objects.filter(status='active', section_type='footer').prefetch_related('submenus').order_by('rank', '-created_at')
    
    return {
        'site_settings': settings,
        'website_menus': website_menus,
        'website_menus_footer': website_menus_footer
    }

def current_language(request):
    """
    Context processor to make current language available to all templates
    """
    current_lang = 'en'  
    if hasattr(request, 'session'):
        current_lang = request.session.get('lang', 'en')
    return {
        'current_lang': current_lang
    }

def get_current_year(request):
    current_datetime = datetime.now()
    current_year = current_datetime.year    
    return {
        'current_year': current_year
    }
