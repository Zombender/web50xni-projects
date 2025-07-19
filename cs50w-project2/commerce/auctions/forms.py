from django import forms
from .models import Listing, Bid, Comment


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title',
                  'description',
                  'category',
                  'starting_bid',
                  'image',
                  'is_active']

    def clean(self):
        cleaned_data = super().clean()
        starting_bid = cleaned_data.get('starting_bid')
        if starting_bid <=0:
            self.add_error('starting_bid', "Starting Bid can't be less than 0.01")
        return cleaned_data

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        self.listing: Listing = kwargs.pop('listing', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')

        if self.listing:
            current_price = self.listing.current_price
            if amount is not None and amount < current_price:
                self.add_error('amount', f'Bid must be greater than ${current_price}')
        return cleaned_data
