from django.conf import settings


def site_brand(request):
    return {"site_brand_name": getattr(settings, "SITE_BRAND_NAME", "MarketingHub")}
