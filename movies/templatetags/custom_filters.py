from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Custom filter for multiplying two numbers"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value  # Return original value if error occurs
