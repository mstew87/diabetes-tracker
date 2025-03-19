from django import forms
from .models import GlucoseReading

class GlucoseReadingForm(forms.ModelForm):
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