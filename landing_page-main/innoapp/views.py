import json
from urllib.parse import urlparse, parse_qs

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import URLValidator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import MediaContent, PageContent, SocialLink


DEFAULT_PAGE_CONTENT = {
    "site_brand": "InnoWorks Studio",
    "site_tagline": "Digital Strategy & Growth",
    "nav_home": "Home",
    "nav_about": "About",
    "nav_membership": "Client Stories",
    "nav_events": "Insights",
    "nav_contact": "Contact",
    "nav_pages": "Pages",
    "login_button": "Admin Login",
    "login_title": "Admin Login",
    "login_help": "Use your Django staff credentials to unlock edit mode.",
    "login_username_label": "Username",
    "login_password_label": "Password",
    "login_submit": "Login",
    "login_footer_label": "Need help?",
    "login_footer_value": "hello@innoworks.example",
    "hero_welcome": "Practical digital support for growing teams",
    "hero_title_prefix": "We build",
    "hero_rotating_words": "Websites|Automations|Campaigns",
    "hero_story_cta": "Our Story",
    "hero_member_cta": "Read Client Stories",
    "about_section_title": "About InnoWorks Studio",
    "about_history_title": "Strategy, design, and delivery under one roof",
    "about_history_body": "We help service businesses turn outdated websites, scattered tools, and slow manual processes into clear digital systems that customers can trust.",
    "about_history_body_two": "Our team plans, launches, and maintains conversion-focused pages, CRM workflows, and practical content campaigns without adding complexity to your day.",
    "founder_name": "Maya Johnson",
    "founder_role": "Founder / Strategy Lead",
    "cofounder_name": "Daniel Kim",
    "cofounder_role": "Operations Lead",
    "newsletter_title": "Get growth notes",
    "newsletter_body": "Monthly ideas on improving your website, customer follow-up, and local marketing systems.",
    "newsletter_placeholder": "Work email address",
    "newsletter_button": "Subscribe",
    "testimony_section_title": "What Clients Say",
    "testimony_section_subtitle": "Real feedback from teams that trust InnoWorks Studio.",
    "testimony_one_name": "Amina Carter",
    "testimony_one_contact_label": "Chat on WhatsApp",
    "testimony_one_whatsapp_url": "https://wa.me/255700000000",
    "testimony_one_text": "InnoWorks rebuilt our landing page and connected every inquiry to a simple follow-up workflow. We started replying faster and booking better-fit consultations within the first month.",
    "testimony_one_rating": "Rated 5/5",
    "testimony_two_name": "Peter Mwangi",
    "testimony_two_contact_label": "Chat on WhatsApp",
    "testimony_two_whatsapp_url": "https://wa.me/255700000001",
    "testimony_two_text": "The team made our services easy to understand online. The new content, forms, and WhatsApp calls-to-action gave customers a much clearer path to contact us.",
    "testimony_two_rating": "Rated 5/5",
    "testimony_three_name": "Sarah Bennett",
    "testimony_three_contact_label": "Chat on WhatsApp",
    "testimony_three_whatsapp_url": "https://wa.me/255700000002",
    "testimony_three_text": "They handled the details we never had time for: page copy, images, analytics, and lead routing. The site finally feels current and useful.",
    "testimony_three_rating": "Rated 5/5",
    "events_title": "Latest Insights",
    "event_one_day": "24",
    "event_one_month": "Jan 2026",
    "event_one_title": "New conversion audit package",
    "event_one_body": "Our focused audit reviews your homepage, forms, tracking, and follow-up flow, then gives your team a prioritized action list.",
    "event_one_location_label": "Location:",
    "event_one_location": "Online consultation",
    "event_one_ticket_label": "Info:",
    "event_one_ticket": "Limited monthly slots",
    "event_one_button": "Learn More",
    "event_two_day": "28",
    "event_two_month": "Jan 2026",
    "event_two_title": "CRM cleanup sprint now available",
    "event_two_body": "We organize contact lists, lead statuses, and automated replies so sales teams can see what needs attention next.",
    "event_two_location_label": "Location:",
    "event_two_location": "Remote delivery",
    "event_two_ticket_label": "Info:",
    "event_two_ticket": "Two-week sprint",
    "event_two_button": "Learn More",
    "contact_title": "Start a Project",
    "contact_submit": "Send Message",
    "contact_location": "Innovation House, Dar es Salaam",
    "contact_phone": "+255 700 123 456",
    "contact_email": "hello@innoworks.example",
    "contact_directions": "Directions",
    "footer_join_title": "Studio Hours",
    "footer_weekday_label": "Mon-Fri",
    "footer_weekday_hours": "8:00 AM - 5:00 PM",
    "footer_weekend_label": "Sat-Sun",
    "footer_weekend_hours": "Closed",
    "footer_copyright": "Copyright © 2026 InnoWorks Studio",
    "footer_credit": "Design: TemplateMo. Distributed by ThemeWagon",
    "edit_mode_badge": "EDIT MODE ACTIVE",
    "social_section_title": "Follow Us",
    "logout_button": "Logout",
    "nav_event_listing": "Event Listing",
    "nav_event_detail": "Event Detail",
    "hero_video_placeholder": "No video selected",
    "contact_name_label": "Full Name",
    "contact_email_label": "Email address",
    "contact_message_label": "Message",
    "social_empty": "No social links configured.",
}

