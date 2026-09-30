from django.contrib import admin

from .models import Course, CourseSection, Faq, Review, Section


class FaqInline(admin.TabularInline):
    model = Faq
    extra = 1


class CourseSectionInlineForCourse(admin.TabularInline):
    model = CourseSection
    extra = 1
    autocomplete_fields = ('section',)
    fk_name = 'course'


class CourseSectionInlineForSection(admin.TabularInline):
    model = CourseSection
    extra = 1
    autocomplete_fields = ('course',)
    fk_name = 'section'


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'position', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FaqInline, CourseSectionInlineForSection]
    search_fields = ('title',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'school', 'duration_months', 'is_active')
    list_filter = ('format', 'is_active')
    search_fields = ('title', 'school')
    inlines = [CourseSectionInlineForCourse]


admin.site.register(Review)
admin.site.register(Faq)
admin.site.register(CourseSection)