function previewImage(input, imageId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const imageElement = document.getElementById(imageId);
            if (imageElement) {
                imageElement.src = e.target.result;
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

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
            this.updateProductUrl(sizeSelect);

            // Add event listener for size changes
            sizeSelect.addEventListener("change", () => {
                this.updateProductCard(sizeSelect);
                this.updateProductUrl(sizeSelect);
            });
        });

        // Add event listeners for image uploads
        const imageInputs = document.querySelectorAll("input[type='file'][id^='image-edit-']");
        imageInputs.forEach(imageInput => {
            const imageId = imageInput.id.replace("image-edit-", "product-image-");
            imageInput.addEventListener("change", () => {
                this.previewImage(imageInput, imageId);
            });
        });
    }

    updateProductCard(sizeSelect) {
        if (!sizeSelect) return;

        // Find the parent card containing the size selector
        var cardElement = sizeSelect.closest(".product-card");
        if (!cardElement) {
            return;
        }

        // Get the selected option details
        const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
        if (!selectedOption) return;

        const price = selectedOption.dataset.price;
        const stock = parseInt(selectedOption.dataset.stock || 0, 10);

        // Update elements within this specific card
        this.updatePriceDisplay(cardElement, price, stock);
        this.updateBuyButton(cardElement, stock);
        this.updateStockInput(cardElement, stock);
    }

    updateStockInput(cardElement, stock) {
        // Find the stock/quantity input within the specific card
        let stockInput = cardElement.querySelector(`#id_stock`);
        const quantityInput = cardElement.querySelector(`#quantity-select-${cardElement.querySelector('.size').id.split('-')[2]}`);
        if (stockInput) {
            stockInput.value = stock; // Update the stock input value
        } else if (quantityInput){
            quantityInput.value = 1;
        } else{
            stockInput = `#stock-select-${cardElement.querySelector('.size').id.split('-')[2]}`
            stockInput.value = stock; 
        }
    }

    updatePriceDisplay(cardElement, price, stock) {
        const sizeInput = cardElement.querySelector('.size');
        let slug = '';
        if (sizeInput) {
            slug = sizeInput.id.split('-')[2];
        }
    
        const priceDisplay = cardElement.querySelector(`#price-${slug}`);
        const priceEdit = cardElement.querySelector(`#id_price`);
    
        if (priceDisplay) {
            if (stock > 0) {
                priceDisplay.innerHTML = `<strong>$${price} <span>each</span></strong>`;
                priceDisplay.classList.remove(this.outOfStockClass);
            } else {
                priceDisplay.innerHTML = `<strong>Out of Stock</strong>`;
                priceDisplay.classList.add(this.outOfStockClass);
            }
        } else if (priceEdit) {
            priceEdit.value = `${price}`;
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

    updateProductUrl(sizeSelect) {
        if (!sizeSelect) return;

        // Extract slug or ID from the select element's ID
        const selectId = sizeSelect.id; // Example: size-select-<slug or id>
        const slug = selectId.split('-')[2]; // Extract slug or ID

        // Get the base URL and selected size
        const base_url = sizeSelect.getAttribute("data-base-url");
        const size = sizeSelect.value;

        // Check if we are on the detail view
        const isDetailView = document.querySelector(".product-card.container"); // Unique class for detail view

        if (isDetailView) {
            // Update the current page's URL
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set("size", size); // Update the size parameter
            window.history.replaceState(null, "", newUrl.toString());
        } else {
            // Update 'detail-link' and 'edit-link' only for list view
            const detailLink = document.getElementById(`detail-link-${slug}`);
            const editLink = document.getElementById(`edit-link-${slug}`);

            // Update 'detail-link' if it exists
            if (detailLink && base_url) {
                detailLink.href = `${base_url}?size=${size}`;
            }

            // Update 'edit-link' if it exists
            if (editLink && base_url) {
                editLink.href = `${base_url}?size=${size}`;
            }
        }
    }    
}

// Initialize the handler on DOM load
document.addEventListener("DOMContentLoaded", () => new ProductCardHandler());
