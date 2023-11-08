from django.urls import path, include
from . import views

# /api/
urlpatterns = [
    path('products/', views.ProductListCreateAPIView.as_view()),
    path('products/<int:pk>', views.ProductRetrieveUpdateDestroyAPIView.as_view()),

    path('supplier/', views.SupplierListCreateAPIView.as_view()),
    path('supplier/<int:pk>', views.SupplierRetrieveUpdateDestroyAPIView.as_view()),

    path('send_qr/<int:pk>', views.send_qr),
]