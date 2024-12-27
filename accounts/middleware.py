# Django imports
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.urls import resolve, reverse
from django.shortcuts import redirect
from django.contrib.auth import REDIRECT_FIELD_NAME


class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Middleware to ensure that users are authenticated before accessing
    specific parts of the application, such as the admin panel
    and operations.

    Handles redirects for login and unauthorized access based
    on user permissions.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Process each view to enforce authentication and authorization rules.
        Redirects users to login or 401 pages when necessary.

        Args:
            request: The current request object.
            view_func: The view function being accessed.
            view_args: Positional arguments for the view.
            view_kwargs: Keyword arguments for the view.

        Returns:
            None or HttpResponse: Returns a redirect or forbidden response
            based on user authentication and authorization status.
        """
        current_url = resolve(request.path_info).url_name

        # Check if the user is not authenticated
        if not request.user.is_authenticated:
            # Allow access to certain URLs without authentication
            allowed_urls = [
                'account_login', 'account_signup', 'account_reset_password',
                'home', 'about', 'privacy_policy', 'product', 'product_detail',
                'product_list', 'custom_401', 'custom_404', 'wireframes',
                'account_reset_password_done', 'help',
                'account_reset_password_from_key',
                'account_confirm_email', 'account_verified_email_required',
                'account_email_verification_sent', 'cart', 'add_to_cart',
                'render_toast', 'validate_data', 'delete_cart', 'update_cart',
                'set_cookie_consent', 'reset_cookie_consent',
                'webhook', 'cache_checkout_data',
            ]

            if current_url not in allowed_urls:
                # Redirect due to middleware restriction
                messages.warning(request, 'Please log in to continue.')
                return redirect(
                    f'{reverse("account_login")}?{REDIRECT_FIELD_NAME}='
                    f'{request.get_full_path()}'
                )
            elif current_url == 'account_login' and 'next' not in request.GET:
                # Direct request to login page, capture the referring page
                previous_page = request.META.get('HTTP_REFERER', '/')
                if (
                    previous_page and previous_page !=
                    request.build_absolute_uri(reverse('account_login'))
                ):
                    request.session['previous_page'] = previous_page

        # Enforce superuser access for the admin panel
        elif request.path.startswith(reverse('admin:index')):
            if not request.user.is_authenticated:
                # Redirect unauthenticated users to login
                return redirect(
                    f'{reverse("account_login")}?{REDIRECT_FIELD_NAME}='
                    f'{request.get_full_path()}'
                )
            elif not (request.user.is_superuser or request.user.is_staff):
                # Redirect non-superusers to custom 401 page
                return redirect('custom_401')

        # Allow access if no restrictions are met
        return None
