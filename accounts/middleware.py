from django.utils.deprecation import MiddlewareMixin


class ThemeMiddleware(MiddlewareMixin):
    """Middleware to handle user theme preference safely."""

    def process_request(self, request):
        request.theme_preference = "light"

        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            request.theme_preference = getattr(user, "theme_preference", "light") or "light"