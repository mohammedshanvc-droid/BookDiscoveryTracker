

# Register your models here.

from django.contrib import admin
from .models import ReadingList


@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_year', 'status', 'date_added')
    list_filter = ('status',)
    search_fields = ('title', 'author')



