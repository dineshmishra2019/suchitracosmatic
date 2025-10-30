from django import forms
from django.forms import inlineformset_factory
from store.models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'brand', 'name', 'slug', 'description', 'price', 'ingredients', 'how_to_use', 'is_available', 'is_featured']
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'brand': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'slug': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'ingredients': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
            'how_to_use': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 3}),
        }

ProductImageFormSet = inlineformset_factory(
    Product, ProductImage,
    fields=('image', 'is_main_image'),
    extra=1, can_delete=True
)