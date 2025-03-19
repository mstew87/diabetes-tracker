# Generated by Django 5.1.7 on 2025-03-19 04:45

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GlucoseReading',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('glucose_level', models.FloatField(help_text='Glucose level in mg/dL.')),
                ('carbs', models.FloatField(blank=True, help_text='Carbs consumed in grams.', null=True)),
                ('insulin', models.FloatField(blank=True, help_text='Insulin dose in units.', null=True)),
                ('notes', models.TextField(blank=True, help_text='Any additional notes about the reading.')),
                ('reading_time', models.CharField(choices=[('FA', 'Fasting'), ('BF', 'Before Breakfast'), ('AF', 'After Breakfast'), ('BL', 'Before Lunch'), ('AL', 'After Lunch'), ('BD', 'Before Dinner'), ('AD', 'After Dinner'), ('BT', 'Bedtime'), ('OT', 'Other')], default='OT', max_length=2)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='glucose_readings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
