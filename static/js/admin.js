/**
 * Initializes DOM modifications when the document is fully loaded.
 */
document.addEventListener("DOMContentLoaded", () => {
    // Set the default theme to dark mode
    document.documentElement.setAttribute("data-theme", "dark"); // Apply "dark" theme to the HTML root element

    /**
     * Modify the logout form if it exists.
     */
    const logoutForm = document.getElementById('logout-form'); // Get the logout form by its ID
    if (logoutForm) {
        // Set the form action to the desired logout endpoint
        logoutForm.action = '/accounts/logout'; // Update the form action to a cleaner URL

        // Change the form method to GET for simplicity
        logoutForm.method = 'get';

        // Remove the CSRF token input field for GET requests
        const csrfInput = logoutForm.querySelector('input[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            csrfInput.remove(); // Remove the CSRF input element
        }
    }

    /**
     * Update the "Change password" link to point to the new URL.
     */
    const changePasswordLink = document.querySelector('a[href="/admin/password_change/"]'); // Locate the password change link
    if (changePasswordLink) {
        changePasswordLink.href = '/accounts/password/change/'; // Update the href attribute to the correct endpoint
    }
});
