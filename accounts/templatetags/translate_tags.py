from django import template

register = template.Library()

# Translation dictionary
TRANSLATIONS = {
    'dk': {
        "What's Our User Says": "Hvad vores bruger siger",
        "Committed to Helping Our Clients Succeed": "Forpligtet til at hjælpe vores kunder med at lykkes",
        "View All": "Se alle",
        "English": "Engelsk",
        "Danish": "Dansk",
    }
}

@register.simple_tag(takes_context=True)
def translate(context, text):
    """
    Custom translation tag that works without gettext
    Usage: {% translate "Text to translate" %}
    """
    current_lang = context.get('current_lang', 'en')
    
    if current_lang == 'en':
        return text
    
    return TRANSLATIONS.get(current_lang, {}).get(text, text)


@register.filter
def trans_field(obj, field_name):
    """
    Get translated field from model based on current language
    Usage: {{ object|trans_field:'title' }}
    Will return object.title_dk if language is 'dk', otherwise object.title
    """
    # This will be used in templates where we have access to request
    # For now, just return the base field
    return getattr(obj, field_name, '')
