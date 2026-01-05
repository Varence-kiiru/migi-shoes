from django import forms
import re
from models_app.models import Address, PaymentMethod


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'street', 'city', 'zip_code']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'street': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ZIP'}),
        }
    
    def clean(self):
        super().clean()
        # Set error class on invalid fields
        for error_field in self.errors:
            self.fields[error_field].widget.attrs.update({'class': 'form-control is-invalid'})


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_type', 'card_num', 'exp_date', 'holder_name', 'card_type', 'mpesa_phone']
        widgets = {
            'payment_type': forms.Select(attrs={'class': 'form-select'}),
            'card_num': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card number'}),
            'exp_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'holder_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name on card'}),
            'card_type': forms.Select(attrs={'class': 'form-select'}),
            'mpesa_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'M-Pesa phone number'}),
        }

    # CVV is a transient field: validate on the form but do NOT save it to the model
    cvv = forms.CharField(
        required=False,
        max_length=4,
        min_length=3,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV', 'autocomplete': 'off'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make CVV required only for card payments
        if self.instance and self.instance.payment_type == 'card':
            self.fields['cvv'].required = True

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')

        # Set error class on invalid fields
        for error_field in self.errors:
            self.fields[error_field].widget.attrs.update({'class': 'form-control is-invalid'})

        # Make CVV required for card payments
        if payment_type == 'card':
            cvv = cleaned_data.get('cvv')
            if not cvv:
                self.add_error('cvv', 'CVV is required for card payments.')
            elif not cvv.isdigit():
                self.add_error('cvv', 'CVV must contain only digits.')
            elif len(cvv) not in (3, 4):
                self.add_error('cvv', 'CVV must be 3 or 4 digits.')

        return cleaned_data

    def clean_cvv(self):
        value = self.cleaned_data.get('cvv', '')
        if value is None:
            value = ''
        value = value.strip()
        # Only validate if payment type is card
        if self.cleaned_data.get('payment_type') == 'card':
            if not value:
                raise forms.ValidationError('CVV is required.')
            if not value.isdigit():
                raise forms.ValidationError('CVV must contain only digits.')
            if len(value) not in (3, 4):
                raise forms.ValidationError('CVV must be 3 or 4 digits.')
        return value



class ContactForm(forms.Form):
    full_name = forms.CharField(
        max_length=255,
        required=True,
        label='Full name',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'})
    )
    email = forms.EmailField(
        required=True,
        label='Email address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@example.com'})
    )
    phone = forms.CharField(
        max_length=13,
        required=True,
        label='Phone number',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0712345678 or +254712345678'})
    )

    ALLOWED_EMAIL_DOMAINS = {
        'gmail.com', 'yahoo.com', 'yahoo.co.uk', 'outlook.com', 'hotmail.com', 'live.com',
        'icloud.com', 'me.com', 'protonmail.com', 'aol.com'
    }

    def clean_email(self):
        value = self.cleaned_data.get('email', '').strip().lower()
        if not value:
            raise forms.ValidationError('Email address is required.')
        try:
            local, domain = value.rsplit('@', 1)
        except ValueError:
            raise forms.ValidationError('Invalid email format.')
        if domain not in self.ALLOWED_EMAIL_DOMAINS:
            raise forms.ValidationError('Please use an email from a major provider (e.g. Gmail, Outlook, Yahoo, iCloud).')
        return value

    def clean_phone(self):
        value = self.cleaned_data.get('phone', '')
        if value is None:
            value = ''
        # Remove all whitespace so users can type spaced numbers
        value = re.sub(r'\s+', '', value).strip()
        if not value:
            raise forms.ValidationError('Phone number is required.')

        # Accept Kenyan phone formats:
        # - 0712345678 (10 digits starting with 07)
        # - +254712345678 (13 digits starting with +254)
        if re.fullmatch(r'07\d{8}', value):
            # Valid Kenyan mobile format (10 digits)
            pass
        elif re.fullmatch(r'\+2547\d{8}', value):
            # Valid international format (13 digits)
            pass
        else:
            raise forms.ValidationError('Phone must be a valid Kenyan number: 0712345678 or +254712345678')

        return value
    
    def clean(self):
        super().clean()
        # Set error class on invalid fields
        for error_field in self.errors:
            self.fields[error_field].widget.attrs.update({'class': 'form-control is-invalid'})
