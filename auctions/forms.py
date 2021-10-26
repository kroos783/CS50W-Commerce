from django.forms import ModelForm

from auctions.models import Auction
from .models import *

class AuctionForm(ModelForm):
    class Meta:
        model = Auction
        fields = ['title_item', 'description_item', 'category', 'image_URL', 'start_price', 'durations']

class CommitForm(ModelForm):
    class Meta:
        model = Commit
        fields = ['comment']

class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['bid']