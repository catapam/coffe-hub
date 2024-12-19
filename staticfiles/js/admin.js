document.addEventListener("DOMContentLoaded", () => {
    document.documentElement.setAttribute("data-theme", "dark");
    const logoutForm = document.getElementById('logout-form'); // Get the form by ID
    if (logoutForm) {
        // Set the desired action and method
        logoutForm.action = '/accounts/logout'; // Set the clean action
        logoutForm.method = 'get'; // Change the method to GET

        // Remove the CSRF token input field
        const csrfInput = logoutForm.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            csrfInput.remove(); // Remove the CSRF input element
        }
    }

    // Update the "Change password" link
    const changePasswordLink = document.querySelector('a[href="/admin/password_change/"]');
    if (changePasswordLink) {
        changePasswordLink.href = '/accounts/password/change/'; // Update the href
    }
});
