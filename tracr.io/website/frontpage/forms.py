from django import forms

class EmailSubscriptionForm(forms.Form):
  email = forms.EmailField(max_length=256,
                           required=True,
                           widget=forms.TextInput(
                             attrs={'placeholder': 'Leave Your Email'}))

