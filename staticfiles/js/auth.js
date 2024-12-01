/**
 * Toggles the sidebar collapse/expand and updates the toggle button icon.
 */
function handleSidebarToggle() {
    var sidebar = document.getElementById('sidebar');
    var toggleBtn = document.getElementById('toggle-btn');
    var mainContent = document.getElementById('content-container');

    // Guard clause to ensure the elements exist
    if (!sidebar || !toggleBtn || !mainContent) {
        console.error("Sidebar, toggle button, or main content not found.");
        return;
    }

    // Toggle the 'collapsed' class on the sidebar and main content
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('collapsed');

    // Toggle the icon between left and right arrow
    var icon = toggleBtn.querySelector('i');
    if (icon) {
        icon.classList.toggle('fa-arrow-left');
        icon.classList.toggle('fa-arrow-right');
    }
}

/**
 * Adjusts the sidebar and main content layout based on screen width.
 * Collapses the sidebar on smaller screens (< 768px) and expands it on larger screens.
 */
function handleScreenResize() {
    var sidebar = document.getElementById('sidebar');
    var toggleBtn = document.getElementById('toggle-btn');
    var mainContent = document.getElementById('content-container');

    // Guard clause to ensure the elements exist
    if (!sidebar || !toggleBtn || !mainContent) {
        console.error("Sidebar, toggle button, or main content not found.");
        return;
    }

    if (window.innerWidth < 768) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('collapsed');
        var icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-arrow-left');
            icon.classList.add('fa-arrow-right');
        }
    } else {
        sidebar.classList.remove('collapsed');
        mainContent.classList.remove('collapsed');
        var icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-arrow-right');
            icon.classList.add('fa-arrow-left');
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    var toggleBtn = document.getElementById('toggle-btn');
    var sidebar = document.getElementById('sidebar');
    var mainContent = document.getElementById('content-container');

    // Guard clause to ensure the elements exist
    if (!toggleBtn || !sidebar || !mainContent) {
        console.error("Sidebar, toggle button, or main content not found.");
        return;
    }

    // Initial state: Collapse sidebar on smaller screens
    if (window.innerWidth < 768) {
        sidebar.classList.add('collapsed');
        mainContent.classList.add('collapsed');
        var icon = toggleBtn.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-arrow-left');
            icon.classList.add('fa-arrow-right');
        }
    }

    // Attach resize event listener
    window.addEventListener('resize', handleScreenResize);

    // Attach click event listener to the sidebar toggle button
    toggleBtn.addEventListener('click', handleSidebarToggle);
});
