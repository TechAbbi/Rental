from django import forms
from .models import BillDetails


class BillDetailsForm(forms.ModelForm):
    class Meta:
        model = BillDetails
        fields = "__all__"
