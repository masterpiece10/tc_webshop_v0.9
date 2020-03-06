from django import forms

from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address 
        fields = [
            'nickname',
            'name',
            'address_type',
            'address_line_1',
            'address_line_2',
            'address_line_3',
            'state',
            'city',
            'zip_code',
            'country',
            
        ]

class AddressChangeForm(forms.ModelForm):
    class Meta:
        model = Address 
        fields = [
            'nickname',
            'name',
            'address_type',
            'address_line_1',
            'address_line_2',
            'address_line_3',
            'state',
            'city',
            'zip_code',
            'country',
        ]


