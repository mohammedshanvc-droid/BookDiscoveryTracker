from django.db import models
from django.contrib.auth.models import User


# ==========================================
# READING LIST MODEL
# ==========================================

class ReadingList(models.Model):

    READING_STATUS = [
        ('want_to_read', 'Want to Read'),
        ('currently_reading', 'Currently Reading'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    open_library_id = models.CharField(max_length=100)

    title = models.CharField(max_length=255)

    author = models.CharField(
        max_length=255,
        blank=True
    )

    publish_year = models.IntegerField(
        null=True,
        blank=True
    )

    cover_url = models.URLField(
        max_length=500,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=READING_STATUS,
        default='want_to_read'
    )

    is_favorite = models.BooleanField(default=False)

    date_added = models.DateTimeField(auto_now_add=True)

    date_updated = models.DateTimeField(auto_now=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'open_library_id'],
                name='unique_user_reading_book'
            )
        ]

    def __str__(self):
        return self.title


# ==========================================
# USER PROFILE MODEL
# ==========================================

class Profile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# ==========================================
# READING PROGRESS MODEL
# Saves the user's last reading page
# ==========================================

class ReadingProgress(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='book_reading_progress'
    )

    book_key = models.CharField(max_length=255)

    last_page = models.PositiveIntegerField(default=1)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'book_key'],
                name='unique_reading_progress_per_user'
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.book_key} - "
            f"Page {self.last_page}"
        )