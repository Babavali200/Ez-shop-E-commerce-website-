from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=(
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    ), initial='customer')

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type', 'phone_number', 'address', 'email')
        error_messages = {
            'username': {
                'unique': "This username is already taken. Please try another one.",
            },
            'password_mismatch': "The passwords do not match. Please ensure both passwords are identical.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            # Remove default help text for username to make it cleaner, or customize it
            if field_name == 'username':
                field.help_text = "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
