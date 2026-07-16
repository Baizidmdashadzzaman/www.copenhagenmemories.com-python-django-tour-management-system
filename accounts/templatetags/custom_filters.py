from decimal import Decimal
from django import template

register = template.Library()

@register.filter
def minus(value, arg):
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (TypeError, ValueError):
        return value