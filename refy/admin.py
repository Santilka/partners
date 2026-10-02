from django.contrib import admin
from django import forms

from .models import Category, Course, CourseSection, Faq, Review, Section


class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'tag': forms.TextInput(attrs={
                'placeholder': 'Хит, Новинка, Скидка, python, frontend, backend...',
                'style': 'width: 450px;'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Название курса',
                'style': 'width: 550px;'
            }),
            'school': forms.TextInput(attrs={
                'placeholder': 'Название школы / платформы',
                'style': 'width: 450px;'
            }),
            'audience': forms.TextInput(attrs={
                'placeholder': 'Для кого: новички, разработчики...',
                'style': 'width: 450px;'
            }),
            'duration_months': forms.NumberInput(attrs={
                'placeholder': 'Например: 6',
                'style': 'width: 120px;'
            }),
            'duration_days': forms.NumberInput(attrs={
                'placeholder': 'Например: 21',
                'style': 'width: 120px;'
            }),
            'format_note': forms.TextInput(attrs={
                'placeholder': 'с куратором, в записи + вебинары...',
                'style': 'width: 450px;'
            }),
            'document': forms.TextInput(attrs={
                'placeholder': 'Диплом / Сертификат / Удостоверение',
                'style': 'width: 350px;'
            }),
            'price': forms.TextInput(attrs={
                'placeholder': 'от 45 000 ₽ или Бесплатно',
                'style': 'width: 250px;'
            }),
            'rating': forms.NumberInput(attrs={
                'placeholder': '4.8',
                'step': '0.1',
                'style': 'width: 100px;'
            }),
            'reviews_count': forms.NumberInput(attrs={
                'placeholder': '124',
                'style': 'width: 100px;'
            }),
            'details_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
                'style': 'width: 550px;'
            }),
            'school_url': forms.URLInput(attrs={
                'placeholder': 'https://...',
                'style': 'width: 550px;'
            }),
            'position': forms.NumberInput(attrs={
                'placeholder': '0',
                'style': 'width: 80px;'
            }),
        }


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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'position', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'slug', 'position', 'is_active')
    list_filter = ('category', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [FaqInline, CourseSectionInlineForSection]
    search_fields = ('title',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    form = CourseAdminForm
    list_display = ('title', 'school', 'duration_months', 'duration_days', 'is_active')
    list_filter = ('format', 'is_active')
    search_fields = ('title', 'school')
    inlines = [CourseSectionInlineForCourse]


admin.site.register(Review)
admin.site.register(Faq)
admin.site.register(CourseSection)