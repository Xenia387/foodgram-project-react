# Generated by Django 3.2.16 on 2024-01-08 13:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0030_tagrecipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingred', to='foodgram.recipe', verbose_name='Рецепт'),
        ),
    ]
