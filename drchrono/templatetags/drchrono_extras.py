from django import template    
register = template.Library()    

@register.filter('timestamp_to_time')
def convert_timestamp_to_time(timestamp):
    import datetime
    # ISO 8601 specific
    return datetime.datetime.strptime( timestamp, "%Y-%m-%dT%H:%M:%S" )
