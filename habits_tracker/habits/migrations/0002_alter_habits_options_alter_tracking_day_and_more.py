# Generated by Django 4.1 on 2022-08-16 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='habits',
            options={'verbose_name': 'Привычка', 'verbose_name_plural': 'Привычки'},
        ),
        migrations.AlterField(
            model_name='tracking',
            name='day',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='tracking',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='Завершено'),
        ),
    ]
