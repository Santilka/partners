from django.db.models import Case, IntegerField, Q, When
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Course, CourseSection, Review, Section

HOME_TILES = 8
FEATURED = 6
SEARCH_LIMIT = 60


def random_courses(limit=FEATURED):
    base = Course.objects.filter(is_active=True)
    items = list(base.exclude(tag='').order_by('?')[:limit])
    if len(items) < limit:
        items += list(base.filter(tag='').order_by('?')[:limit - len(items)])
    return items


def home(request):
    sections = (
        Section.objects.filter(is_active=True, category__is_active=True)
        .select_related('category')
        .order_by('category__position', 'category__title', 'position', 'title')
    )
    groups = {}
    for s in sections:
        g = groups.setdefault(s.category_id, {'category': s.category, 'sections': [], 'total': 0})
        g['total'] += 1
        if len(g['sections']) < HOME_TILES:
            g['sections'].append(s)
    return render(request, 'refy/home.html', {
        'groups': list(groups.values()),
        'featured': random_courses(),
    })


def search(request):
    q = request.GET.get('q', '').strip()[:100]
    words = [w for w in q.split() if len(w) > 1][:5]
    courses = []
    if words:
        match_any = Q()
        cases = []
        for w in words:
            m = (
                Q(title__icontains=w) | Q(tag__icontains=w) | Q(school__icontains=w)
                | Q(audience__icontains=w)
                | Q(pk__in=CourseSection.objects.filter(section__title__icontains=w).values('course_id'))
            )
            match_any |= m
            cases.append(Case(When(m, then=1), default=0, output_field=IntegerField()))
        courses = (
            Course.objects.filter(is_active=True).filter(match_any)
            .annotate(score=sum(cases))
            .order_by('-score', 'position', 'title')[:SEARCH_LIMIT]
        )
    return render(request, 'refy/search.html', {'q': q, 'searched': bool(words), 'courses': courses})


def category(request, category_slug):
    obj = Category.objects.filter(slug=category_slug, is_active=True).first()
    if obj is None:
        old = (Section.objects.filter(slug=category_slug, is_active=True, category__is_active=True)
               .select_related('category').first())
        if old:
            return redirect(old.get_absolute_url(), permanent=True)
        raise Http404
    return render(request, 'refy/category.html', {
        'category': obj,
        'sections': obj.sections.filter(is_active=True),
    })


def course_detail(request, slug):
    obj = get_object_or_404(Course, slug=slug, is_active=True)
    link = (obj.course_sections
            .filter(section__is_active=True, section__category__is_active=True)
            .select_related('section__category').first())
    return render(request, 'refy/course.html', {
        'course': obj,
        'parent': link.section if link else None,
        'reviews': obj.reviews.all(),
    })


def section(request, category_slug, slug):
    obj = get_object_or_404(
        Section.objects.select_related('category'),
        slug=slug, category__slug=category_slug,
        category__is_active=True, is_active=True,
    )
    courses = Course.objects.filter(
        course_sections__section=obj,
        is_active=True,
    ).distinct()
    return render(request, 'refy/section.html', {
        'section': obj,
        'courses': courses,
        'reviews': Review.objects.filter(course__in=courses)[:3],
        'faqs': obj.faqs.all(),
    })