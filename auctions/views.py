from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import *
from .forms import *


def index(request):
    return render(request, "auctions/index.html", {
        "all_auctions": Auction.objects.filter(closed=False)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_auction(request):
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        form = AuctionForm(request.POST)
        # if form is valid
        if form.is_valid():
            # try save db
            try:
                new_auction = form.save(commit=False)
                new_auction.user = user
                new_auction.save()
            # if integrity Error
            except IntegrityError:
                return render(request, "auctions/create.html", {
                    "form": form,
                    "message": "We were unable to add the auction"
                })
            messages.add_message(request, messages.SUCCESS, "Success! Your auction has been created.")
            return HttpResponseRedirect(reverse("index"))    
        # if form is not valid
        else:
            messages.add_message(request, messages.WARNING, "Something went wrong. Please try again.")
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": AuctionForm()
        })

@login_required
def auctions(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        if request.POST.get("button") == "Watchlist":
            if not user.watchlist.filter(auction=auction):
                watchlist = WatchList()
                watchlist.user = user
                watchlist.auction = auction
                watchlist.save()
            else:
                user.watchlist.filter(auction=auction).delete()
            return HttpResponseRedirect(reverse('auction', args=(auction.id)))
        if not auction.closed:
            if request.POST.get("button") == "close":
                auction.closed = True
                auction.save()
            else:
                price = float(request.POST["bid"])
                bids = auction.bid.all()
                if user.username != auction.user.username:
                    if price <= auction.start_price:
                        return render(request, "auctions/auction.html", {
                            "auction": auction,
                            "form": BidForm(),
                            "message": "Error: invalid bid amount."
                        })
                    form = BidForm(request.POST)
                    if form.is_valid():
                        bid = form.save(commit=False)
                        bid.user = user
                        bid.save()
                        auction.bid.add(bid)
                        auction.start_price = price
                        auction.save()
                    else:
                        return render(request, 'auctions/auction.html', {
                            "form": form
                        })
        return HttpResponseRedirect(reverse('auction', args=(auction.id)))
    else:
        return render(request, "auctions/auction.html", {
            "auction": auction,
            "form": BidForm()
        })                

@login_required
def category(request):
    pass

@login_required
def watchlist(request):
    pass