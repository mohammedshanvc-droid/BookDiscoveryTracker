
import requests


def search_books(query):
    url = "https://openlibrary.org/search.json"

    params = {
        "q": query,
        "limit": 10
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    books = []

    for item in data.get("docs", []):
        books.append({
            "open_library_id": item.get("key", "").replace("/works/", ""),
            "title": item.get("title", ""),
            "author": ", ".join(item.get("author_name", [])),
            "publish_year": item.get("first_publish_year"),
            "cover_url": (
                f"https://covers.openlibrary.org/b/id/{item['cover_i']}-M.jpg"
                if item.get("cover_i")
                else ""
            )
        })

    return books
