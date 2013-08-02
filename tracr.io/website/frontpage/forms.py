from django import forms

class EmailSubscriptionForm(forms.Form):
  email = forms.EmailField(max_length=256,
                           required=True,
                           label='Leave Your Email')

