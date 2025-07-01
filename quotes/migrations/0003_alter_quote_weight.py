import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("quotes", "0002_load_initial_quotes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="quote",
            name="weight",
            field=models.PositiveIntegerField(
                default=100,
                help_text="Число от 1 до 1000. Чем выше значение, тем чаще будет выпадать цитата.",
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(1000),
                ],
                verbose_name="Вес",
            ),
        ),
    ]
