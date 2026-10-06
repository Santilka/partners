from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Category, Course, School, Section


class BaseSitemap(Sitemap):
    protocol = 'https'


class HomeSitemap(BaseSitemap):
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['refy:home']

    def location(self, item):
        return reverse(item)


class CategorySitemap(BaseSitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Category.objects.filter(is_active=True)


class SectionSitemap(BaseSitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        return Section.objects.filter(is_active=True, category__is_active=True).select_related('category')


class CourseSitemap(BaseSitemap):
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return Course.objects.filter(is_active=True, slug__isnull=False)


class SchoolSitemap(BaseSitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return School.objects.filter(slug__isnull=False)


sitemaps = {
    'home': HomeSitemap,
    'categories': CategorySitemap,
    'sections': SectionSitemap,
    'courses': CourseSitemap,
    'schools': SchoolSitemap,
}