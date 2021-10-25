from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORY = (
    ('1', 'Electronique'),
    ('2', 'Vetement'),
    ('3', 'Meubles'),
    ('4', 'Salle de bain'),
    ('5', 'Cuisine'),
    ('6', 'Toy'),
    ('7', 'Autre')
)

DURATIONS = (
    ('1', 'One day'),
    ('3', 'Three days'),
    ('7', 'One week'),
    ('14', 'Two weeks'),
    ('28', 'Four weeks')
)


class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    category = models.CharField(max_length=1, choices=CATEGORY)

    def __str__(self):
        return f"{self.category}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bid")
    time = models.DateTimeField(auto_now_add=True)
    bid = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.user} bid for {self.bid}"

class Commit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commit_user")
    comment = models.CharField(max_length=512)
    time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user}: {self.comment}"

class Auction(models.Model):
    category = models.CharField(max_length=1, choices=CATEGORY)
    title_item = models.CharField(max_length=64)
    description_item = models.CharField(max_length=512)
    image_URL = models.URLField(blank=True)
    durations = models.CharField(max_length=2, choices=DURATIONS)
    closed = models.BooleanField(default=False)
    start_price = models.DecimalField(max_digits=8, decimal_places=2)
    time  = models.DateTimeField(auto_now_add=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    bid = models.ManyToManyField(Bid, blank=True, related_name="bids")
    comments = models.ManyToManyField(Commit, blank=True, related_name="comments")
    
    def __str__(self):
        return f"{self.title_item}"

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Watchlist_user")
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name="auction")