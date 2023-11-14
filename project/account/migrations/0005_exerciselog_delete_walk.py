# Generated by Django 4.1.2 on 2022-12-25 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_walk'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExerciseLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=10, null=True, verbose_name='type')),
                ('user', models.CharField(max_length=50, null=True, verbose_name='user')),
                ('data', models.TextField(verbose_name='data')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='수행일시')),
            ],
        ),
        migrations.DeleteModel(
            name='Walk',
        ),
    ]