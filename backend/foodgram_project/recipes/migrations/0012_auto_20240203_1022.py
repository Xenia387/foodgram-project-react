# Generated by Django 3.1.4 on 2024-02-03 07:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20240203_1021'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='favorite',
            unique_together=set(),
        ),
    ]