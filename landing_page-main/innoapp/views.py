import json
from xml.sax.saxutils import escape as xml_escape
from urllib.parse import urlparse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.validators import URLValidator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

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


DEFAULT_PAGE_CONTENT = {
    "site_brand": "InnoWorks Studio",
    "site_tagline": "Digital Strategy & Growth",
    "nav_home": "Home",
    "nav_about": "About",
    "nav_gallery": "Gallery",
    "nav_membership": "Client Stories",
    "nav_events": "Insights",
    "nav_contact": "Contact",
    "nav_pages": "Pages",
    "login_button": "Login",
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
    "hero_video_eyebrow": "Featured Videos",
    "hero_video_heading": "Watch Our Work in Action",
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
    "gallery_section_eyebrow": "Project Gallery",
    "gallery_section_title": "Explore Our Digital Work",
    "gallery_section_subtitle": "A modern view of services, systems, and customer-focused improvements delivered for growing teams.",
    "gallery_empty": "No gallery items yet. Add your first gallery item from admin.",
    "gallery_add_button": "Add Gallery Item",
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
    "floating_contact_button": "Contact Us",
    "floating_contact_title": "How can we help?",
    "floating_contact_subtitle": "Send your details and our team will contact you shortly.",
    "floating_contact_name": "Your Name",
    "floating_contact_phone": "Phone Number",
    "floating_contact_email": "Email Address",
    "floating_contact_message": "How can we help you?",
    "floating_contact_submit": "Send Request",
    "floating_contact_success": "Thank you. Your message has been received.",
    "seo_site_name": "InnoWorks Studio",
    "seo_default_title": "InnoWorks Studio | Digital Strategy & Growth",
    "seo_default_description": "InnoWorks Studio helps growing teams build trusted websites, digital workflows, customer inquiry systems, and practical content strategies.",
    "seo_default_keywords": "digital strategy, business website, landing page, customer inquiries, web design, automation, Dar es Salaam",
    "seo_author": "InnoWorks Studio",
    "seo_og_type": "website",
    "seo_twitter_card": "summary_large_image",
    "seo_theme_color": "#3D405B",
    "seo_robots": "index, follow",
    "social_empty": "No social links configured.",
    "listing_page_title": "Insights & Updates",
    "listing_page_cta": "Explore Insights",
    "listing_featured_title": "Featured Work",
    "listing_upcoming_title": "Latest Business Insights",
    "detail_page_title": "Insight Detail",
    "detail_page_cta": "Learn More",
    "detail_section_title": "Digital growth system for service teams",
    "detail_intro_title": "Clear websites, faster follow-up, better customer journeys",
    "detail_intro_body": "This featured insight shows how a focused digital improvement plan can help a business replace scattered tools with a landing page, lead capture flow, and simple reporting rhythm.",
    "detail_intro_body_two": "Use this page to explain a signature service, client result, workshop, or announcement. Staff can edit every visible block without changing template code.",
    "detail_info_title": "Project Detail",
    "detail_date_label": "Date:",
    "detail_location_label": "Location:",
    "detail_info_label": "Info:",
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

DEFAULT_MEDIA = {}

DEFAULT_HERO_VIDEOS = [
    {
        "title": "Digital systems overview",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "title": "Client workflow walkthrough",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "title": "Analytics review demo",
        "sort_order": 3,
        "is_active": True,
    },
]

DEFAULT_TESTIMONIALS = [
    {
        "name": "Amina Carter",
        "role": "Operations Director",
        "quote": "InnoWorks rebuilt our landing page and connected every inquiry to a simple follow-up workflow. We started replying faster and booking better-fit consultations within the first month.",
        "rating": 5,
        "whatsapp_url": "https://wa.me/255700000000",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "name": "Peter Mwangi",
        "role": "Founder",
        "quote": "The team made our services easy to understand online. The new content, forms, and WhatsApp calls-to-action gave customers a much clearer path to contact us.",
        "rating": 5,
        "whatsapp_url": "https://wa.me/255700000001",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "name": "Sarah Bennett",
        "role": "Managing Partner",
        "quote": "They handled the details we never had time for: page copy, images, analytics, and lead routing. The site finally feels current and useful.",
        "rating": 5,
        "whatsapp_url": "https://wa.me/255700000002",
        "sort_order": 3,
        "is_active": True,
    },
]

DEFAULT_EVENTS = [
    {
        "title": "Conversion audit package",
        "summary": "A focused review of your homepage, forms, analytics, and follow-up flow with a prioritized action list.",
        "body": "Our conversion audit gives growing service teams a practical plan for improving the pages and follow-up steps that turn visitors into qualified conversations. We review message clarity, form friction, analytics visibility, mobile experience, and response workflows.",
        "day": "24",
        "month": "Jan 2026",
        "date_text": "24 Jan 2026",
        "location": "Online consultation",
        "info_label": "Info:",
        "info": "Limited monthly slots",
        "button_text": "Learn More",
        "sort_order": 1,
        "is_featured": True,
        "is_active": True,
    },
    {
        "title": "CRM cleanup sprint",
        "summary": "A two-week sprint to organize contacts, lead stages, automated replies, and team visibility.",
        "body": "This sprint helps teams regain control of messy customer data. We simplify lead stages, remove duplicate noise, set up useful reminders, and make sure every new inquiry has a clear next step.",
        "day": "28",
        "month": "Jan 2026",
        "date_text": "28 Jan 2026",
        "location": "Remote delivery",
        "info_label": "Info:",
        "info": "Two-week sprint",
        "button_text": "Learn More",
        "sort_order": 2,
        "is_featured": True,
        "is_active": True,
    },
    {
        "title": "Local search content refresh",
        "summary": "A business-ready content refresh for service pages, FAQs, and stronger local discovery.",
        "body": "We update your most important service content so prospects can quickly understand what you do, who you help, and how to contact you. The work includes page copy, structured FAQs, and practical calls-to-action.",
        "day": "03",
        "month": "Feb 2026",
        "date_text": "03 Feb 2026",
        "location": "Remote delivery",
        "info_label": "Info:",
        "info": "Content package",
        "button_text": "View Detail",
        "sort_order": 3,
        "is_featured": False,
        "is_active": True,
    },
]

DEFAULT_GALLERY_ITEMS = [
    {
        "title": "Website Experience Design",
        "subtitle": "Clean pages that help visitors understand and act quickly.",
        "description": "A modern landing page layout focused on trust, speed, mobile usability, and clear calls-to-action.",
        "category": "Design",
        "sort_order": 1,
        "is_featured": True,
        "is_active": True,
    },
    {
        "title": "Digital Workflow Setup",
        "subtitle": "Simple systems for capturing and following up with customer inquiries.",
        "description": "We help teams connect forms, WhatsApp actions, email notifications, and organized lead tracking.",
        "category": "Automation",
        "sort_order": 2,
        "is_featured": True,
        "is_active": True,
    },
    {
        "title": "Content Refresh",
        "subtitle": "Sharper words, better structure, and stronger service presentation.",
        "description": "Service pages, updates, and business profiles are arranged to help customers trust the company faster.",
        "category": "Content",
        "sort_order": 3,
        "is_featured": False,
        "is_active": True,
    },
    {
        "title": "Customer Support Channels",
        "subtitle": "Make it easy for people to contact the business from any device.",
        "description": "Floating contact buttons, WhatsApp links, and inquiry forms help visitors reach the right team quickly.",
        "category": "Support",
        "sort_order": 4,
        "is_featured": False,
        "is_active": True,
    },
]

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
VIDEO_KEYS = set()
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/ogg", "video/quicktime"}
TEXT_MODEL_FIELDS = {
    "testimonial": (Testimonial, {"name", "role", "quote", "whatsapp_url"}),
    "event": (EventInsight, {"title", "summary", "body", "day", "month", "date_text", "location", "info_label", "info", "button_text"}),
    "hero_video": (HeroVideo, {"title"}),
    "gallery": (GalleryItem, {"title", "subtitle", "description", "category"}),
}
IMAGE_MODEL_FIELDS = {
    "testimonial": (Testimonial, {"image"}),
    "event": (EventInsight, {"image"}),
    "hero_video": (HeroVideo, {"poster"}),
    "gallery": (GalleryItem, {"image"}),
}
VIDEO_MODEL_FIELDS = {
    "hero_video": (HeroVideo, {"video"}),
}


def _safe_external_url(url, fallback):
    parsed = urlparse(url or "")
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url
    return fallback


def _media_payload(instance):
    return {
        "image_url": instance.image.url if instance and instance.image else "",
        "video_url": instance.video.url if instance and instance.video else "",
        "youtube_url": "",
        "youtube_embed_url": "",
    }


def _ensure_defaults():
    for key, value in DEFAULT_PAGE_CONTENT.items():
        item, created = PageContent.objects.get_or_create(key=key, defaults={"content": value})
        if not created and key == "login_button" and item.content == "Admin Login":
            item.content = value
            item.save(update_fields=["content"])
            continue
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
    for item in DEFAULT_HERO_VIDEOS:
        HeroVideo.objects.get_or_create(sort_order=item["sort_order"], defaults=item)
    if not Testimonial.objects.exists():
        for item in DEFAULT_TESTIMONIALS:
            Testimonial.objects.create(**item)
    if not EventInsight.objects.exists():
        for item in DEFAULT_EVENTS:
            EventInsight.objects.create(**item)
    if not GalleryItem.objects.exists():
        for item in DEFAULT_GALLERY_ITEMS:
            GalleryItem.objects.create(**item)


def _shared_context(request):
    _ensure_defaults()
    content_dict = {item.key: item.content for item in PageContent.objects.all()}
    media_dict = {item.key: _media_payload(item) for item in MediaContent.objects.all()}
    events = EventInsight.objects.filter(is_active=True).order_by("sort_order", "id")
    featured_events = events.filter(is_featured=True)
    gallery_items = GalleryItem.objects.filter(is_active=True).order_by("sort_order", "id")
    if request.user.is_staff:
        customer_inquiries = CustomerInquiry.objects.all().order_by("-created_at")[:20]
        unread_inquiry_count = CustomerInquiry.objects.filter(status=CustomerInquiry.STATUS_NEW).count()
    else:
        customer_inquiries = []
        unread_inquiry_count = 0
    return {
        "content": content_dict,
        "media": media_dict,
        "socials": SocialLink.objects.all().order_by("id"),
        "is_edit_mode": request.user.is_staff,
        "site_url": request.build_absolute_uri("/").rstrip("/"),
        "canonical_url": request.build_absolute_uri(request.path),
        "hero_words": [word.strip() for word in content_dict.get("hero_rotating_words", "Reliable|Professional|Trusted").split("|") if word.strip()],
        "hero_videos": HeroVideo.objects.filter(is_active=True).order_by("sort_order", "id"),
        "testimonials": Testimonial.objects.filter(is_active=True).order_by("sort_order", "id"),
        "events": events,
        "featured_events": featured_events,
        "detail_event": events.first(),
        "gallery_items": gallery_items,
        "featured_gallery_items": gallery_items.filter(is_featured=True),
        "customer_inquiries": customer_inquiries,
        "unread_inquiry_count": unread_inquiry_count,
    }


def _staff_required(request):
    if not request.user.is_staff:
        return JsonResponse({"error": "Forbidden"}, status=403)
    return None


def _model_instance(model_name, object_id, registry, field_name):
    model_config = registry.get(model_name)
    if not model_config:
        return None, JsonResponse({"error": "Invalid editable item."}, status=400)
    model_class, allowed_fields = model_config
    if field_name not in allowed_fields:
        return None, JsonResponse({"error": "Invalid editable field."}, status=400)
    return get_object_or_404(model_class, id=object_id), None


def homepage(request):
    return render(request, "index.html", _shared_context(request))


def details(request):
    context = _shared_context(request)
    context["active_page"] = "detail"
    return render(request, "event-detail.html", context)


def event_list(request):
    context = _shared_context(request)
    context["active_page"] = "listing"
    return render(request, "event-listing.html", context)


@require_GET
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


@require_GET
def sitemap_xml(request):
    site_url = request.build_absolute_uri("/").rstrip("/")
    urls = [
        {"loc": f"{site_url}/", "priority": "1.0"},
        {"loc": f"{site_url}/list/", "priority": "0.8"},
        {"loc": f"{site_url}/details/", "priority": "0.7"},
    ]

    xml_items = []
    for item in urls:
        loc = xml_escape(item["loc"])
        priority = xml_escape(item["priority"])
        xml_items.append(
            f"<url><loc>{loc}</loc><changefreq>weekly</changefreq><priority>{priority}</priority></url>"
        )

    xml = '<?xml version="1.0" encoding="UTF-8"?>'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += "".join(xml_items)
    xml += "</urlset>"
    return HttpResponse(xml, content_type="application/xml")


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
    model_name = payload.get("model")
    object_id = payload.get("id")
    field_name = payload.get("field")
    if model_name or object_id or field_name:
        value = payload.get("content", "")
        instance, error = _model_instance(model_name, object_id, TEXT_MODEL_FIELDS, field_name)
        if error:
            return error
        setattr(instance, field_name, value)
        instance.save(update_fields=[field_name])
        return JsonResponse({
            "success": True,
            "model": model_name,
            "id": object_id,
            "field": field_name,
            "content": value,
        })

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
    model_name = request.POST.get("model")
    object_id = request.POST.get("id")
    field_name = request.POST.get("field")
    file = request.FILES.get("file")
    if model_name or object_id or field_name:
        if not file or file.content_type not in ALLOWED_IMAGE_TYPES:
            return JsonResponse({"error": "Unsupported image type."}, status=400)
        instance, error = _model_instance(model_name, object_id, IMAGE_MODEL_FIELDS, field_name)
        if error:
            return error
        setattr(instance, field_name, file)
        instance.save(update_fields=[field_name])
        image_field = getattr(instance, field_name)
        return JsonResponse({
            "success": True,
            "model": model_name,
            "id": object_id,
            "field": field_name,
            "image_url": image_field.url,
        })

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
    model_name = request.POST.get("model")
    object_id = request.POST.get("id")
    field_name = request.POST.get("field")
    gallery_key = request.POST.get("gallery_key")
    file = request.FILES.get("file")
    files = request.FILES.getlist("files")
    if gallery_key == "hero_video_gallery":
        uploaded_files = files or ([file] if file else [])
        if not uploaded_files:
            return JsonResponse({"error": "Choose at least one video file."}, status=400)
        if any(item.content_type not in ALLOWED_VIDEO_TYPES for item in uploaded_files):
            return JsonResponse({"error": "Unsupported video type."}, status=400)

        last_order = HeroVideo.objects.order_by("-sort_order", "-id").values_list("sort_order", flat=True).first() or 0
        videos = []
        for index, uploaded_file in enumerate(uploaded_files, start=1):
            title = uploaded_file.name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").strip() or "Featured Video"
            item = HeroVideo.objects.create(
                title=title[:160],
                video=uploaded_file,
                sort_order=last_order + index,
                is_active=True,
            )
            videos.append({
                "id": item.id,
                "title": item.title,
                "video_url": item.video.url,
                "sort_order": item.sort_order,
            })
        return JsonResponse({"success": True, "gallery_key": gallery_key, "videos": videos})

    if model_name or object_id or field_name:
        if not file or file.content_type not in ALLOWED_VIDEO_TYPES:
            return JsonResponse({"error": "Unsupported video type."}, status=400)
        instance, error = _model_instance(model_name, object_id, VIDEO_MODEL_FIELDS, field_name)
        if error:
            return error
        setattr(instance, field_name, file)
        instance.save(update_fields=[field_name])
        video_field = getattr(instance, field_name)
        return JsonResponse({
            "success": True,
            "model": model_name,
            "id": object_id,
            "field": field_name,
            "video_url": video_field.url,
        })

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
    return JsonResponse({"error": "Video URLs are disabled. Upload a video file instead."}, status=400)


@require_POST
def create_gallery_item(request):
    staff_error = _staff_required(request)
    if staff_error:
        return staff_error

    last_order = GalleryItem.objects.order_by("-sort_order", "-id").values_list("sort_order", flat=True).first() or 0
    item = GalleryItem.objects.create(
        title="New Gallery Item",
        subtitle="Add a short subtitle for this gallery item.",
        description="Describe this work, service, or project clearly so visitors understand its value.",
        category="Featured",
        sort_order=last_order + 1,
        is_active=True,
    )

    return JsonResponse({
        "success": True,
        "id": item.id,
        "message": "Gallery item created.",
    })


@require_POST
def submit_inquiry(request):
    name = (request.POST.get("name") or "").strip()
    phone = (request.POST.get("phone") or "").strip()
    email = (request.POST.get("email") or "").strip()
    message = (request.POST.get("message") or "").strip()

    if not name:
        return JsonResponse({"error": "Please enter your name."}, status=400)

    if not phone and not email:
        return JsonResponse({"error": "Please enter phone or email so we can contact you."}, status=400)

    if not message:
        return JsonResponse({"error": "Please write your message."}, status=400)

    inquiry = CustomerInquiry.objects.create(
        name=name,
        phone=phone,
        email=email,
        message=message,
        source="Floating Contact Form",
    )

    return JsonResponse({
        "success": True,
        "message": "Thank you. Your message has been received.",
        "id": inquiry.id,
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
