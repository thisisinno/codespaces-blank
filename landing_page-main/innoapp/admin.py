from django.contrib import admin

from .models import (
    CustomerInquiry,
    EventInsight,
    GalleryItem,
    HeroVideo,
    MediaContent,
    PageContent,
    SocialLink,
    Testimonial,
)


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


@admin.register(HeroVideo)
class HeroVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("title",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "rating", "sort_order", "is_active")
    list_editable = ("sort_order", "is_active")
    search_fields = ("name", "role", "quote")


@admin.register(EventInsight)
class EventInsightAdmin(admin.ModelAdmin):
    list_display = ("title", "date_text", "location", "sort_order", "is_featured", "is_active")
    list_editable = ("sort_order", "is_featured", "is_active")
    search_fields = ("title", "summary", "body", "location", "info")


@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "sort_order", "is_featured", "is_active")
    list_editable = ("sort_order", "is_featured", "is_active")
    search_fields = ("title", "subtitle", "description", "category")
    ordering = ("sort_order", "id")


@admin.register(CustomerInquiry)
class CustomerInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "status", "source", "created_at")
    list_filter = ("status", "source", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "phone", "email", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