GENERIC_DEFAULT_PAGE_CONTENT = {
    "site_brand": "Your Brand",
    "site_tagline": "Your Tagline",
    "nav_membership": "Testimonials",
    "nav_events": "Latest Updates",
    "nav_contact": "Contact Us",
    "login_footer_value": "support@example.com",
    "hero_welcome": "Welcome to Our Website",
    "hero_title_prefix": "We are",
    "hero_rotating_words": "Reliable|Professional|Trusted",
    "hero_member_cta": "Read Testimonials",
    "about_section_title": "About Us",
    "about_history_title": "Who We Are",
    "about_history_body": "Write a short description about your company, mission, and services here.",
    "about_history_body_two": "Use this area to explain why customers should trust your business.",
    "founder_name": "Team Member Name",
    "founder_role": "Founder / Manager",
    "cofounder_name": "Team Member Name",
    "cofounder_role": "Operations Lead",
    "newsletter_title": "Get our newsletter",
    "newsletter_body": "Enter a short message encouraging visitors to subscribe or contact you.",
    "newsletter_placeholder": "Email address",
    "testimony_section_title": "What Our Customers Say",
    "testimony_section_subtitle": "Real feedback from people who trust our services.",
    "testimony_one_name": "Customer Name",
    "testimony_one_text": "Write the customer testimonial here. Explain the experience, service quality, and result.",
    "testimony_two_name": "Customer Name",
    "testimony_two_text": "Share another customer story here so visitors can understand the value you provide.",
    "testimony_three_name": "Customer Name",
    "testimony_three_text": "Use this testimonial to highlight reliability, support, or a successful outcome.",
    "events_title": "Latest Updates",
    "event_one_title": "Service Update",
    "event_one_body": "Write a short update about your latest service, offer, announcement, or business news.",
    "event_one_location": "Your business location",
    "event_one_ticket": "Contact us",
    "event_two_title": "Customer Announcement",
    "event_two_body": "Use this area to share another update, featured service, or useful message for customers.",
    "event_two_location": "Your business location",
    "event_two_ticket": "Contact us",
    "contact_title": "Contact Us",
    "contact_submit": "Submit Form",
    "contact_location": "Your business location",
    "contact_phone": "+255 XXX XXX XXX",
    "contact_email": "info@example.com",
    "footer_join_title": "Business Hours",
    "footer_copyright": "Copyright © 2026 Your Brand",
}

