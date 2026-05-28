"""
Cloudflare R2 storage backend (S3-compatible API).
"""

from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class R2Storage(S3Boto3Storage):
    """Store uploaded media on R2 with optional public custom domain."""

    location = "media"
    default_acl = "public-read"
    file_overwrite = False

    def url(self, name):
        custom_domain = getattr(settings, "AWS_S3_CUSTOM_DOMAIN", None)
        if custom_domain and custom_domain.strip():
            custom_domain_clean = custom_domain.strip().rstrip("/")
            if not custom_domain_clean.startswith("http"):
                custom_domain_clean = f"https://{custom_domain_clean}"
            file_path = f"{self.location}/{name}".replace("//", "/").lstrip("/")
            return f"{custom_domain_clean}/{file_path}"
        return super().url(name)
