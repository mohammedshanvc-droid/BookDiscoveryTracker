
from rest_framework import serializers


class BookSerializer(serializers.Serializer):
    open_library_id = serializers.CharField()
    title = serializers.CharField()
    author = serializers.CharField(allow_blank=True, required=False)
    publish_year = serializers.IntegerField(allow_null=True, required=False)
    cover_url = serializers.CharField(allow_blank=True, required=False)
