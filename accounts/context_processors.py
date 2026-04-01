def theme_context(request):
    theme = "light"

    try:
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            if hasattr(user, "theme_preference") and user.theme_preference:
                theme = user.theme_preference
            elif hasattr(user, "theme") and user.theme:
                theme = user.theme
    except Exception:
        theme = "light"

    return {
        "theme": theme
    }