LEGACY_DEFAULT_PAGE_CONTENT = {
    "site_brand": "Tiya",
    "site_tagline": "Golf Club",
    "nav_membership": "Membership",
    "nav_events": "Events",
    "login_footer_value": "contact@tiyaclub.com",
    "hero_welcome": "Welcome to the club",
    "hero_title_prefix": "Tiya is",
    "hero_rotating_words": "Modern|Creative|Lifestyle",
    "hero_member_cta": "Become a member",
    "about_section_title": "About Tiya",
    "about_history_title": "Tiya Club History",
    "about_history_body": "Since 1984, Tiya has been ranked among the top golf destinations in the world. This Bootstrap landing page is now fully powered by a lightweight frontend CMS.",
    "about_history_body_two": "Right-click any highlighted content while signed in as staff to update copy, visuals, or links instantly without a page refresh.",
    "founder_name": "Michael",
    "founder_role": "Founder",
    "cofounder_name": "Sandy",
    "cofounder_role": "Co-Founder",
    "newsletter_body": "Capture emails, refresh promo copy, and swap media directly from the landing page.",
    "events_title": "Upcoming Events",
    "event_one_month": "Feb 2048",
    "event_one_title": "Private activities",
    "event_one_body": "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "event_one_location": "National Center, NYC",
    "event_one_ticket_label": "Ticket:",
    "event_one_ticket": "$250",
    "event_one_button": "Buy Ticket",
    "event_two_month": "Feb 2048",
    "event_two_title": "Group tournament activities",
    "event_two_body": "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "event_two_location": "National Center, NYC",
    "event_two_ticket_label": "Ticket:",
    "event_two_ticket": "$350",
    "event_two_button": "Buy Ticket",
    "contact_title": "Contact Tiya",
    "contact_location": "London, United Kingdom",
    "contact_phone": "(020) 010-020-0340",
    "contact_email": "info@company.com",
    "footer_join_title": "Join Us",
    "footer_weekday_hours": "6:00 AM - 6:00 PM",
    "footer_weekend_hours": "6:30 AM - 8:30 PM",
    "footer_copyright": "Copyright © 2048 Tiya Golf Club",
}

DEFAULT_MEDIA = {
    "hero_video": {"youtube_url": "https://www.youtube.com/watch?v=MGNgbNGOzh8"},
}

DEFAULT_SOCIAL_LINKS = [
    {"name": "Instagram", "url": "https://instagram.com", "icon_class": "bi-instagram"},
    {"name": "Twitter", "url": "https://twitter.com", "icon_class": "bi-twitter"},
    {"name": "WhatsApp", "url": "https://whatsapp.com", "icon_class": "bi-whatsapp"},
]

IMAGE_KEYS = {
    "founder_image",
    "cofounder_image",
    "event_one_image",
    "event_two_image",
    "contact_map",
    "site_logo",
    "testimony_one_image",
    "testimony_two_image",
    "testimony_three_image",
}
VIDEO_KEYS = {"hero_video"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg", "video/quicktime"}


def _youtube_embed_url(url):
    if not url:
        return ""
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        video_id = parsed.path.strip("/")
    else:
        video_id = parse_qs(parsed.query).get("v", [""])[0]
    return f"https://www.youtube.com/embed/{video_id}" if video_id else url


def _safe_external_url(url, fallback):
    parsed = urlparse(url or "")
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url
    return fallback


def _media_payload(instance):
    return {
        "image_url": instance.image.url if instance and instance.image else "",
        "video_url": instance.video.url if instance and instance.video else "",
        "youtube_url": instance.youtube_url if instance else "",
        "youtube_embed_url": _youtube_embed_url(instance.youtube_url if instance else ""),
    }


def _ensure_defaults():
    for key, value in DEFAULT_PAGE_CONTENT.items():
        item, created = PageContent.objects.get_or_create(key=key, defaults={"content": value})
        if not created and item.content in {
            LEGACY_DEFAULT_PAGE_CONTENT.get(key),
            GENERIC_DEFAULT_PAGE_CONTENT.get(key),
        }:
            item.content = value
            item.save(update_fields=["content"])
    for key, value in DEFAULT_MEDIA.items():
        MediaContent.objects.get_or_create(key=key, defaults=value)
    for social in DEFAULT_SOCIAL_LINKS:
        SocialLink.objects.get_or_create(name=social["name"], defaults=social)


def _staff_required(request):
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)
    return None


def homepage(request):
    _ensure_defaults()
    content_dict = {item.key: item.content for item in PageContent.objects.all()}
    media_dict = {item.key: _media_payload(item) for item in MediaContent.objects.all()}
    testimony_links = {
        "one": _safe_external_url(content_dict.get("testimony_one_whatsapp_url"), DEFAULT_PAGE_CONTENT["testimony_one_whatsapp_url"]),
        "two": _safe_external_url(content_dict.get("testimony_two_whatsapp_url"), DEFAULT_PAGE_CONTENT["testimony_two_whatsapp_url"]),
        "three": _safe_external_url(content_dict.get("testimony_three_whatsapp_url"), DEFAULT_PAGE_CONTENT["testimony_three_whatsapp_url"]),
    }
    context = {
        "content": content_dict,
        "media": media_dict,
        "socials": SocialLink.objects.all().order_by("id"),
        "is_edit_mode": request.user.is_staff,
        "testimony_links": testimony_links,
        "hero_words": [word.strip() for word in content_dict.get("hero_rotating_words", "Reliable|Professional|Trusted").split("|") if word.strip()],
    }
    return render(request, "index.html", context)


