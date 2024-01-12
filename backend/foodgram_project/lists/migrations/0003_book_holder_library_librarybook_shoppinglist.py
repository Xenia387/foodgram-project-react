# Generated by Django 3.2.16 on 2024-01-04 08:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodgram', '0029_auto_20231227_1516'),
        ('lists', '0002_auto_20231226_2135'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Holder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256, unique=True)),
                ('holder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='libraries', to='lists.holder')),
            ],
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('ingredients', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_in_ingredient', to='foodgram.ingredient', verbose_name='Ингредиенты рецепта')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredient_in_recipe', to='foodgram.recipe', verbose_name='Рецепт в корзине')),
            ],
            options={
                'verbose_name_plural': 'Список покупок',
            },
        ),
        migrations.CreateModel(
            name='LibraryBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveSmallIntegerField(default=0)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='libraries_in_book', to='lists.book')),
                ('library', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='books_in_library', to='lists.library')),
            ],
        ),
    ]
