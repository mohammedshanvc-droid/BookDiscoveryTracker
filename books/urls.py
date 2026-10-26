
from django.urls import path
from .views import book_search

urlpatterns = [
    path('books/search/', book_search, name='book_search'),
]
