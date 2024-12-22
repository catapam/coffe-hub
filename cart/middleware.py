from django.shortcuts import redirect

class CartRedirectMiddleware:
    """
    Middleware to handle post-login redirection to the cart choice page.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and 'post_login_redirect' in request.session:
            redirect_url = request.session.pop('post_login_redirect', None)
            if redirect_url:
                return redirect(redirect_url)

        return response


