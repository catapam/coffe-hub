// Mobile Search Bar Toggle
/**
 * Sets up the toggle functionality for the mobile search bar.
 * Toggles visibility and active states of the search bar when the button is clicked.
 */
function setupMobileSearchToggle() {
    const mobileSearchButton = document.getElementById('mobileSearchButton');
    if (mobileSearchButton) {
        mobileSearchButton.addEventListener('click', function () {
            const searchBar = document.querySelector('.search-bar-container');
            if (searchBar) {
                searchBar.classList.toggle('active'); // Show/hide the search bar
                searchBar.classList.toggle('d-none'); // Ensure it’s not hidden
            }
        });
    }
}

// Menu Item Toggle
/**
 * Sets up toggle functionality for menu items.
 * Ensures only one menu item is active at a time.
 */
function setupMenuItemToggle() {
    const menuItems = document.querySelectorAll('.menu-item');
    if (menuItems.length > 0) {
        menuItems.forEach(item => {
            if (item.id === 'toggle-btn') return;
            item.addEventListener('click', function () {
                if (this.classList.contains('active')) {
                    this.classList.remove('active'); // Deactivate if already active
                } else {
                    menuItems.forEach(i => i.classList.remove('active')); // Deactivate all
                    this.classList.add('active'); // Activate the clicked item
                }
            });
        });
    }
}

// Filter Form Toggle
/**
 * Sets up toggle functionality for the filter form.
 * Toggles visibility between "d-none" and "d-block" classes.
 */
function setupFilterToggle() {
    const toggleButton = document.getElementById('toggle-filters');
    const filterForm = document.getElementById('filter-form');

    if (toggleButton && filterForm) {
        toggleButton.addEventListener('click', function () {
            const isHidden = filterForm.classList.contains('d-none');

            // Toggle visibility classes
            filterForm.classList.toggle('d-none', !isHidden);
            filterForm.classList.toggle('d-block', isHidden);
        });
    }
}

// Category Dropdown Multi-Select
/**
 * Sets up multi-select functionality for category checkboxes.
 * Handles "All" checkbox behavior and updates the dropdown button label.
 */
function setupCategorySelection() {
    const allCheckbox = document.querySelector('input[name="category[]"][value=""]');
    const categoryCheckboxes = document.querySelectorAll('input[name="category[]"]:not([value=""])');

    if (allCheckbox) {
        // Handle "All" checkbox behavior
        allCheckbox.addEventListener('change', function () {
            if (allCheckbox.checked) {
                categoryCheckboxes.forEach(checkbox => checkbox.checked = false);
            }
            updateCategoryButton();
        });
    }

    if (categoryCheckboxes.length > 0) {
        // Handle individual category checkboxes behavior
        categoryCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function () {
                if (this.checked) {
                    allCheckbox.checked = false; // Deselect "All" when any category is selected
                }
                if (Array.from(categoryCheckboxes).every(checkbox => checkbox.checked)) {
                    allCheckbox.checked = true; // Select "All" if all individual categories are selected
                    categoryCheckboxes.forEach(checkbox => checkbox.checked = false); // Deselect others
                }
                updateCategoryButton();
            });
        });
    }
}

/**
 * Updates the category dropdown button label based on selected categories.
 */
function updateCategoryButton() {
    const allCheckbox = document.querySelector('input[name="category[]"][value=""]');
    const categoryCheckboxes = document.querySelectorAll('input[name="category[]"]:not([value=""])');
    const categoryDropdownButton = document.getElementById('categoryDropdownButton');

    // Check if the button exists
    if (!categoryDropdownButton) {
        return;
    }

    if (allCheckbox && allCheckbox.checked) {
        categoryDropdownButton.textContent = 'All';
    } else {
        const selectedCategories = Array.from(categoryCheckboxes)
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.closest('label').textContent.trim());

        if (selectedCategories.length > 0) {
            categoryDropdownButton.textContent = selectedCategories.join(', ');
        } else {
            categoryDropdownButton.textContent = 'All';
        }
    }
}

// Refresh page on "Show Out of Stock" toggle
/**
 * Sets up functionality to refresh the page based on the "Show Out of Stock" checkbox state.
 */
function setupOutOfStockToggle() {
    const outOfStockCheckbox = document.getElementById('show-out-of-stock');
    if (outOfStockCheckbox) {
        outOfStockCheckbox.addEventListener('change', function () {
            // Reload the page with the updated query parameter
            const url = new URL(window.location.href);
            if (this.checked) {
                url.searchParams.set('show_out_of_stock', 'on');
            } else {
                url.searchParams.delete('show_out_of_stock');
            }
            window.location.href = url.toString();
        });
    }
}

// Cookie Consent Banner
/**
 * Sets up the cookie consent banner functionality.
 * Hides the banner and loads deferred images upon acceptance.
 */
function setupCookieConsent() {
    const banner = document.getElementById('cookie-banner');
    const acceptButton = document.getElementById('accept-cookies');

    // Check if consent is already given
    if (document.cookie.split('; ').find(row => row.startsWith('cookies_accepted='))) {
        banner.style.display = 'none';
        loadDeferredImages();
        return;
    }

    // Show the banner if consent is not given
    banner.style.display = 'block';

    // Handle acceptance
    acceptButton.addEventListener('click', () => {
        fetch('/set-cookie-consent/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.cookie = "cookies_accepted=true; path=/; max-age=" + 60 * 60 * 24 * 365; // 1 year
                    banner.style.display = 'none';
                    loadDeferredImages(); // Load images after consent
                } else {
                    showToast('warning', `Failed to save cookie preference, please refresh the page and try again`);
                }
            })
            .catch(error => showToast('error', `${error}`));
    });
}

