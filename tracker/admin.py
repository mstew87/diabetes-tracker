from django.contrib import admin
from .models import GlucoseReading

@admin.register(GlucoseReading)
class GlucoseReadingAdmin(admin.ModelAdmin):
    list_display = ('user', 'timestamp', 'glucose_level', 'insulin', 'carbs', 'reading_time')
    list_filter = ('reading_time', 'user')
    search_fields = ('notes', 'user__username')
    date_hierarchy = 'timestamp'
