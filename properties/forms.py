from django import forms

class Propertiesform(forms.Form):
    from django import forms

class PropertyForm(forms.Form):
    PROPERTY_TYPE_CHOICES = [
        ('House', 'House'),
        ('Apartment', 'Apartment'),
    ]

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'placeholder': 'Property Title'}),
        label="Property Title"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Description of the property'}),
        label="Property Description"
    )
    price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'placeholder': 'Price in EURO'}),
        label="Price"
    )
    property_type = forms.ChoiceField(
        choices=PROPERTY_TYPE_CHOICES,
        widget=forms.Select(),
        label="Type of Property"
    )
    location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Location'}),
        label="Location"
    )
    bedrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Number of Bedrooms'}),
        label="Bedrooms"
    )
    bathrooms = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Number of Bathrooms'}),
        label="Bathrooms"
    )
    area = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'Area in square feet'}),
        label="Area (sq ft)"
    )
    image = forms.ImageField(
        required=False,
        label="Property Image"
    )
