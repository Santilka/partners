from django.contrib import admin

from .models import Course, Faq, Review, Section


class FaqInline(admin.TabularInline):
    model = Faq
    extra = 1


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'position', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FaqInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'school', 'duration_months', 'is_active')
    list_filter = ('section', 'format', 'is_active')
    search_fields = ('title', 'school')


admin.site.register(Review)
admin.site.register(Faq)
