# Generated by Django 4.1.2 on 2022-11-05 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FinnhubSupportedExchanges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exchange_code', models.CharField(max_length=4, null=True, unique=True)),
                ('exchange_name', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('exchange_timezone', models.CharField(blank=True, max_length=100, null=True)),
                ('exchange_open_time', models.TimeField()),
            ],
        ),
    ]
