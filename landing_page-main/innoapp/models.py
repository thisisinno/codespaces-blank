from django.db import models


class PageContent(models.Model):
    key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.key or "page-content"


class MediaContent(models.Model):
    key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to="media/", null=True, blank=True)
    video = models.FileField(upload_to="videos/", null=True, blank=True)
    youtube_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.key or "media-content"


class SocialLink(models.Model):
    name = models.CharField(max_length=120, unique=True, null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    icon_class = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.name or "social-link"
