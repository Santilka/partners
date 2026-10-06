from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

RESERVED_SLUGS = {'search', 'kursy', 'shkoly', 'go'}


class Category(models.Model):
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
        verbose_name = 'Главный раздел'
        verbose_name_plural = 'Главные разделы'

    def __str__(self):
        return self.title

    def clean(self):
        if self.slug in RESERVED_SLUGS:
            raise ValidationError({'slug': 'Этот адрес зарезервирован'})

    def get_absolute_url(self):
        return reverse('refy:category', args=[self.slug])


class Section(models.Model):
    category = models.ForeignKey(Category, related_name='sections', null=True,
                                 on_delete=models.PROTECT,
                                 verbose_name='Главный раздел')
    title = models.CharField('Название', max_length=120)
    slug = models.SlugField(unique=True)
    summary = models.CharField('Краткое описание', max_length=200, blank=True)
    icon = models.FileField('Иконка', upload_to='refy/icons/', blank=True)
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
        if self.category_id:
            return reverse('refy:section', args=[self.category.slug, self.slug])
        return reverse('refy:home')


class School(models.Model):
    title = models.CharField('Название', max_length=120, unique=True)
    slug = models.SlugField('Адрес страницы', max_length=120, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'Школа'
        verbose_name_plural = 'Школы'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._old_title = self.title

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        old = self._old_title
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f'shkola-{self.pk}'
            super().save(update_fields=['slug'])
        if old and old != self.title:
            Course.objects.filter(school=old).update(school=self.title)
        self._old_title = self.title

    def get_absolute_url(self):
        return reverse('refy:school', args=[self.slug]) if self.slug else ''


class SchoolReview(models.Model):
    school = models.ForeignKey(School, related_name='reviews',
                               on_delete=models.CASCADE, verbose_name='Школа')
    author = models.CharField('Автор', max_length=120)
    text = models.TextField('Текст отзыва')

    class Meta:
        verbose_name = 'Отзыв о школе'
        verbose_name_plural = 'Отзывы о школах'

    def __str__(self):
        return self.author


class Course(models.Model):
    FORMATS = [('online', 'Онлайн'), ('webinar', 'Вебинар'), ('hybrid', 'Гибрид (онлайн + вебинар)')]

    tag = models.CharField('Тег', max_length=60, blank=True)
    title = models.CharField('Название', max_length=200)
    image = models.FileField('Картинка', upload_to='refy/courses/', blank=True)
    slug = models.SlugField('Адрес страницы', max_length=200, unique=True, null=True, blank=True)
    school = models.CharField('Школа', max_length=120)
    audience = models.CharField('Аудитория', max_length=120, blank=True)
    duration_months = models.PositiveSmallIntegerField('Продолжительность (месяцы)', null=True, blank=True)
    duration_days = models.PositiveSmallIntegerField('Продолжительность (дни)', null=True, blank=True)
    format = models.CharField('Формат', max_length=10, choices=FORMATS, default='online')
    format_note = models.CharField("Примечание к формату", max_length=80, blank=True)
    document = models.CharField('Выдаваемый Документ', max_length=60, blank=True)
    price = models.CharField('Цена', max_length=60, blank=True)
    installment = models.BooleanField('Рассрочка', default=False)
    rating = models.DecimalField('Рейтинг', max_digits=2, decimal_places=1, null=True, blank=True)
    details_url = models.URLField('Ссылка на детали', blank=True)
    position = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        ordering = ['position', 'title']
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f'kurs-{self.pk}'
            super().save(update_fields=['slug'])

    def get_absolute_url(self):
        return reverse('refy:course', args=[self.slug]) if self.slug else ''

    @property
    def is_online(self):
        return self.format == 'online'

    @property
    def has_diploma(self):
        return 'диплом' in self.document.lower()

    def clean(self):
        if bool(self.duration_months) == bool(self.duration_days):
            raise ValidationError('Укажите длительность либо в месяцах, либо в днях.')

    @property
    def duration_display(self):
        if self.duration_months:
            return f'{self.duration_months} мес.'
        if self.duration_days:
            return f'{self.duration_days} дн.'
        return ''

    @property
    def is_short(self):
        if self.duration_months:
            return self.duration_months <= 6
        if self.duration_days:
            return self.duration_days <= 180
        return False


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

class HeroSlide(models.Model):
    title = models.CharField('Название (для админки)', max_length=120, blank=True)
    html = models.TextField(
        'HTML + CSS',
        blank=True,
        help_text='HTML и CSS работают. &lt;script&gt; из админки не сработает — JS только в slider.js.',
    )
    image = models.FileField(
        'Картинка',
        upload_to='refy/slider/',
        blank=True,
        help_text=
                'ⓘ Рекомендуемый размер: 1920 × 720 px (пропорция 8:3), JPG/WebP, до 300–400 КБ. <br>'
                'Подойдут исходники: 1920×720, 2560×960, 3840×1440 (8:3) — идеально; <br>'
                '1920×1080, 2560×1440, 3840×2160 (16:9) — обрежутся сверху/снизу; <br>'
                '2400×1600, 3000×2000 (3:2) — обрежутся по краям. <br>'
                'Не подойдут: вертикальные (9:16), квадратные (1:1), меньше 1440 px по ширине. <br>'
                'Важное размещайте в центре кадра — верх и низ могут обрезаться.<br>'
                'https://bulkresizephotos.com/ — бесплатный онлайн-ресайзер, можно обрезать и сжать картинку.',
    )
    alt = models.CharField(
        'Alt картинки',
        max_length=160,
        blank=True,
        help_text=
                'Краткое описание картинки (1 фраза). '
                'Для декоративного фона можно оставить пустым. '
                'Для SEO и скринридеров лучше заполнять.'
    )
    link_url = models.URLField('Ссылка (кнопка)', blank=True)
    link_text = models.CharField('Текст кнопки', max_length=60, blank=True)
    position = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['position', 'id']
        verbose_name = 'Слайд (hero)'
        verbose_name_plural = 'Слайды (hero)'

    def __str__(self):
        return self.title or f'Слайд {self.pk}'

class ClickEvent(models.Model):
    course = models.ForeignKey(Course, related_name='clicks', null=True, blank=True,
                               on_delete=models.SET_NULL, verbose_name='Курс')
    url = models.URLField('Ссылка', max_length=500)
    source = models.CharField('Страница', max_length=300, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    is_bot = models.BooleanField('Бот', default=False)
    created_at = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['course', 'created_at'])]
        verbose_name = 'Клик'
        verbose_name_plural = 'Клики'

    def __str__(self):
        return f'{self.course_id} · {self.created_at:%Y-%m-%d %H:%M}'