from django.db import models
from django.urls import reverse


class Section(models.Model):
    title = models.CharField('Название', max_length=120)
    slug = models.SlugField(unique=True)
    summary = models.CharField('Краткое описание', max_length=200, blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    seo_text = models.TextField('SEO-текст (HTML)', blank=True)
    position = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['position', 'title']
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('refy:section', args=[self.slug])


class Course(models.Model):
    FORMATS = [('online', 'Онлайн'), ('hybrid', 'Гибрид'), ('offline', 'Очно')]

    tag = models.CharField('Тег', max_length=60, blank=True)
    title = models.CharField('Название', max_length=200)
    school = models.CharField('Школа', max_length=120)
    audience = models.CharField('Аудитория', max_length=120, blank=True)
    duration_months = models.PositiveSmallIntegerField('Продолжительность (месяцы)')
    format = models.CharField('Формат', max_length=10, choices=FORMATS, default='online')
    format_note = models.CharField("Примечание к формату", max_length=80, blank=True)
    document = models.CharField('Выдаваемый Документ', max_length=60, blank=True)
    price = models.CharField('Цена', max_length=60, blank=True)
    installment = models.BooleanField('Рассрочка', default=False)
    rating = models.DecimalField('Рейтинг', max_digits=2, decimal_places=1, null=True, blank=True)
    reviews_count = models.PositiveIntegerField('Количество отзывов', default=0)
    details_url = models.URLField('Ссылка на детали', blank=True)
    school_url = models.URLField('Ссылка на школу', blank=True)
    position = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        ordering = ['position', 'title']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title

    @property
    def is_online(self):
        return self.format == 'online'

    @property
    def has_diploma(self):
        return 'диплом' in self.document.lower()

    @property
    def is_short(self):
        return self.duration_months <= 6


class Review(models.Model):
    course = models.ForeignKey(Course, related_name='reviews',
                                on_delete=models.CASCADE, 
                                verbose_name='Курс')
    author = models.CharField('Автор', max_length=120)
    text = models.TextField('Текст отзыва')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return self.author

class CourseSection(models.Model):
    course = models.ForeignKey(Course, related_name='course_sections', on_delete=models.CASCADE, verbose_name='Курс')
    section = models.ForeignKey(Section, related_name='course_sections', on_delete=models.CASCADE, verbose_name='Раздел')
    position = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        unique_together = ('course', 'section')
        ordering = ['position']
        verbose_name = 'Курс в разделе'
        verbose_name_plural = 'Курсы в разделах'

    def __str__(self):
        return f'{self.course.title} → {self.section.title}'

class Faq(models.Model):
    section = models.ForeignKey(Section, related_name='faqs', 
                                on_delete=models.CASCADE, 
                                verbose_name='Раздел')
    question = models.CharField('Вопрос', max_length=250)
    answer = models.TextField('Ответ')
    position = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['position']
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return self.question
