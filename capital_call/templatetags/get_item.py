from django import template
register = template.Library()


@register.filter
def get_item(obj, key):
    """
    Template tag to return a given key dynamically from a dictionary or an object
    """
    val = None
    if obj and type(obj) == dict:
        val = obj.get(key)
    elif obj and hasattr(obj, key):
        val = getattr(obj, key)
    val = val or ''
    return val
