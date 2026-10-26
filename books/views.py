
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from requests.exceptions import RequestException
from .services import search_books


@api_view(['GET'])
def book_search(request):
    query = request.query_params.get('q', '').strip()

    if not query:
        return Response(
            {'error': 'Please provide a book title or author using the q parameter.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        books = search_books(query)

        return Response({
            'query': query,
            'count': len(books),
            'results': books
        }, status=status.HTTP_200_OK)

    except (RequestException, ValueError):
        return Response(
            {'error': 'Unable to connect to Open Library. Please try again.'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
