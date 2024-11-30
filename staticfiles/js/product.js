class ProductCardHandler {
    constructor() {
        this.disabledClass = "disabled";
        this.outOfStockClass = "text-danger";
        this.init();
    }

    init() {
        // Select all size dropdowns and set up event listeners
        const sizeSelectors = document.querySelectorAll(".size");
        sizeSelectors.forEach(sizeSelect => {
            // Trigger updates for each size selector on DOM load
            this.updateProductCard(sizeSelect);

            // Add event listener for size changes
            sizeSelect.addEventListener("change", () => this.updateProductCard(sizeSelect));
        });
    }

    updateProductCard(sizeSelect) {
        if (!sizeSelect) return;

        // Extract product ID from the element's ID
        const productId = sizeSelect.id.split("-")[2];
        const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
        const price = selectedOption.dataset.price || 0;
        const stock = parseInt(selectedOption.dataset.stock || 0, 10);

        // Update price display
        const priceDisplay = document.getElementById(`price-display-${productId}`);
        if (priceDisplay) {
            if (stock > 0) {
                priceDisplay.innerHTML = `<strong>$${price} <span>each</span></strong>`;
                priceDisplay.classList.remove(this.outOfStockClass);
            } else {
                priceDisplay.innerHTML = `<strong>Out of Stock</strong>`;
                priceDisplay.classList.add(this.outOfStockClass);
            }
        }

        // Enable or disable the buy button
        const buyButton = document.getElementById(`buy-button-${productId}`);
        if (buyButton) {
            if (stock <= 0) {
                buyButton.classList.add(this.disabledClass);
                buyButton.setAttribute("disabled", "disabled");
            } else {
                buyButton.classList.remove(this.disabledClass);
                buyButton.removeAttribute("disabled");
            }
        }
    }
}

// Initialize the handler on DOM load
document.addEventListener("DOMContentLoaded", () => new ProductCardHandler());
