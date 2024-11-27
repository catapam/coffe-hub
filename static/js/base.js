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

// Initialize all event listeners once DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    setupMobileSearchToggle();
    setupMenuItemToggle();
    setupFilterToggle();
});
