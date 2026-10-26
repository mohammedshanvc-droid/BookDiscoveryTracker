
import json
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import ReadingList, ReadingProgress, Profile


OPEN_LIBRARY_URL = "https://openlibrary.org/search.json"

OPEN_LIBRARY_HEADERS = {
    "User-Agent": "BookTrack/1.0 (educational project)"
}


def _open_library_search(title="", author="", limit=20):
    params = {
        "fields": (
            "key,title,author_name,cover_i,"
            "first_publish_year,ia,ebook_access,"
            "has_fulltext,public_scan_b"
        ),
        "limit": limit,
    }

    if title:
        params["title"] = title

    if author:
        params["author"] = author

    if not title and not author:
        return []

    response = requests.get(
        OPEN_LIBRARY_URL,
        params=params,
        headers=OPEN_LIBRARY_HEADERS,
        timeout=30,
    )
    response.raise_for_status()

    return response.json().get("docs", [])


def _get_cover_url(book):
    cover_id = book.get("cover_i")

    if cover_id:
        return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    return ""


def _get_archive_ids(book):
    archive_ids = book.get("ia") or []

    if isinstance(archive_ids, str):
        archive_ids = [archive_ids]

    return archive_ids


def index_view(request):
    return render(request, "reading/index.html")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("reader_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get(
            "confirm_password",
            request.POST.get("password2", ""),
        )

        if not username or not password:
            messages.error(
                request,
                "Please fill in all required fields.",
            )

        elif User.objects.filter(username=username).exists():
            messages.error(request, "This username already exists.")

        elif email and User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")

        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")

        else:
            try:
                validate_password(password)

            except ValidationError as error:
                for error_message in error.messages:
                    messages.error(request, error_message)

            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

                Profile.objects.get_or_create(user=user)

                messages.success(
                    request,
                    "Account created successfully. Please log in.",
                )
                return redirect("login")

    return render(request, "reading/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("reader_dashboard")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect("reader_dashboard")

        messages.error(request, "Invalid username or password.")

    return render(request, "reading/login.html")


@login_required(login_url="login")
def reader_dashboard(request):
    user_books = ReadingList.objects.filter(user=request.user)

    context = {
        "books": user_books.order_by("-date_added")[:6],
        "total_books": user_books.count(),
        "currently_reading": user_books.filter(
            status="currently_reading"
        ).count(),
        "completed_books": user_books.filter(
            status="completed"
        ).count(),
        "want_to_read": user_books.filter(
            status="want_to_read"
        ).count(),
        "favorite_count": user_books.filter(
            is_favorite=True
        ).count(),
    }

    return render(request, "reading/dashboard.html", context)


@login_required(login_url="login")
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_image = request.FILES.get("profile_image")

        if profile_image:
            profile.profile_image = profile_image
            profile.save()
            messages.success(
                request,
                "Profile image updated successfully.",
            )
        else:
            messages.error(request, "Please select an image.")

        return redirect("profile")

    return render(
        request,
        "reading/profile.html",
        {
            "profile": profile,
            "user_email": request.user.email,
        },
    )


@login_required(login_url="login")
def reading_view(request):
    books = ReadingList.objects.filter(
        user=request.user
    ).order_by("-date_added")

    return render(
        request,
        "reading/reading.html",
        {"books": books},
    )


@login_required(login_url="login")
def favorite_books_view(request):
    books = ReadingList.objects.filter(
        user=request.user,
        is_favorite=True,
    ).order_by("-date_added")

    return render(
        request,
        "reading/favorites.html",
        {"books": books},
    )


@login_required(login_url="login")
def search_page(request):
    query = request.GET.get("q", "").strip()
    books = []
    error = ""

    if query:
        try:
            books = _open_library_search(title=query, limit=20)

            for book in books:
                book["cover_url"] = _get_cover_url(book)
                book["open_library_id"] = book.get("key", "")
                book["author_display"] = ", ".join(
                    book.get("author_name", [])
                ) or "Unknown author"
                book["publish_year"] = book.get("first_publish_year")

                archive_ids = _get_archive_ids(book)
                access = book.get("ebook_access", "")

                book["can_read_online"] = (
                    access == "public" and bool(archive_ids)
                )

                book["reading_url"] = (
                    f"https://archive.org/details/{archive_ids[0]}"
                    if archive_ids
                    else ""
                )

        except requests.RequestException:
            error = (
                "Unable to connect to Open Library. "
                "Check your internet connection and try again."
            )

        except (ValueError, TypeError):
            error = (
                "Open Library returned an unexpected response. "
                "Please try again."
            )

    return render(
        request,
        "reading/search.html",
        {
            "books": books,
            "query": query,
            "error": error,
        },
    )


@login_required(login_url="login")
@require_POST
def update_status(request, book_id):
    book = get_object_or_404(
        ReadingList,
        id=book_id,
        user=request.user,
    )

    new_status = request.POST.get("status", "").strip()

    valid_statuses = {
        "want_to_read",
        "currently_reading",
        "completed",
    }

    if new_status not in valid_statuses:
        messages.error(request, "Invalid reading status.")
        return redirect("reading")

    book.status = new_status

    if new_status == "completed":
        if not book.completed_at:
            book.completed_at = timezone.now()
    else:
        book.completed_at = None

    book.save(
        update_fields=[
            "status",
            "completed_at",
            "date_updated",
        ]
    )

    messages.success(
        request,
        "Reading status updated successfully.",
    )
    return redirect("reading")


@login_required(login_url="login")
@require_POST
def toggle_favorite(request, book_id=None):
    book_id = (
        book_id
        or request.POST.get("book_id")
        or request.POST.get("id")
    )

    book = get_object_or_404(
        ReadingList,
        id=book_id,
        user=request.user,
    )

    book.is_favorite = not book.is_favorite

    book.save(
        update_fields=[
            "is_favorite",
            "date_updated",
        ]
    )

    if book.is_favorite:
        messages.success(
            request,
            f'"{book.title}" added to favorites.',
        )
    else:
        messages.success(
            request,
            f'"{book.title}" removed from favorites.',
        )

    return redirect(request.POST.get("next") or "reading")


@login_required(login_url="login")
@require_POST
def add_search_favorite(request):
    open_library_id = request.POST.get(
        "open_library_id",
        request.POST.get("book_id", ""),
    ).strip()

    title = request.POST.get("title", "").strip()
    author = request.POST.get("author", "").strip()
    cover_url = request.POST.get("cover_url", "").strip()

    year_value = request.POST.get(
        "publish_year",
        request.POST.get("year", ""),
    ).strip()

    if not open_library_id or not title:
        messages.error(request, "Book details are missing.")
        return redirect("search_page")

    if len(open_library_id) > 100:
        messages.error(request, "Invalid book identifier.")
        return redirect("search_page")

    try:
        publish_year = int(year_value) if year_value else None
    except ValueError:
        publish_year = None

    book, created = ReadingList.objects.get_or_create(
        user=request.user,
        open_library_id=open_library_id,
        defaults={
            "title": title[:255],
            "author": author[:255],
            "publish_year": publish_year,
            "cover_url": cover_url[:500],
            "status": "want_to_read",
        },
    )

    if created:
        messages.success(
            request,
            f'"{book.title}" added to your reading list.',
        )
    else:
        messages.info(
            request,
            "This book is already in your reading list.",
        )

    return redirect(request.POST.get("next") or "reading")


@login_required(login_url="login")
@require_POST
def remove_book(request, book_id=None):
    book_id = (
        book_id
        or request.POST.get("book_id")
        or request.POST.get("id")
    )

    book = get_object_or_404(
        ReadingList,
        id=book_id,
        user=request.user,
    )

    book.delete()

    messages.success(
        request,
        "Book removed from your reading list.",
    )

    return redirect("reading")


@login_required(login_url="login")
def reading_history_view(request):
    books = ReadingList.objects.filter(
        user=request.user,
        status="completed",
    ).order_by("-completed_at", "-date_updated")

    progress_items = ReadingProgress.objects.filter(
        user=request.user
    ).order_by("-updated_at")

    return render(
        request,
        "reading/history.html",
        {
            "books": books,
            "progress_items": progress_items,
        },
    )


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def read_book_view(request):
    title = request.GET.get("title", "").strip()[:255]
    author = request.GET.get("author", "").strip()[:255]

    open_library_id = request.GET.get(
        "open_library_id",
        request.GET.get("book_id", ""),
    ).strip()[:100]

    if not title and open_library_id:
        title = open_library_id.rsplit("/", 1)[-1].replace("_", " ")

    if not title:
        messages.error(request, "Please select a book first.")
        return redirect("search_page")

    book_key = open_library_id or (
        "search:" + title.casefold() + "|" + author.casefold()
    )

    progress, _ = ReadingProgress.objects.get_or_create(
        user=request.user,
        book_key=book_key,
    )

    context = {
        "title": title,
        "author": author or "Unknown author",
        "book_key": book_key,
        "last_page": progress.last_page,
        "embed_url": "",
        "reading_url": "",
        "error": "",
        "ebook_access": "",
    }

    try:
        books = _open_library_search(
            title=title,
            author=author,
            limit=50,
        )

        candidates = [
            book for book in books if _get_archive_ids(book)
        ]

        exact_matches = [
            book for book in candidates
            if book.get("title", "").casefold() == title.casefold()
        ]

        if author and exact_matches:
            author_matches = [
                book for book in exact_matches
                if any(
                    author.casefold() in name.casefold()
                    for name in book.get("author_name", [])
                )
            ]

            if author_matches:
                exact_matches = author_matches

        if exact_matches:
            candidates = exact_matches

        priority = {
            "public": 0,
            "borrowable": 1,
            "printdisabled": 2,
            "no_ebook": 3,
        }

        candidates.sort(
            key=lambda book: (
                priority.get(book.get("ebook_access", ""), 4),
                not bool(book.get("public_scan_b")),
                not bool(book.get("has_fulltext")),
            )
        )

        selected = candidates[0] if candidates else None

        if selected:
            context["title"] = selected.get("title", title)
            context["author"] = ", ".join(
                selected.get("author_name", [])
            ) or author or "Unknown author"

            archive_id = _get_archive_ids(selected)[0]
            access = selected.get("ebook_access", "")

            context["ebook_access"] = access
            context["embed_url"] = (
                f"https://archive.org/embed/{archive_id}"
            )
            context["reading_url"] = (
                f"https://archive.org/details/{archive_id}"
            )

            if access == "public":
                context["error"] = ""
            elif access == "borrowable":
                context["error"] = (
                    "This book may require you to sign in "
                    "and borrow it on Internet Archive."
                )
            elif access == "printdisabled":
                context["error"] = (
                    "This edition may have restricted reading access. "
                    "Check Internet Archive for its reading options."
                )
            else:
                context["error"] = (
                    "Full reading access could not be confirmed. "
                    "Check the edition on Internet Archive."
                )

        else:
            context["error"] = (
                "No online reader was found for this book. "
                "Try another edition on Open Library."
            )

            context["reading_url"] = (
                "https://openlibrary.org/search?q="
                + requests.utils.quote(title)
            )

    except requests.RequestException:
        context["error"] = (
            "Unable to connect to Open Library. Please try again."
        )

    except (ValueError, TypeError, KeyError):
        context["error"] = (
            "Open Library returned unexpected book information."
        )

    return render(request, "reading/read_book.html", context)


@login_required(login_url="login")
@require_POST
def save_book_progress(request):
    try:
        data = json.loads(request.body or "{}")

        book_key = str(data.get("book_key", "")).strip()
        page = int(data.get("page", 1))

        if not book_key or len(book_key) > 255:
            return JsonResponse(
                {"error": "Invalid book identifier."},
                status=400,
            )

        if not 1 <= page <= 100000:
            return JsonResponse(
                {"error": "Invalid page number."},
                status=400,
            )

    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse(
            {"error": "Invalid request."},
            status=400,
        )

    progress, _ = ReadingProgress.objects.update_or_create(
        user=request.user,
        book_key=book_key,
        defaults={"last_page": page},
    )

    return JsonResponse({
        "success": True,
        "last_page": progress.last_page,
    })
