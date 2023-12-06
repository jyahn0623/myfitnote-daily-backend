# Generated by Django 4.1.2 on 2023-11-25 11:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_alter_client_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientMeasurement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.TextField(blank=True, null=True, verbose_name='횟수')),
                ('grade', models.TextField(blank=True, null=True, verbose_name='등급')),
                ('raw_data', models.TextField(blank=True, null=True, verbose_name='data')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='수행일시')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.client', verbose_name='고객')),
            ],
            options={
                'ordering': ('-pk',),
            },
        ),
    ]