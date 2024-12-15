// Mobile Search Bar Toggle
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
function setupMenuItemToggle() {
    const menuItems = document.querySelectorAll('.menu-item');
    if (menuItems.length > 0) {
        menuItems.forEach(item => {
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

// Function to update the button label
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

        categoryDropdownButton.textContent = selectedCategories.length > 0
            ? selectedCategories.join(', ')
            : 'All';
    }
}

// Refresh page on "Show Out of Stock" toggle
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
                    showToast('warning', `Failed to save cookie preference, please refresh the page and try again`)
                }
            })
            .catch(error => showToast('error', `${error}`));
    });
}

// Function to load deferred images
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

async function handleApiResponse(response) {
    let json;
    try {
        // Parse JSON response
        json = await response.json();
    } catch (error) {
        showToast("error", `An unexpected error occurred: ${error}`);
        return null;
    }

    if (!response.ok) {
        // Handle HTTP errors
        const errorMessage = json.error || "An unexpected error occurred.";
        showToast(json.type || "error", errorMessage);
        return null;
    }

    // If success, return the parsed JSON
    return json;
}

async function customFetch(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await handleApiResponse(response);
        return data;
    } catch (error) {
        showToast("error", `Failed to connect to the server: ${error}`);
        return null;
    }
}

function initializeToasts() {
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach((toastElement) => {
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    });
}

// Initialize all event listeners once DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    setupMobileSearchToggle();
    setupMenuItemToggle();
    setupFilterToggle();
    setupCategorySelection();
    updateCategoryButton();
    setupOutOfStockToggle();
    setupCookieConsent();
    initializeToasts();
});
