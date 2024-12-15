from django.views.generic import TemplateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
import json
from django.views import View
from django.http import JsonResponse

# Class-based view for handling 404 Not Found error
class Custom404View(TemplateView):
    """
    This view renders a custom 404 error page when the page is not found.
    It uses the '404.html' template and returns an HTTP status code of 404.
    """
    template_name = '404.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the 404 status with the
        custom template.
        """
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


# Class-based view for handling 401 Unauthorized error
class Custom401View(TemplateView):
    """
    This view renders a custom 401 error page when the user is unauthorized.
    It uses the '401.html' template and returns an HTTP status code of 401.
    """
    template_name = '401.html'

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the 401 status with the
        custom template.
        """
        response = super().get(request, *args, **kwargs)
        response.status_code = 401
        return response


def set_cookie_consent(request):
    if request.method == "POST":
        response = JsonResponse({"success": True})
        response.set_cookie(
            "cookies_accepted",
            "true",
            max_age=31536000,  # 1 year
            samesite="Lax",  # Options: Lax, Strict, None
            secure=True  # Ensures the cookie is only sent over HTTPS
        )
        return response
    return JsonResponse({"success": False}, status=400)


def reset_cookie_consent(request):
    response = JsonResponse({"success": True, "message": "Cookie consent reset!"})
    response.delete_cookie("cookies_accepted", path="/")
    return response


@csrf_exempt
def render_toast_template(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            message = data.get("message", "Default message")
            type = data.get("type", "success")  # e.g., success, error, warning
            context = {"message": message, "type": type}
            html = render_to_string("includes/toasts.html", context)
            return JsonResponse({"html": html}, status=200)
        except Exception as e:
            return JsonResponse({"success": False, "type": "error", "error": str(e)}, status=500)
    return JsonResponse({"success": False, "type": "error", "error": "Invalid request method"}, status=405)