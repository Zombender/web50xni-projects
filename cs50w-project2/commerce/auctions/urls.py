from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.HomeListingView.as_view(), name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path('watchlist/', views.WatchlistView.as_view(), name='watchlist'),
    path("listing/create-listing/", views.CreateListingView.as_view(), name='create-listing'),
    path('listing/<int:pk>', views.DetailListingView.as_view(), name='listing'),
    path('listing/<int:pk>/add-bid', views.CreateBidView.as_view(), name='add-bid'),
    path('listing/<int:pk>/edit', views.UpdateListingView.as_view(), name='edit-listing'),
    path('listing/<int:pk>/watchlist', views.toggle_watchlist, name='listing-watchlist-toggle'),
    path('listing/categories', views.CategoryListview.as_view(), name='category'),
    path('listing/category/<int:pk>', views.CategoryListingListView.as_view(), name='listing-category')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
