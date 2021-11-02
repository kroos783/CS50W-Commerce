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


@login_required(login_url="/login")
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
            messages.add_message(request, messages.SUCCESS, "Success! Your auction has been created.", extra_tags="alert alert-success")
            return HttpResponseRedirect(reverse("index"))    
        # if form is not valid
        else:
            messages.add_message(request, messages.WARNING, "Something went wrong. Please try again.", extra_tags="alert alert-danger")
            return render(request, "auctions/create.html", {
                "form": form
            })
    else:
        return render(request, "auctions/create.html", {
            "form": AuctionForm()
        })


@login_required(login_url="/login")
def auctions(request, auction_id):
    auction = Auction.objects.get(id=auction_id)
    if request.method == "POST":
        user = User.objects.get(username=request.user)
        if request.POST.get("button") == "Watchlist":
            if not user.Watchlist_user.filter(auction=auction):
                watchlist = WatchList()
                watchlist.user = user
                watchlist.auction = auction
                watchlist.save()
                messages.add_message(request, messages.SUCCESS, "This auction has been added in your watchlist.", extra_tags="alert alert-success")
            else:
                user.Watchlist_user.filter(auction=auction).delete()
                messages.add_message(request, messages.SUCCESS, "This auction has been deleted to your watchlist.", extra_tags="alert alert-danger")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        if request.POST.get("button") == "Comment":
            form = CommitForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.user = user
                comment.save()
                auction.comments.add(comment)
                auction.save()
                messages.add_message(request, messages.SUCCESS, "Your comment has been added.", extra_tags="alert alert-success")
            return HttpResponseRedirect(request.META['HTTP_REFERER'])
        if not auction.closed:
            if request.POST.get("button") == "Close":
                auction.closed = True
                auction.save()
                messages.add_message(request, messages.SUCCESS, "Your auction is now closed.", extra_tags="alert alert-danger")
            else:
                price = float(request.POST["bid"])
                if user.username != auction.user.username:
                    if not auction.bid.exists():
                        if float(price) <= float(auction.start_price):
                            messages.add_message(request, messages.WARNING, "Error: invalid bid amount.", extra_tags="alert alert-danger")
                            return render(request, "auctions/auction.html", {
                                "auction": auction,
                                "formBid": BidForm(),
                                "commitForm": CommitForm()
                            })
                        else:
                            formBid = BidForm(request.POST)
                            if formBid.is_valid():
                                bid = formBid.save(commit=False)
                                bid.user = user
                                bid.save()
                                auction.bid.add(bid)
                                auction.save()
                                messages.add_message(request, messages.SUCCESS, "Your bid is placed.", extra_tags="alert alert-success")
                            else:
                                return render(request, 'auctions/auction.html', {
                                    "formBid": formBid,
                                    "commitForm": CommitForm()
                                })
                    elif float(price) <= float(auction.bid.last().bid):
                            messages.add_message(request, messages.WARNING, "Error: invalid bid amount.", extra_tags="alert alert-danger")
                            return render(request, "auctions/auction.html", {
                                "auction": auction,
                                "formBid": BidForm(),
                                "commitForm": CommitForm()
                            })
                    else:
                        formBid = BidForm(request.POST)
                        if formBid.is_valid():
                            bid = formBid.save(commit=False)
                            bid.user = user
                            bid.save()
                            auction.bid.add(bid)
                            auction.save()
                            messages.add_message(request, messages.SUCCESS, "Your bid is placed.", extra_tags="alert alert-success")
                        else:
                            return render(request, 'auctions/auction.html', {
                                "formBid": formBid,
                                "commitForm": CommitForm()
                            })
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:
        return render(request, "auctions/auction.html", {
            "auction": auction,
            "formBid": BidForm(),
            "commitForm": CommitForm()
        })                

def categories(request):
    if request.POST.get("button") == "Filter":
        category = request.POST["category"]
        auctions = Auction.objects.filter(category=category)
        return render(request, 'auctions/categories.html', {
            "form": AuctionForm(),
            "auctions": auctions
        })
    return render(request, 'auctions/categories.html', {
        "form": AuctionForm()
    })

@login_required(login_url="/login")
def watchlist(request):
    product = WatchList.objects.filter(user=request.user)
    auctions_id = WatchList.objects.values_list('auction', flat=True)
    auctions = Auction.objects.filter(pk__in=auctions_id)
    return render(request, "auctions/watchlist.html", {
        "watchlist": product,
        "auctions": auctions
    })