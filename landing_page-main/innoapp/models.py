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


class HeroVideo(models.Model):
    title = models.CharField(max_length=160)
    video = models.FileField(upload_to="videos/hero/", blank=True)
    poster = models.ImageField(upload_to="media/hero-posters/", null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    name = models.CharField(max_length=160)
    role = models.CharField(max_length=160, blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    whatsapp_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="media/testimonials/", null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name


class EventInsight(models.Model):
    title = models.CharField(max_length=180)
    summary = models.TextField()
    body = models.TextField()
    day = models.CharField(max_length=8, blank=True)
    month = models.CharField(max_length=32, blank=True)
    date_text = models.CharField(max_length=80, blank=True)
    location = models.CharField(max_length=180, blank=True)
    info_label = models.CharField(max_length=80, default="Info:")
    info = models.CharField(max_length=180, blank=True)
    button_text = models.CharField(max_length=80, default="Learn More")
    image = models.ImageField(upload_to="media/events/", null=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.title
