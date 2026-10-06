from django.contrib import admin
from django.db.models import Count, Q
from django import forms

from .models import Category, ClickEvent, Course, CourseSection, Faq, Review, School, SchoolReview, Section


class CourseAdminForm(forms.ModelForm):
    school = forms.ChoiceField(label='Школа', help_text='Сначала добавьте школу в разделе «Школы»')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        titles = list(School.objects.values_list('title', flat=True))
        current = self.instance.school if self.instance.pk else ''
        if current and current not in titles:
            titles.append(current)
        self.fields['school'].choices = [('', '---------')] + [(t, t) for t in titles]

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
            'details_url': forms.URLInput(attrs={
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


class ReviewInline(admin.StackedInline):
    model = Review
    extra = 1


class SchoolReviewInline(admin.StackedInline):
    model = SchoolReview
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
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'school', 'duration_months', 'duration_days', 'is_active', 'clicks_total')
    list_filter = ('format', 'is_active')
    search_fields = ('title', 'school')
    inlines = [CourseSectionInlineForCourse, ReviewInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            clicks_n=Count('clicks', filter=Q(clicks__is_bot=False)))

    @admin.display(description='Клики', ordering='clicks_n')
    def clicks_total(self, obj):
        return obj.clicks_n


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'course', 'short_text')
    list_filter = ('course',)
    list_select_related = ('course',)
    search_fields = ('author', 'text', 'course__title')
    autocomplete_fields = ('course',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:80]


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title',)
    inlines = [SchoolReviewInline]


@admin.register(SchoolReview)
class SchoolReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'school', 'short_text')
    list_filter = ('school',)
    list_select_related = ('school',)
    search_fields = ('author', 'text', 'school__title')
    autocomplete_fields = ('school',)

    @admin.display(description='Текст')
    def short_text(self, obj):
        return obj.text[:80]


admin.site.register(Faq)
admin.site.register(CourseSection)


@admin.register(ClickEvent)
class ClickEventAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'course', 'is_bot', 'source')
    list_filter = ('is_bot', 'created_at')
    date_hierarchy = 'created_at'
    list_select_related = ('course',)
    search_fields = ('course__title', 'source')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False