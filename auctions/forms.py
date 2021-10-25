from django import forms

from auctions.models import Auction
from .models import *

class AuctionForm(forms.Form):
    class Meta:
        model = Auction
        fields = ['title_item', 'description_item', 'category', 'image_URL', 'start_price', 'durations']

class CommitForm(forms.Form):
    class Meta:
        model = Commit
        fields = ['comment']

class BidForm(forms.Form):
    class Meta:
        model = Bid
        fields = ['price']