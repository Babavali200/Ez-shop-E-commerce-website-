from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    """
    Form for sellers to create or update their products.
    """
    class Meta:
        model = Product
        fields = [
            'category', 
            'name', 
            'description', 
            'price', 
            'discount_price', 
            'color', 
            'image', 
            'stock'
        ]
        
        # Adding some basic widgets to make the form look better
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01'}),
            'discount_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
