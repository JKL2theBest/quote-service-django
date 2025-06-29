from django.db import models
from django.core.exceptions import ValidationError

class Source(models.Model):
    """Источник цитаты (фильм, книга и т.д.)."""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название источника"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"


class Quote(models.Model):
    """Цитата."""
    MAX_QUOTES_PER_SOURCE = 3

    text = models.TextField(
        unique=True,
        verbose_name="Текст цитаты"
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name="quotes",
        verbose_name="Источник"
    )
    weight = models.PositiveIntegerField(
        default=100,
        help_text="Чем выше значение, тем чаще будет выпадать цитата.",
        verbose_name="Вес"
    )
    likes = models.PositiveIntegerField(default=0, verbose_name="Лайки")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Дизлайки")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f'"{self.text[:50]}..."'

    def clean(self):
        """
        Метод для валидации на уровне модели.
        """
        if self.pk is None:
            quote_count = Quote.objects.filter(source=self.source).count()
            if quote_count >= self.MAX_QUOTES_PER_SOURCE:
                raise ValidationError(
                    f"Нельзя добавить больше {self.MAX_QUOTES_PER_SOURCE} цитат для одного источника."
                )

    def save(self, *args, **kwargs):
        """Сохранение, всегда с вызовом clean()."""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
        ordering = ['-created_at']