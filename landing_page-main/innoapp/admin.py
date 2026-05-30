from django.contrib import admin

from .models import MediaContent, PageContent, SocialLink


@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ("key", "content")
    search_fields = ("key", "content")


@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    list_display = ("key", "image", "video", "youtube_url")
    search_fields = ("key", "youtube_url")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "icon_class")
    search_fields = ("name", "url", "icon_class")