def details(request):
    return render(request, "event-detail.html")


def event_list(request):
    return render(request, "event-listing.html")


@require_POST
def login_view(request):
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if user is None:
        messages.error(request, "Invalid username or password.")
        return redirect("homepage")
    login(request, user)
    return redirect("homepage")


@require_GET
@login_required
def logout_view(request):
    logout(request)
    return redirect("homepage")


@require_POST
def save_text(request):
    staff_error = _staff_required(request)
    if staff_error:
        return staff_error
    payload = json.loads(request.body.decode("utf-8"))
    key = payload.get("key")
    value = payload.get("content")
    if not key:
        return JsonResponse({"error": "Missing key."}, status=400)
    item, _ = PageContent.objects.get_or_create(key=key)
    item.content = value
    item.save()
    return JsonResponse({"success": True, "key": key, "content": value})


@require_POST
def upload_image(request):
    staff_error = _staff_required(request)
    if staff_error:
        return staff_error
    key = request.POST.get("key")
    file = request.FILES.get("file")
    if not key or key not in IMAGE_KEYS:
        return JsonResponse({"error": "Invalid image key."}, status=400)
    if not file or file.content_type not in ALLOWED_IMAGE_TYPES:
        return JsonResponse({"error": "Unsupported image type."}, status=400)
    item, _ = MediaContent.objects.get_or_create(key=key)
    item.image = file
    item.save()
    return JsonResponse({"success": True, "key": key, "image_url": item.image.url})


@require_POST
def upload_video(request):
    staff_error = _staff_required(request)
    if staff_error:
        return staff_error
    key = request.POST.get("key")
    file = request.FILES.get("file")
    if not key or key not in VIDEO_KEYS:
        return JsonResponse({"error": "Invalid video key."}, status=400)
    if not file or file.content_type not in ALLOWED_VIDEO_TYPES:
        return JsonResponse({"error": "Unsupported video type."}, status=400)
    item, _ = MediaContent.objects.get_or_create(key=key)
    item.video = file
    item.youtube_url = ""
    item.save()
    return JsonResponse({"success": True, "key": key, "video_url": item.video.url})


@require_POST
def update_youtube(request):
    staff_error = _staff_required(request)
    if staff_error:
        return staff_error
    payload = json.loads(request.body.decode("utf-8"))
    key = payload.get("key")
    youtube_url = payload.get("youtube_url")
    if not key or key not in VIDEO_KEYS:
        return JsonResponse({"error": "Invalid video key."}, status=400)
    validator = URLValidator()
    try:
        validator(youtube_url)
    except Exception:
        return JsonResponse({"error": "Invalid YouTube URL."}, status=400)
    item, _ = MediaContent.objects.get_or_create(key=key)
    item.youtube_url = youtube_url
    item.video = None
    item.save()
    return JsonResponse({
        "success": True,
        "key": key,
        "youtube_url": youtube_url,
        "youtube_embed_url": _youtube_embed_url(youtube_url),
    })


@require_POST
def update_social(request):
    staff_error = _staff_required(request)
    if staff_error:
        return staff_error
    payload = json.loads(request.body.decode("utf-8"))
    social_id = payload.get("id")
    if not social_id:
        return JsonResponse({"error": "Missing social id."}, status=400)
    validator = URLValidator()
    url = payload.get("url")
    try:
        validator(url)
    except Exception:
        return JsonResponse({"error": "Invalid social URL."}, status=400)
    social = get_object_or_404(SocialLink, id=social_id)
    social.name = payload.get("name") or social.name
    social.url = url
    social.icon_class = payload.get("icon_class") or social.icon_class
    social.save()
    return JsonResponse({
        "success": True,
        "id": social.id,
        "name": social.name,
        "url": social.url,
        "icon_class": social.icon_class,
    })
