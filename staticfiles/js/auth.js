/**
 * Toggles the sidebar collapse/expand and updates the toggle button icon.
 */
function handleSidebarToggle() {
    let sidebar = document.getElementById('sidebar'); // Sidebar element
    let toggleBtn = document.getElementById('toggle-btn'); // Button to toggle sidebar
    let mainContent = document.getElementById('content-container'); // Main content container

    // Guard clause to ensure the elements exist
    if (!sidebar || !toggleBtn || !mainContent) {
        showToast('error', "Sidebar, toggle button, or main content not found."); // Error notification
        return;
    }

    // Toggle the 'collapsed' class on the sidebar and main content
    sidebar.classList.toggle('collapsed'); // Collapse/expand sidebar
    mainContent.classList.toggle('collapsed'); // Adjust main content accordingly

    // Toggle the icon between left and right arrow
    let icon = toggleBtn.querySelector('i'); // Icon inside the toggle button
    if (icon) {
        icon.classList.toggle('fa-arrow-left'); // Switch to left arrow
        icon.classList.toggle('fa-arrow-right'); // Switch to right arrow
    }
}

/**
 * Adjusts the sidebar and main content layout based on screen width.
 * Collapses the sidebar on smaller screens (< 768px) and expands it on larger screens.
 */
function handleScreenResize() {
    let sidebar = document.getElementById('sidebar'); // Sidebar element
    let toggleBtn = document.getElementById('toggle-btn'); // Button to toggle sidebar
    let mainContent = document.getElementById('content-container'); // Main content container

    // Guard clause to ensure the elements exist
    if (!sidebar || !toggleBtn || !mainContent) {
        showToast('error', "Sidebar, toggle button, or main content not found."); // Error notification
        return;
    }

    if (window.innerWidth < 768) {
        // Collapse sidebar on smaller screens
        sidebar.classList.add('collapsed');
        mainContent.classList.add('collapsed');
        let icon = toggleBtn.querySelector('i'); // Icon inside the toggle button
        if (icon) {
            icon.classList.remove('fa-arrow-left'); // Remove left arrow
            icon.classList.add('fa-arrow-right'); // Add right arrow
        }
    } else {
        // Expand sidebar on larger screens
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('collapsed');
        let icon = toggleBtn.querySelector('i'); // Icon inside the toggle button
        if (icon) {
            icon.classList.remove('fa-arrow-right'); // Remove right arrow
            icon.classList.add('fa-arrow-left'); // Add left arrow
        }
    }
}

/**
 * Initializes the sidebar state and event listeners once the DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', function () {
    let toggleBtn = document.getElementById('toggle-btn'); // Button to toggle sidebar
    let sidebar = document.getElementById('sidebar'); // Sidebar element
    let mainContent = document.getElementById('content-container'); // Main content container

    // Guard clause to ensure the elements exist
    if (!toggleBtn || !sidebar || !mainContent) {
        showToast('error', "Sidebar, toggle button, or main content not found."); // Error notification
        return;
    }

    // Initial state: Collapse sidebar on smaller screens
    if (window.innerWidth < 768) {
        sidebar.classList.add('collapsed'); // Collapse sidebar
        mainContent.classList.add('collapsed'); // Adjust main content
        let icon = toggleBtn.querySelector('i'); // Icon inside the toggle button
        if (icon) {
            icon.classList.remove('fa-arrow-left'); // Remove left arrow
            icon.classList.add('fa-arrow-right'); // Add right arrow
        }
    }

    // Attach resize event listener
    window.addEventListener('resize', handleScreenResize);

    // Attach click event listener to the sidebar toggle button
    toggleBtn.addEventListener('click', handleSidebarToggle);
});
