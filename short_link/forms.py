from django import forms
from .models import ShortURL

class ShortURLForm(forms.ModelForm):
    custom_short_code = forms.CharField(
        max_length=20, required=False, help_text="Custom Shortcode (optional)"
    )
    extension = forms.CharField(
        required=False,
    )
    expiry_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        help_text="Enter date and time in YYYY-MM-DDTHH:mm format",
    )  # For link expiry
    password = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.PasswordInput,
        help_text="Password protection (optional)",
    ) 
    accurate_location_tracking = forms.BooleanField(
        required=False,
        initial=False,
        label="Enable Accurate Location Tracking",
        help_text="Allow accurate location tracking when accessing this short URL."
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.password:
            self.fields['password'].widget = forms.TextInput()  # Change widget to TextInput
            self.fields['password'].widget.attrs['value'] = self.instance.password

    custom_note = forms.CharField( 
        required=False,
    )
    class Meta:
        model = ShortURL
        fields = ("original_url", "custom_short_code", "extension", "expiry_date", "password", "custom_note", "accurate_location_tracking")

