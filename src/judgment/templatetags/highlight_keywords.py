import re
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name="highlight_search")
def highlight_search(text, search):
    if not search:
        return text
    search = re.split((";"), search)[:-1]
    
    for i in search:
        highlighted = re.sub(i, '<span style="background-color: #FFFF00">{}</span>'.format(i), text, flags=re.IGNORECASE)
        text = highlighted
    return mark_safe(text)