import logging
from urllib.parse import urlsplit

from django.db.models import Case, Count, IntegerField, OuterRef, Q, Subquery, When
from django.db.models.functions import Coalesce
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from . import seo
from .models import Category, ClickEvent, Course, CourseSection, Review, School, SchoolReview, Section, HeroSlide

HOME_TILES = 8
FEATURED = 6
SEARCH_LIMIT = 60
BOT_MARKERS = ('bot', 'crawl', 'spider', 'slurp', 'preview', 'headless')

log = logging.getLogger(__name__)


def with_review_flags(qs):
    return qs.annotate(
        reviews_n=Count('reviews', distinct=True),
        school_reviews_n=Coalesce(Subquery(
            SchoolReview.objects.filter(school__title=OuterRef('school'))
            .order_by().values('school__title').annotate(n=Count('pk')).values('n')[:1]
        ), 0),
        school_slug=Subquery(
            School.objects.filter(title=OuterRef('school'), reviews__isnull=False).values('slug')[:1]
        ),
    )


def random_courses(limit=FEATURED):
    base = with_review_flags(Course.objects.filter(is_active=True))
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
        'hero_slides': HeroSlide.objects.filter(is_active=True),
        'seo': seo.page(
            request,
            'Каталог курсов: цены, отзывы, сравнение',
            'Честный каталог курсов по разным направлениям: цены, отзывы студентов и практика в одном месте.',
        ),
    })


def search(request):
    q = request.GET.get('q', '').replace('\x00', '').strip()[:100]
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
            with_review_flags(Course.objects.filter(is_active=True)).filter(match_any)
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
        'seo': seo.page(
            request,
            f'{obj.seo_title or obj.title} — каталог курсов',
            obj.seo_description or obj.summary or f'{obj.title}: направления, курсы, цены и отзывы студентов.',
            seo.crumbs(request, (obj.title, obj.get_absolute_url())),
        ),
    })


def course_detail(request, slug):
    obj = get_object_or_404(Course, slug=slug, is_active=True)
    link = (obj.course_sections
            .filter(section__is_active=True, section__category__is_active=True)
            .select_related('section__category').first())
    school_obj = School.objects.filter(title=obj.school).first()
    chain = []
    if link:
        s = link.section
        chain = [(s.category.title, s.category.get_absolute_url()), (s.title, s.get_absolute_url())]
    chain.append((obj.title, obj.get_absolute_url()))
    facts = ', '.join(x for x in (obj.duration_display, obj.get_format_display().lower(), obj.price) if x)
    desc = (f'{obj.title} от {obj.school}' + (f': {facts}' if facts else '')
            + '. Отзывы студентов и условия обучения.')
    return render(request, 'refy/course.html', {
        'course': obj,
        'parent': link.section if link else None,
        'reviews': obj.reviews.all(),
        'school_obj': school_obj,
        'school_reviews_n': school_obj.reviews.count() if school_obj else 0,
        'seo': seo.page(
            request,
            f'{obj.title} — {obj.school}: цена и отзывы',
            desc,
            seo.crumbs(request, *chain),
            seo.course(request, obj, desc, school_obj),
            image=obj.image,
        ),
    })


def school_detail(request, slug):
    obj = get_object_or_404(School, slug=slug)
    courses = with_review_flags(Course.objects.filter(is_active=True, school=obj.title))
    return render(request, 'refy/school.html', {
        'school': obj,
        'courses': courses,
        'reviews': obj.reviews.all(),
        'seo': seo.page(
            request,
            f'{obj.title} — курсы и отзывы',
            f'Курсы школы {obj.title}: цены, длительность, формат обучения и отзывы студентов.',
            seo.crumbs(request, (obj.title, obj.get_absolute_url())),
            seo.school(request, obj),
        ),
    })


def section(request, category_slug, slug):
    obj = get_object_or_404(
        Section.objects.select_related('category'),
        slug=slug, category__slug=category_slug,
        category__is_active=True, is_active=True,
    )
    base = Course.objects.filter(
        course_sections__section=obj,
        is_active=True,
    ).distinct()
    courses = list(with_review_flags(base))
    faqs = list(obj.faqs.all())
    nodes = [seo.crumbs(request, (obj.category.title, obj.category.get_absolute_url()),
                        (obj.title, obj.get_absolute_url()))]
    if courses:
        nodes.append(seo.item_list(request, courses))
    if faqs:
        nodes.append(seo.faq(faqs))
    return render(request, 'refy/section.html', {
        'section': obj,
        'courses': courses,
        'reviews': Review.objects.filter(course__in=base)[:3],
        'faqs': faqs,
        'seo': seo.page(
            request,
            f'{obj.seo_title or obj.title} — каталог курсов',
            obj.seo_description or obj.summary or f'{obj.title}: сравнение курсов, цены и отзывы студентов.',
            *nodes,
        ),
    })


def go(request, pk):
    obj = get_object_or_404(Course, pk=pk, is_active=True)
    if not obj.details_url:
        raise Http404
    if request.method == 'GET':
        ua = request.META.get('HTTP_USER_AGENT', '')
        ref = request.META.get('HTTP_REFERER', '')
        human = (
            bool(ua)
            and not any(b in ua.lower() for b in BOT_MARKERS)
            and request.COOKIES.get('hv') == '1'
            and urlsplit(ref).netloc == request.get_host()
        )
        try:
            ClickEvent.objects.create(
                course=obj,
                url=obj.details_url,
                source=ref[:300],
                user_agent=ua[:255],
                is_bot=not human,
            )
        except Exception:
            log.exception('click log failed')
    return HttpResponseRedirect(obj.details_url)


def robots(request):
    lines = [
        'User-agent: *', 'Disallow: /go/', 'Disallow: /search/',
        f"Sitemap: https://{request.get_host()}{reverse('refy:sitemap')}",
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain')