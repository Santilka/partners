from django import template

register = template.Library()


@register.filter
def ru_plural(n, forms):
    one, few, many = forms.split(',')
    n = abs(int(n))
    if 11 <= n % 100 <= 14:
        return many
    if n % 10 == 1:
        return one
    if 2 <= n % 10 <= 4:
        return few
    return many