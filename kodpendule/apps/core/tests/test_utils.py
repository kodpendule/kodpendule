from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware


def apply_request_middleware(request, *, language: str = "sr") -> None:
    """Attach session, auth, messages, and locale to a RequestFactory request."""
    request.META.setdefault("HTTP_ACCEPT_LANGUAGE", language)
    session_middleware = SessionMiddleware(lambda req: None)
    session_middleware.process_request(request)
    request.session.save()
    locale_middleware = LocaleMiddleware(lambda req: None)
    locale_middleware.process_request(request)
    auth_middleware = AuthenticationMiddleware(lambda req: None)
    auth_middleware.process_request(request)
    message_middleware = MessageMiddleware(lambda req: None)
    message_middleware.process_request(request)
