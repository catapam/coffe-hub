import json

# Django imports
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import FileResponse


class Custom404View(TemplateView):
    '''
    Render a custom 404 error page when a page is not found.

    Uses the '404.html' template and returns an HTTP 404 status.
    '''
    template_name = '404.html'

    def get(self, request, *args, **kwargs):
        '''
        Handle GET requests and return the 404 status with the
        custom template.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse: The 404 error page response.
        '''
        response = super().get(request, *args, **kwargs)
        response.status_code = 404
        return response


class Custom401View(TemplateView):
    '''
    Render a custom 401 error page for unauthorized access.

    Uses the '401.html' template and returns an HTTP 401 status.
    '''
    template_name = '401.html'

    def get(self, request, *args, **kwargs):
        '''
        Handle GET requests and return the 401 status with the
        custom template.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse: The 401 error page response.
        '''
        response = super().get(request, *args, **kwargs)
        response.status_code = 401
        return response


def set_cookie_consent(request):
    '''
    Set a cookie to indicate user consent for cookies.

    Handles POST requests to create the 'cookies_accepted' cookie with
    a max age of 1 year.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    '''
    if request.method == 'POST':
        response = JsonResponse({'success': True})
        response.set_cookie(
            'cookies_accepted',
            'true',
            max_age=31536000,  # 1 year
            samesite='Lax',  # Options: Lax, Strict, None
            secure=True  # Ensures the cookie is only sent over HTTPS
        )
        return response
    return JsonResponse({'success': False}, status=400)


def reset_cookie_consent(request):
    '''
    Reset the user's cookie consent by deleting the cookie.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON response confirming cookie reset.
    '''
    response = JsonResponse({
        'success': True, 'message': 'Cookie consent reset!'
    })
    response.delete_cookie('cookies_accepted', path='/')
    return response


@csrf_exempt
def render_toast_template(request):
    '''
    Render a toast message template with the provided context.

    Handles POST requests to dynamically generate toast messages
    using the 'includes/toasts.html' template.

    Args:
        request (HttpRequest): The incoming HTTP request.

    Returns:
        JsonResponse: A JSON response containing the rendered HTML or
                      an error message.
    '''
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', 'Default message')
            type = data.get('type', 'success')
            context = {'message': message, 'type': type}
            html = render_to_string('includes/toasts.html', context)
            return JsonResponse({'html': html}, status=200)
        except Exception as e:
            return JsonResponse(
                {
                    'success': False,
                    'type': 'error',
                    'error': str(e)
                },
                status=500
            )
    return JsonResponse(
        {
            'success': False,
            'type': 'error',
            'error': 'Invalid request method'
        },
        status=405
    )


def robots_txt(request):
    """
    Serve robots.txt from the project root.
    """
    return FileResponse(open('robots.txt', 'rb'), content_type='text/plain')


def sitemap_xml(request):
    """
    Serve sitemap.xml from the project root.
    """
    return FileResponse(open('sitemap.xml', 'rb'), content_type='application/xml')
