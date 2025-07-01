from django.contrib import admin
from .models import Source, Quote


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    """Отображение Source в админ-панели."""

    list_display = ("name", "quote_count")
    search_fields = ("name",)

    def quote_count(self, obj):
        """Поле для отображения количества цитат у источника."""
        return obj.quotes.count()

    quote_count.short_description = "Количество цитат"


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """Отображение Quote в админ-панели."""

    list_display = (
        "short_text",
        "source",
        "weight",
        "likes",
        "dislikes",
        "views",
        "created_at",
    )
    list_filter = ("source", "created_at")
    search_fields = ("text", "source__name")

    readonly_fields = ("likes", "dislikes", "views", "created_at")

    fieldsets = (
        (None, {"fields": ("text", "source", "weight")}),
        (
            "Статистика (нередактируемо)",
            {
                "fields": ("likes", "dislikes", "views", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def short_text(self, obj):
        """Укороченный текст цитаты."""
        return f"{obj.text[:75]}..." if len(obj.text) > 75 else obj.text

    short_text.short_description = "Текст цитаты"
