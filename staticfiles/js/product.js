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

        // Find the parent card containing the size selector
        const cardElement = sizeSelect.closest(".card");
        if (!cardElement) return;

        // Get the selected option details
        const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
        if (!selectedOption) return;

        const price = selectedOption.dataset.price || 0;
        const stock = parseInt(selectedOption.dataset.stock || 0, 10);

        // Update elements within this specific card
        this.updatePriceDisplay(cardElement, price, stock);
        this.updateBuyButton(cardElement, stock);
    }

    updatePriceDisplay(cardElement, price, stock) {
        // Find the price display within the specific card
        const priceDisplay = cardElement.querySelector(`#price-display-${cardElement.querySelector('.size').id.split('-')[2]}`);
        if (priceDisplay) {
            if (stock > 0) {
                priceDisplay.innerHTML = `<strong>$${price} <span>each</span></strong>`;
                priceDisplay.classList.remove(this.outOfStockClass);
            } else {
                priceDisplay.innerHTML = `<strong>Out of Stock</strong>`;
                priceDisplay.classList.add(this.outOfStockClass);
            }
        }
    }

    updateBuyButton(cardElement, stock) {
        // Find the buy button within the specific card
        const buyButton = cardElement.querySelector(`#buy-button-${cardElement.querySelector('.size').id.split('-')[2]}`);
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
