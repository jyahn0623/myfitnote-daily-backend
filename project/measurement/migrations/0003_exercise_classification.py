# Generated by Django 4.1.2 on 2023-12-12 00:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0002_alter_exercise_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='classification',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='분류'),
        ),
    ]
