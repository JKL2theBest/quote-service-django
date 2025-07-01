from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


class Source(models.Model):
    """Источник цитаты (фильм, книга и т.д.)."""

    name = models.CharField(
        max_length=255, unique=True, verbose_name="Название источника"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Источник"
        verbose_name_plural = "Источники"


class QuoteQuerySet(models.QuerySet):
    def update_and_get(self, **kwargs):
        rows_updated = self.update(**kwargs)
        if rows_updated > 0:
            return self.first()
        return None


class Quote(models.Model):
    """Цитата."""
    MAX_QUOTES_PER_SOURCE = 3
    text = models.TextField(unique=True, verbose_name="Текст цитаты")
    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="quotes", verbose_name="Источник"
    )
    weight = models.PositiveIntegerField(
        default=100,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
        help_text="Число от 1 до 1000. Чем выше значение, тем чаще будет выпадать цитата.",
        verbose_name="Вес"
    )
    likes = models.PositiveIntegerField(default=0, verbose_name="Лайки")
    dislikes = models.PositiveIntegerField(default=0, verbose_name="Дизлайки")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    objects = QuoteQuerySet.as_manager()

    def __str__(self):
        return f'"{self.text[:50]}..."'

    def clean(self):
        """
        Метод для валидации на уровне модели.
        """
        if self.pk is None:
            quote_count = Quote.objects.filter(source=self.source).count()
            if quote_count >= self.MAX_QUOTES_PER_SOURCE:
                raise ValidationError(f"Нельзя добавить больше {self.MAX_QUOTES_PER_SOURCE} цитат для одного источника.")

    def save(self, *args, **kwargs):
        """Сохранение, всегда с вызовом clean()."""
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Цитата"
        verbose_name_plural = "Цитаты"
        ordering = ["-created_at"]
