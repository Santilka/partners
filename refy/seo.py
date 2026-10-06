import json

from django.urls import reverse
from django.utils.safestring import mark_safe

SITE = 'Каталог курсов'


def url(request, path):
    return f'https://{request.get_host()}{path}'


def ld(nodes):
    raw = json.dumps({'@context': 'https://schema.org', '@graph': nodes}, ensure_ascii=False)
    return mark_safe(raw.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026'))


def crumbs(request, *items):
    items = [(SITE, reverse('refy:home'))] + list(items)
    return {'@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': name, 'item': url(request, path)}
        for i, (name, path) in enumerate(items, 1)
    ]}


def course(request, c, description, school=None):
    provider = {'@type': 'Organization', 'name': c.school}
    if school and school.slug:
        provider['url'] = url(request, school.get_absolute_url())
    node = {'@type': 'Course', 'name': c.title, 'description': description,
            'url': url(request, c.get_absolute_url()), 'provider': provider}
    if c.image:
        node['image'] = url(request, c.image.url)
    return node


def school(request, s):
    return {'@type': 'EducationalOrganization', 'name': s.title, 'url': url(request, s.get_absolute_url())}


def item_list(request, courses):
    return {'@type': 'ItemList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'url': url(request, c.get_absolute_url())}
        for i, c in enumerate(courses, 1)
    ]}


def faq(items):
    return {'@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': f.question, 'acceptedAnswer': {'@type': 'Answer', 'text': f.answer}}
        for f in items
    ]}


def page(request, title, description, *nodes, image=None):
    return {
        'title': title,
        'description': description,
        'image': url(request, image.url) if image else '',
        'jsonld': ld(list(nodes)) if nodes else '',
    }