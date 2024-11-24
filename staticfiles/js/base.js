// Mobile search bar toggler
document.getElementById('mobileSearchButton').addEventListener('click', function () {
    const searchBar = document.querySelector('.search-bar-container');
    searchBar.classList.toggle('active'); // Show/hide the search bar
    searchBar.classList.toggle('d-none'); // Ensure it’s not hidden
});

// Define a function to handle the menu item toggle
function setupMenuItemToggle() {
    // Select all menu items
    const menuItems = document.querySelectorAll('.menu-item');

    // Add click event listener to each menu item
    menuItems.forEach(item => {
        item.addEventListener('click', function () {
            // If this item is already active, remove the active class
            if (this.classList.contains('active')) {
                this.classList.remove('active');
            } else {
                // Remove 'active' class from all menu items
                menuItems.forEach(i => i.classList.remove('active'));

                // Add 'active' class to the clicked menu item
                this.classList.add('active');
            }
        });
    });
}


// Call the function when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', setupMenuItemToggle);