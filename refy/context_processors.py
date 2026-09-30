from .models import Section


def nav_sections(request):
    return {'nav_sections': Section.objects.filter(is_active=True)[:8]}
