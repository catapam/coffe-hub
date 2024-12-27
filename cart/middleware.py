# Django imports
from django.shortcuts import redirect


class CartRedirectMiddleware:
    """
    Middleware to handle post-login redirection to the cart choice page.
    """
    def __init__(self, get_response):
        """
        Initializes the middleware with the provided response handler.

        Args:
            get_response (function): The next middleware or view in the chain.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Processes the incoming request and checks for post-login redirection.

        Args:
            request (HttpRequest): The HTTP request being processed.

        Returns:
            HttpResponse: The response after handling the post-login
            redirection.
        """
        response = self.get_response(request)

        if (
            request.user.is_authenticated and
            'post_login_redirect' in request.session
        ):
            redirect_url = request.session.pop('post_login_redirect', None)
            if redirect_url:
                return redirect(redirect_url)

        return response
