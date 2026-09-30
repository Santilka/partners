from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Review, Section


def home(request):
    sections = Section.objects.filter(is_active=True).annotate(
        n=Count('courses', filter=Q(courses__is_active=True))
    )
    return render(request, 'refy/home.html', {'sections': sections})


def section(request, slug):
    obj = get_object_or_404(Section, slug=slug, is_active=True)
    courses = obj.courses.filter(is_active=True)
    return render(request, 'refy/section.html', {
        'section': obj,
        'courses': courses,
        'reviews': Review.objects.filter(course__in=courses)[:3],
        'faqs': obj.faqs.all(),
    })
