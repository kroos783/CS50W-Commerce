from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_auction, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("auction/<int:auction_id>", views.auctions, name="auction"),
    path("categories.html", views.categories, name="categories" )
]
