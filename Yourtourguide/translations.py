"""
Simple translation dictionary for Django i18n
This is a fallback when gettext tools are not available
"""

TRANSLATIONS = {
    'dk': {
        "What's Our User Says": "Hvad vores bruger siger",
        "Committed to Helping Our Clients Succeed": "Forpligtet til at hjælpe vores kunder med at lykkes",
        "View All": "Se alle",
        "English": "Engelsk",
        "Danish": "Dansk",
    }
}

def get_translation(text, lang='en'):
    """
    Get translation for given text and language
    """
    if lang == 'en':
        return text
    return TRANSLATIONS.get(lang, {}).get(text, text)
