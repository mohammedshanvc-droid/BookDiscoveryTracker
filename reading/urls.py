
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.reader_dashboard, name='reader_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('my-reading-list/', views.reading_view, name='reading'),
    path('history/', views.reading_history_view, name='reading_history'),
    path('favorites/', views.favorite_books_view, name='favorite_books'),
    path('search/', views.search_page, name='search_page'),

    path('read-book/', views.read_book_view, name='read_book'),
    path(
        'save-book-progress/',
        views.save_book_progress,
        name='save_book_progress'
    ),

    path(
    'update-status/<int:book_id>/',
    views.update_status,
    name='update_status'
    ),
    path(
        'toggle-favorite/<int:book_id>/',
        views.toggle_favorite,
        name='toggle_favorite'
    ),
    path(
        'add-search-favorite/',
        views.add_search_favorite,
        name='add_search_favorite'
    ),
    path(
        'remove-book/<int:book_id>/',
        views.remove_book,
        name='remove_book'
    ),

    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='reading/password_reset.html',
            email_template_name='reading/password_reset_email.html',
            subject_template_name='reading/password_reset_subject.txt',
        ),
        name='password_reset'
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='reading/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='reading/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='reading/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
