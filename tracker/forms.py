from django import forms
from .models import GlucoseReading
from django.utils import timezone

class GlucoseReadingForm(forms.ModelForm):
    reading_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control', 
            'type': 'date', 
            'max': timezone.localtime(timezone.now()).strftime('%Y-%m-%d')
        }),
        help_text="Date of reading"
    )
    
    time_of_reading = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={
            'class': 'form-control', 
            'type': 'time'
        }),
        help_text="Clock time when reading was taken"
    )
    
    class Meta:
        model = GlucoseReading
        fields = ['glucose_level', 'carbs', 'insulin', 'reading_time', 'notes']
        widgets = {
            'glucose_level': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Glucose level (mg/dL)'}),
            'carbs': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Carbs consumed (g)'}),
            'insulin': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Insulin dose (units)'}),
            'reading_time': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Any additional notes', 'rows': 3}),
        }
        labels = {
            'reading_time': 'Reading Time Label',
        }
        help_texts = {
            'reading_time': 'What category best describes when this reading was taken?',
        }

    def clean_glucose_level(self):
        glucose_level = self.cleaned_data['glucose_level']
        if glucose_level < 0:
            raise forms.ValidationError("Glucose level cannot be negative.")
        if glucose_level > 500:  # Safety check for extremely high values
            raise forms.ValidationError("Please verify this glucose level. If correct, please add a note.")
        return glucose_level
        
    def clean_carbs(self):
        carbs = self.cleaned_data.get('carbs')
        if carbs is not None and carbs < 0:
            raise forms.ValidationError("Carbs cannot be negative.")
        return carbs
        
    def clean_insulin(self):
        insulin = self.cleaned_data.get('insulin')
        if insulin is not None and insulin < 0:
            raise forms.ValidationError("Insulin dose cannot be negative.")
        return insulin
        
    def clean(self):
        cleaned_data = super().clean()
        reading_date = cleaned_data.get('reading_date')
        time_of_reading = cleaned_data.get('time_of_reading')
        
        # Validate that the timestamp is not in the future
        if reading_date and time_of_reading:
            from datetime import datetime
            from django.utils import timezone
            
            # Combine date and time into a naive datetime
            reading_datetime = datetime.combine(reading_date, time_of_reading)
            
            # Get user's timezone
            current_tz = timezone.get_current_timezone()
            
            # Localize the datetime to user's timezone
            localized_datetime = current_tz.localize(reading_datetime)
            
            # Check if the localized datetime is in the future
            if localized_datetime > timezone.now():
                raise forms.ValidationError("You cannot enter readings from the future.")
                
        return cleaned_data