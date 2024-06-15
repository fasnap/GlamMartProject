from django import forms
from . models import Coupons
class CouponApplyForm(forms.ModelForm):
    class Meta:
        model = Coupons
        fields = ['code', 'coupon_name', 'discount', 'valid_from', 'valid_to']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'coupon_name': forms.TextInput(attrs={'class': 'form-control'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control'}),
            'valid_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
