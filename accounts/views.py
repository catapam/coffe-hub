from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.generic.base import RedirectView
from .forms import UpdateUsernameForm
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login


class CustomLoginView(LoginView):
    """
    Custom login view to handle redirecting the user to the previous page
    if they directly accessed the login page and provided valid credentials.
    """
    template_name = 'accounts/allauth/account/login.html'
    redirect_authenticated_user = True  # Automatically redirect logged-in users
    next_page = reverse_lazy('home')  # Default redirect after successful login

    def form_valid(self, form):
        """
        If the form is valid, log the user in and redirect them.
        """
        # Log the user in
        login(self.request, form.get_user())

        # Check if a previous page was stored in the session
        previous_page = self.request.session.pop('previous_page', None)

        # Redirect to the previous page if available; otherwise, default to `next_page`
        if previous_page:
            return redirect(previous_page)
        else:
            return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests. Capture the previous page for direct login requests.
        """
        if 'next' not in request.GET:
            # Capture the HTTP_REFERER as the previous page, if available
            previous_page = request.META.get('HTTP_REFERER')
            if previous_page and previous_page != request.build_absolute_uri(reverse_lazy('account_login')):
                request.session['previous_page'] = previous_page

        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        """
        Determine the URL to redirect to after login.
        """
        # Default to the next parameter or `next_page`
        return self.get_redirect_url() or self.next_page


@method_decorator(login_required, name='dispatch')
class UpdateUsernameView(FormView):
    """
    View for updating the username of the currently logged-in user.
    Requires the user to be logged in and provides success or error messages
    based on the form submission.
    """

    # Define the template that will be used to render the form
    template_name = 'accounts/allauth/account/update_username.html'

    # Use the UpdateUsernameForm to handle the form logic
    form_class = UpdateUsernameForm

    # Redirect the user to the dashboard after successful form submission
    success_url = reverse_lazy('account_user')

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests (form submissions).
        Checks if the form is valid. If valid, calls form_valid(),
        otherwise form_invalid().
        """
        form = self.get_form()  # Get the form instance
        if form.is_valid():
            # If the form is valid, process it
            return self.form_valid(form)
        else:
            # If the form is invalid, handle the errors
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        """
        Override the get_form method to bind the form to the current user
        instance.

        This ensures that the form updates the logged-in user's username.
        """
        if self.request.method == 'POST':
            # Bind the form to POST data and the current user instance
            return self.form_class(
                self.request.POST,
                instance=self.request.user
                    )
        # Bind the form only to the current user instance for GET requests
        return self.form_class(instance=self.request.user)

    def form_valid(self, form):
        """
        Handle valid form submissions.
        Save the form and display a success message.
        """
        form.save()  # Save the updated username
        # Add a success message to display to the user after updating username
        messages.success(
            self.request,
            'Your username has been updated successfully!'
                )
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Handle invalid form submissions.
        Display an error message and re-render the form.
        """
        # Add an error message to inform the user about the submission failure
        messages.error(
            self.request,
            'There was an error updating your username. Please try again.'
                )
        return super().form_invalid(form)


@method_decorator(login_required, name='dispatch')
class RedirectUserView(RedirectView):
    """
    Class-based view to redirect the user to the update username page.
    Ensures that only logged-in users can access this redirect.
    """
    pattern_name = 'account_user'  # Redirects to the URL pattern

    def get_redirect_url(self, *args, **kwargs):
        """
        Return the URL to redirect to.
        """
        return super().get_redirect_url(*args, **kwargs)