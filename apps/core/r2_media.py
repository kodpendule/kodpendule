"""Delete uploaded files from Cloudflare R2 (when USE_R2 is enabled)."""

from __future__ import annotations

import logging

import boto3
from django.conf import settings

logger = logging.getLogger(__name__)


def delete_file_from_r2(file_path: str | None) -> None:
    """Remove one object from the R2 bucket. No-op when R2 is disabled or path is empty."""
    if not getattr(settings, "USE_R2", False) or not file_path:
        return

    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        key = file_path.lstrip("/")
        location = getattr(settings, "AWS_LOCATION", "") or ""
        if location:
            key = f"{location}/{key}"
        s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
        logger.info("Deleted file from R2: %s", key)
    except Exception:
        logger.exception("Error deleting file from R2: %s", file_path)


def delete_model_file_field(file_field) -> None:
    """Delete storage for a FileField/ImageField if it has a stored name."""
    if file_field and getattr(file_field, "name", None):
        delete_file_from_r2(file_field.name)
