# Generated by Django 3.2.16 on 2024-01-10 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0031_alter_ingredientrecipe_recipe'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lists', '0010_auto_20240108_2141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='recipe',
            field=models.ForeignKey(help_text='Вы можете добавить этот рецепт в избранное', on_delete=django.db.models.deletion.CASCADE, related_name='recipe_in_favorite', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_favorite', to=settings.AUTH_USER_MODEL, verbose_name='Вы'),
        ),
    ]
