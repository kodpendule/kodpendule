"""
Apply Cloudflare R2 media storage from environment variables.

Call from local.py / production.py after base settings are imported.
"""


def configure_r2(module, config) -> None:
    use_r2 = config("USE_R2", default=False, cast=bool)
    module.USE_R2 = use_r2

    if not use_r2:
        return

    installed = list(module.INSTALLED_APPS)
    if "storages" not in installed:
        module.INSTALLED_APPS = [*installed, "storages"]

    module.AWS_ACCESS_KEY_ID = config("R2_ACCESS_KEY_ID", default="")
    module.AWS_SECRET_ACCESS_KEY = config("R2_SECRET_ACCESS_KEY", default="")
    module.AWS_STORAGE_BUCKET_NAME = config("R2_BUCKET_NAME", default="")
    module.AWS_S3_ENDPOINT_URL = config("R2_ENDPOINT_URL", default="")

    custom_domain = config("R2_CUSTOM_DOMAIN", default="")
    if custom_domain:
        module.AWS_S3_CUSTOM_DOMAIN = (
            custom_domain.replace("https://", "").replace("http://", "").rstrip("/")
        )
    else:
        module.AWS_S3_CUSTOM_DOMAIN = None

    module.AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
    module.AWS_DEFAULT_ACL = "public-read"
    module.AWS_LOCATION = "media"
    module.AWS_S3_USE_SSL = True
    module.AWS_S3_VERIFY = True

    storages = dict(getattr(module, "STORAGES", {}))
    storages["default"] = {"BACKEND": "config.storage.R2Storage"}
    module.STORAGES = storages

    if module.AWS_S3_CUSTOM_DOMAIN:
        module.MEDIA_URL = f"https://{module.AWS_S3_CUSTOM_DOMAIN}/{module.AWS_LOCATION}/"
    elif module.AWS_S3_ENDPOINT_URL and module.AWS_STORAGE_BUCKET_NAME:
        module.MEDIA_URL = (
            f"{module.AWS_S3_ENDPOINT_URL.rstrip('/')}/"
            f"{module.AWS_STORAGE_BUCKET_NAME}/{module.AWS_LOCATION}/"
        )