/**
 * Loads deferred images by setting their "src" attribute from "data-src".
 */
function loadDeferredImages() {
    const deferredImages = document.querySelectorAll('.deferred-image[data-src]');
    deferredImages.forEach(img => {
        const dataSrc = img.getAttribute('data-src');
        if (dataSrc) {
            img.src = dataSrc; // Set the actual source to the img element
            img.removeAttribute('data-src'); // Clean up the data-src attribute
        }
    });
}

// Toast Functionality
/**
 * Fetches a toast template from the server.
 * @param {string} message - The message to display in the toast.
 * @param {string} type - The type of toast (e.g., "success", "error").
 * @returns {Promise<string|null>} The toast HTML as a string or null on failure.
 */
async function fetchToastTemplate(message, type) {
    const url = "/render-toast/";
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ message, type })
        });
        if (!response.ok) {
            throw new Error("Failed to load toast template.");
        }
        return await response.text();
    } catch (error) {
        console.error("Error fetching toast template:", error);
        return null;
    }
}

/**
 * Displays a toast notification using the fetched template.
 * @param {string} type - The type of toast (e.g., "success", "error").
 * @param {string} message - The message to display in the toast.
 */
async function showToast(type, message) {
    const toastContainer = document.querySelector('.toast-container');

    if (!toastContainer) {
        console.error("Toast container not found.");
        return;
    }

    // Fetch the toast HTML
    const toastResponse = await fetchToastTemplate(message, type);

    if (!toastResponse) {
        console.error("Failed to fetch toast response.");
        return;
    }

    // Parse the JSON response to extract the HTML
    let toastHTML;
    try {
        const parsedResponse = JSON.parse(toastResponse); // Parse JSON
        toastHTML = parsedResponse.html; // Extract the HTML content
    } catch (error) {
        console.error("Error parsing toast response:", error);
        return;
    }

    const toastWrapper = document.createElement('div');
    toastWrapper.innerHTML = toastHTML.trim();

    const toastElement = toastWrapper.firstElementChild;

    if (!toastElement) {
        console.error("Failed to create a valid toast element.");
        return;
    }

    toastContainer.appendChild(toastElement);

    const toast = new bootstrap.Toast(toastElement);

    toast.show();
}

/**
 * Fetch wrapper with error handling and toast notifications.
 * @param {string} url - The URL to fetch.
 * @param {Object} options - Fetch options (headers, method, etc.).
 * @returns {Promise<Object|null>} The parsed JSON response or null on failure.
 */
async function customFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const contentType = response.headers.get("content-type");

        if (contentType && contentType.includes("application/json")) {
            const data = await response.json();
            return handleApiResponse(response, data);
        } else {
            throw new Error("Invalid response format. Expected JSON.");
        }
    } catch (error) {
        showToast("error", `Request failed: ${error.message}`);
        return null;
    }
}

/**
 * Handles API responses, including error reporting.
 * @param {Response} response - The fetch response.
 * @param {Object} data - The parsed JSON data.
 * @returns {Object|null} The data if valid, or null on error.
 */
async function handleApiResponse(response, data) {
    if (!response.ok) {
        if (data.errors) {
            // Display detailed field-specific errors
            Object.entries(data.errors).forEach(([field, messages]) => {
                const capitalizedField = capitalizeField(field);
                messages.forEach(msg => showToast('error', `${capitalizedField}: ${msg.message || msg}`));
            });
        } else if (data.error) {
            showToast("error", data.error);
        } else {
            showToast("error", "An unexpected error occurred.");
        }
        return null;
    }
    return data;
}

/**
 * Initializes all toasts present on the page.
 */
function initializeToasts() {
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach((toastElement) => {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    });
}

/**
 * Capitalizes a field name, cleaning it of special characters.
 * @param {string} field - The field name to capitalize.
 * @returns {string} The cleaned and capitalized field name.
 */
function capitalizeField(field) {
    // Handle cases like "variant[0].price" by splitting on "." and "[" or other delimiters
    const cleanField = field.split(/[.\[]/)[0]; // Extract only the first segment
    return cleanField.charAt(0).toUpperCase() + cleanField.slice(1);
}

/**
 * Updates the flag image based on the selected country.
 *
 * This function listens for changes in the country selector dropdown.
 * When a country is selected, it dynamically updates the flag image to match
 * the selected country using the country code.
 *
 * Expected IDs:
 * - `id_country`: The <select> element for selecting the country.
 * - `flag_id_country`: The <img> element displaying the corresponding flag.
 *
 * The flag images are expected to follow the naming convention:
 * `/static/flags/{country_code}.gif`, where `{country_code}` is the lowercase
 * value of the selected country's code.
 */
function flagOnCountryChange() {
    // Get the country selector dropdown by its ID
    const countrySelect = document.getElementById('id_country');
    // Get the flag image element by its ID
    const flagImage = document.getElementById('flag_id_country');

    // Check if the country selector exists
    if (countrySelect) {
        // Add an event listener to detect changes in the dropdown
        countrySelect.addEventListener('change', function () {
            // Get the selected country's value and convert it to lowercase
            const selectedCountry = countrySelect.value.toLowerCase();

            // If the flag image exists, update its `src` attribute
            if (flagImage) {
                flagImage.src = `/static/flags/${selectedCountry}.gif`;
            }
        });
    }
}

/**
 * Initializes all event listeners once DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', function () {
    setupMobileSearchToggle();
    setupMenuItemToggle();
    setupFilterToggle();
    setupCategorySelection();
    updateCategoryButton();
    setupOutOfStockToggle();
    setupCookieConsent();
    initializeToasts();
    flagOnCountryChange();
});
