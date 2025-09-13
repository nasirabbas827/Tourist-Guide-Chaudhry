from django import forms
from .models import CustomUser


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = [
            "first_name", "last_name", "nationality", "city", "postal_address",
            "mobile_no", "email", "password", "travel_season", "travel_type",
            "age_range", "budget_range"
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

        return cleaned_data


class LoginForm(forms.Form):
    mobile_no = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)


from django import forms
from .models import UserTravelPlan, Activity

class UserTravelPlanForm(forms.ModelForm):
    class Meta:
        model = UserTravelPlan
        fields = [
            "destination",
            "travel_dates_start",
            "travel_dates_end",
            "accommodation_details",
            "activities",
        ]
        widgets = {
            "travel_dates_start": forms.DateInput(attrs={"type": "date"}),
            "travel_dates_end": forms.DateInput(attrs={"type": "date"}),
            "accommodation_details": forms.Textarea(attrs={"rows": 3}),
            "activities": forms.CheckboxSelectMultiple(),
        }


from django import forms
from .models import ThirdPartyService

class ThirdPartyServiceForm(forms.ModelForm):
    class Meta:
        model = ThirdPartyService
        fields = ["name", "service_type", "contact_url", "destination", "description"]
