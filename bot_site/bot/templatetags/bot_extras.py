from django import template

register = template.Library()


@register.filter
def add_class(value, class_name):
    ret = value.as_widget(attrs={
        "class": " ".join((value.css_classes(), class_name))
    })
    return ret
