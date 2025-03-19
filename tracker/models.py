from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
class GlucoseReading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='glucose_readings')
    timestamp = models.DateTimeField(default=timezone.now)
    glucose_level = models.FloatField(help_text="Glucose level in mg/dL.")
    carbs = models.FloatField(null=True, blank=True, help_text="Carbs consumed in grams.")
    insulin = models.FloatField(null=True, blank=True, help_text="Insulin dose in units.")
    notes = models.TextField(blank=True, help_text="Any additional notes about the reading.")

    FASTING = 'FA'
    BEFORE_BREAKFAST = 'BF'
    AFTER_BREAKFAST = 'AF'
    BEFORE_LUNCH = 'BL'
    AFTER_LUNCH = 'AL'
    BEFORE_DINNER = 'BD'
    AFTER_DINNER = 'AD'
    BEDTIME = 'BT'
    OTHER = 'OT'

    READING_TIME_CHOICES = [
        (FASTING, 'Fasting'),
        (BEFORE_BREAKFAST, 'Before Breakfast'),
        (AFTER_BREAKFAST, 'After Breakfast'),
        (BEFORE_LUNCH, 'Before Lunch'),
        (AFTER_LUNCH, 'After Lunch'),
        (BEFORE_DINNER, 'Before Dinner'),
        (AFTER_DINNER, 'After Dinner'),
        (BEDTIME, 'Bedtime'),
        (OTHER, 'Other'),
    ]

    reading_time = models.CharField(
        max_length=2,
        choices=READING_TIME_CHOICES,
        default=OTHER,
    )

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}'s reading: {self.glucose_level} mg/dL on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"



