from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=200)
    year = models.PositiveIntegerField('Год выпуска', )
    rating = models.IntegerField('Рейтинг на основе отзывов', default=None)
    description = models.TextField('Описание произведения', blank=True)
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанры',
        blank=True,
        null=True,
        help_text='Удерживайте Ctrl для выбора нескольких вариантов',
        on_delete=models.SET_NULL,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категории',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        'api.Title',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    score = models.IntegerField('Оценка',
                                choices=[(i, str(i)) for i in range(1, 11)])
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]

    def __str__(self):
        return self.text[:50]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст комментария')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:50]
