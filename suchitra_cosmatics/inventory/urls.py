from django.urls import path
from .views import ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView

app_name = 'inventory'

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/add/', ProductCreateView.as_view(), name='product-create'),
    path('products/<slug:slug>/edit/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<slug:slug>/delete/', ProductDeleteView.as_view(), name='product-delete'),
]