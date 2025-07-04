import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Source",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        max_length=255, unique=True, verbose_name="Название источника"
                    ),
                ),
            ],
            options={
                "verbose_name": "Источник",
                "verbose_name_plural": "Источники",
            },
        ),
        migrations.CreateModel(
            name="Quote",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("text", models.TextField(unique=True, verbose_name="Текст цитаты")),
                (
                    "weight",
                    models.PositiveIntegerField(
                        default=100,
                        help_text="Чем выше значение, тем чаще будет выпадать цитата.",
                        verbose_name="Вес",
                    ),
                ),
                ("likes", models.PositiveIntegerField(default=0, verbose_name="Лайки")),
                (
                    "dislikes",
                    models.PositiveIntegerField(default=0, verbose_name="Дизлайки"),
                ),
                (
                    "views",
                    models.PositiveIntegerField(default=0, verbose_name="Просмотры"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "source",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="quotes",
                        to="quotes.source",
                        verbose_name="Источник",
                    ),
                ),
            ],
            options={
                "verbose_name": "Цитата",
                "verbose_name_plural": "Цитаты",
                "ordering": ["-created_at"],
            },
        ),
    ]
