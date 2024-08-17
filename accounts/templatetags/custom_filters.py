from django import template

register = template.Library()

@register.filter(name='mask_email')
def mask_email(email):
    try:
        local_part, domain_part = email.split('@')
        masked_local_part = local_part[:3] + '****'
        
        
        return f"{masked_local_part}@{domain_part}"
    except Exception:
        return email  
