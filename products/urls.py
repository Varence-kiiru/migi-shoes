from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'products'

urlpatterns = [
    path('search/', views.ShoeListView.as_view(), name='search'),
    path('gender/<str:gender>/', views.ShoeByGenderListView.as_view(), name='by_gender'),
    path('brand/<int:brand_id>/', views.ShoeByBrandListView.as_view(), name='by_brand'),
    path('<int:pk>/', views.ShoeDetailView.as_view(), name='shoe_details'),
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/delete/<int:item_id>/', views.delete_wishlist_item, name='wishlist_delete'),
    path('wishlist/add/<int:shoe_id>/', views.add_wishlist_item, name='wishlist_add'),
    path('review/<int:shoe_id>',views.reviews, name='reviews'),
    path('review/add/<int:shoe_id>',views.add_review, name='add_review'),
    path('review/edit/<int:review_id>/', views.edit_review, name='edit_review'),
]

#Images don't load without this configuration in debug mode:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)