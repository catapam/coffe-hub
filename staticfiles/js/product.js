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
        const sizeSelectors = document.querySelectorAll(".size");
        sizeSelectors.forEach(sizeSelect => {
            this.updateProductCard(sizeSelect);
            this.updateProductUrl(sizeSelect);

            sizeSelect.addEventListener("change", () => {
                this.updateProductCard(sizeSelect);
                this.updateProductUrl(sizeSelect);
            });
        });

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
    
        const cardElement = sizeSelect.closest(".product-card");
        if (!cardElement) {
            return;
        }
    
        const selectedOption = sizeSelect.options[sizeSelect.selectedIndex];
        if (!selectedOption) return;
    
        const price = selectedOption.dataset.price;
        const stock = parseInt(selectedOption.dataset.stock || 0, 10);
        const variantActive = selectedOption.dataset.active === "true";
        const variantId = selectedOption.dataset.variantId;
    
        this.updatePriceDisplay(cardElement, price, stock);
        this.updateBuyButton(cardElement, stock);
        this.updateStockInput(cardElement, stock);
        this.updateVariantState(cardElement, variantActive, variantId);
    }
    
    updateVariantState(cardElement, isActive, variantId) {
        const variantButton = cardElement.querySelector(".toggle-variant-btn");
        const variantBadge = cardElement.querySelector(`#badge-size-${cardElement.querySelector('.size').id.split('-')[2]}`);
        
        if (variantBadge){
            variantBadge.classList.toggle("badge-active", isActive);
            variantBadge.classList.toggle("badge-inactive", !isActive);
            variantBadge.textContent = isActive ? "Size: Active" : "Size: Inactive";
        } 

        if (variantId){
            if (variantButton){
                variantButton.setAttribute("data-url", `/products/variant/${variantId}/deactivate/`);
                variantButton.setAttribute("data-active", isActive ? "true" : "false");
                variantButton.classList.toggle("btn-danger", isActive);
                variantButton.classList.toggle("btn-success", !isActive);
                variantButton.textContent = isActive ? "Deactivate Size" : "Activate Size";
            }
        } 
    }  

    updateStockInput(cardElement, stock) {
        let stockInput = cardElement.querySelector(`#id_stock`);
        const quantityInput = cardElement.querySelector(`#quantity-select-${cardElement.querySelector('.size').id.split('-')[2]}`);
    
        if (stockInput) {
            stockInput.value = stock; // Update stock input if found
        } else if (quantityInput) {
            quantityInput.value = 1; // Set default quantity input value if found
        } else {
            // Find the stock input element using querySelector
            stockInput = cardElement.querySelector(`#stock-select-${cardElement.querySelector('.size').id.split('-')[2]}`);
            if (stockInput) {
                stockInput.value = `${stock}`; // Update the value of the stock input
            } 
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

        const selectId = sizeSelect.id;
        const slug = selectId.split('-')[2];

        const base_url = sizeSelect.getAttribute("data-base-url");
        const size = sizeSelect.value;

        const isDetailView = document.querySelector(".product-card.container");

        if (isDetailView) {
            const newUrl = new URL(window.location.href);
            newUrl.searchParams.set("size", size);
            window.history.replaceState(null, "", newUrl.toString());
        } else {
            const detailLink = document.getElementById(`detail-link-${slug}`);
            const editLink = document.getElementById(`edit-link-${slug}`);

            if (detailLink && base_url) {
                detailLink.href = `${base_url}?size=${size}`;
            }

            if (editLink && base_url) {
                editLink.href = `${base_url}?size=${size}`;
            }
        }
    }

    previewImage(input, imageId) {
        previewImage(input, imageId);
    }
}

class StarRatingHandler {
    constructor(starContainerSelector, ratingInputSelector) {
        this.starContainer = document.querySelector(starContainerSelector);
        this.ratingInput = document.getElementById(ratingInputSelector);
        
        if (this.starContainer && this.ratingInput) {
            this.init();
        }
    }

    init() {
        this.stars = this.starContainer.querySelectorAll('.star');
        this.stars.forEach(star => {
            star.addEventListener('click', () => this.handleClick(star));
            star.addEventListener('mouseover', () => this.handleMouseOver(star));
            star.addEventListener('mouseout', () => this.handleMouseOut());
        });
    }

    handleClick(star) {
        const chosenValue = parseInt(star.getAttribute('data-value'), 10);
        let currentRating = parseInt(this.ratingInput.value || '0', 10);

        if (currentRating === chosenValue && currentRating > 0) {
            currentRating -= 1;
        } else {
            currentRating = chosenValue;
        }

        this.ratingInput.value = currentRating;
        this.updateStars(currentRating, 'filled');
    }

    handleMouseOver(star) {
        const hoverValue = parseInt(star.getAttribute('data-value'), 10);
        this.updateStars(hoverValue, 'hovered');
        this.updateStars(hoverValue, 'unhovered');
    }

    handleMouseOut() {
        this.stars.forEach(s => s.classList.remove('hovered'));
        this.stars.forEach(s => s.classList.remove('unhovered'));
    }

    updateStars(value, className) {
        this.stars.forEach(s => {
            const starValue = parseInt(s.getAttribute('data-value'), 10);
            if (className === 'filled') {
                s.classList.toggle('filled', starValue <= value);
            } else if (className === 'hovered') {
                s.classList.toggle('hovered', starValue <= value);
            } else if (className === 'unhovered') {
                s.classList.toggle('unhovered', starValue >= value);
            }
        });
    }
}

class ReviewHandler {
    constructor(filterSelector, reviewSelector, noResultsMessageSelector) {
        this.filters = document.querySelectorAll(filterSelector);
        this.reviews = document.querySelectorAll(reviewSelector);
        this.noResultsMessage = document.querySelector(noResultsMessageSelector);

        if (this.filters.length > 0 && this.reviews.length > 0) {
            this.init();
        }
    }

    init() {
        this.filters.forEach(filter => {
            filter.addEventListener('click', () => {
                const filterValue = filter.dataset.filter 
                    ? parseInt(filter.dataset.filter, 10) 
                    : "all";
                this.filterReviews(filterValue);
            });
        });
    }

    filterReviews(filterValue) {
        let reviewsShown = 0;

        this.reviews.forEach(review => {
            const reviewRating = parseInt(review.getAttribute("data-rating"), 10);

            if (filterValue === "all" || reviewRating === filterValue) {
                review.style.display = "block";
                reviewsShown++;
            } else {
                review.style.display = "none";
            }
        });

        if (this.noResultsMessage) {
            this.noResultsMessage.style.display = reviewsShown === 0 ? "block" : "none";
        }
    }
}

class ReviewSilenceHandler {
    constructor(buttonSelector, reviewContainerSelector) {
        this.buttons = document.querySelectorAll(buttonSelector);
        this.reviewContainerSelector = reviewContainerSelector;

        if (this.buttons.length > 0) {
            this.init();
        }
    }

    init() {
        this.buttons.forEach(button => {
            button.addEventListener('click', (event) => {
                event.preventDefault(); // Prevent default anchor behavior
                const url = button.getAttribute('data-url');
                const reviewId = button.getAttribute('data-review-id');

                if (!url || !reviewId) return;

                // Make the POST request
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCSRFToken(),
                        'Content-Type': 'application/json',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.updateReviewState(button, reviewId, data.silenced);
                    } else {
                        console.error('Error toggling silence:', data.error);
                    }
                })
                .catch(error => console.error('Request failed:', error));
            });
        });
    }

    updateReviewState(button, reviewId, silenced) {
        // Update button state
        this.toggleButtonState(button, silenced);

        // Find the review container by ID
        const reviewContainer = document.querySelector(
            `${this.reviewContainerSelector}[data-review-id="${reviewId}"]`
        );

        if (reviewContainer) {
            // Update silenced styles
            const commentElement = reviewContainer.querySelector('.review-comment');
            const silencedIndicator = reviewContainer.querySelector('.silenced-indicator');
            if (commentElement && silencedIndicator) {
                if (silenced) {
                    commentElement.classList.add('silenced');
                    silencedIndicator.classList.add('d-flex');
                    silencedIndicator.classList.remove('d-none');
                } else {
                    commentElement.classList.remove('silenced');
                    silencedIndicator.classList.add('d-none');
                    silencedIndicator.classList.remove('d-flex');
                }
            }
        }
    }

    toggleButtonState(button, silenced) {
        button.classList.toggle('btn-primary', !silenced);
        button.classList.toggle('btn-secondary', silenced);

        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.toggle('fa-eye-slash', !silenced);
            icon.classList.toggle('fa-eye', silenced);
        }

        button.setAttribute('data-silenced', silenced ? 'true' : 'false');
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
}

class ProductActivationHandler {
    constructor(buttonSelector) {
        this.buttons = document.querySelectorAll(buttonSelector);

        if (this.buttons.length > 0) {
            this.init();
        }
    }

    init() {
        this.buttons.forEach(button => {
            button.addEventListener("click", () => {
                const url = button.getAttribute("data-url");
                if (!url) return;

                fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": this.getCSRFToken(),
                        "Content-Type": "application/json",
                    },
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            this.updateButtonState(button, data.active);
                            this.updateBadges(button, data);
                        } else {
                            console.error("Failed to update state:", data.error);
                        }
                    })
                    .catch(error => console.error("Request failed:", error));
            });
        });
    }

    updateButtonState(button, isActive) {
        const buttonText = button.textContent.trim().replace(/(Activate|Deactivate)/, "");
        button.classList.toggle("btn-success", !isActive);
        button.classList.toggle("btn-danger", isActive);
        button.textContent = `${isActive ? "Deactivate" : "Activate"} ${buttonText}`;
        button.setAttribute("data-active", isActive ? "true" : "false");
    }

    updateBadges(button, data) {
        const cardElement = button.closest(".product-card");
        if (!cardElement) return;

        const badgeContainer = cardElement.querySelector(".badge-container");
        if (!badgeContainer) return;

        // Check if the button is for the product or the size
        const isProductButton = button.classList.contains("toggle-product-btn");
        const isSizeButton = button.classList.contains("toggle-variant-btn");

        if (isProductButton) {
            // Update Product Badge
            const productBadge = badgeContainer.querySelector(`#badge-product-${cardElement.querySelector('.size').id.split('-')[2]}`);
            if (productBadge) {
                const isActive = data.active; // Product active state from response
                productBadge.classList.toggle("badge-active", isActive);
                productBadge.classList.toggle("badge-inactive", !isActive);
                productBadge.textContent = `Product: ${isActive ? "Active" : "Inactive"}`;
            }
        }

        if (isSizeButton) {
            // Update Size/Variant Badge
            const variantBadge = badgeContainer.querySelector(`#badge-size-${cardElement.querySelector('.size').id.split('-')[2]}`);
            if (variantBadge) {
                variantBadge.classList.toggle("badge-active");
                variantBadge.classList.toggle("badge-inactive");

                const isActive = variantBadge.classList.contains("badge-active"); 
                variantBadge.textContent = isActive ? "Size: Active" : "Size: Inactive";
            }
        }
    }


    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}


class SelectorHandler {
    constructor(type) {
        this.type = type; // 'category' or 'size'
        this.lastAction = null; // track whether last action was 'add' or 'edit'
        this.init();
    }

    init() {
        this.addButton = document.querySelector(`#add_${this.type}`);
        this.editButton = document.querySelector(`#edit_${this.type}`);
        this.cancelButton = document.querySelector(`#cancel_${this.type}`);
        this.saveButton = document.querySelector(`#save_${this.type}`);

        if (this.addButton && this.editButton && this.cancelButton && this.saveButton) {
            this.selectElement = document.querySelector(`.${this.type}`);
            this.inputElement = document.querySelector(`.${this.type}-input`);

            this.addButton.addEventListener("click", (event) => {
                this.lastAction = "add";
                this.toggleInput(event, "add");
            });
            this.editButton.addEventListener("click", (event) => {
                this.lastAction = "edit";
                this.toggleInput(event, "edit");
            });
            this.cancelButton.addEventListener("click", (event) => {
                this.lastAction = null;
                this.toggleInput(event, "cancel");
            });
            this.saveButton.addEventListener("click", (event) => {
                this.toggleInput(event, "save");
                this.handleSave();
            });
        }
    }

    toggleInput(event, action) {
        const clickedButton = event.target;
        const parentSelectorGroup = clickedButton.closest(".selector-group");

        if (!this.selectElement || !this.inputElement) return;

        if (action === "edit") {
            const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
            this.inputElement.value = selectedOption ? selectedOption.textContent.trim() : "";
        } else if (action === "add") {
            this.inputElement.value = "";
            this.inputElement.placeholder = `New ${this.type}`;
        }

        // Toggle UI elements
        this.selectElement.classList.toggle("d-none", action !== "cancel" && action !== "save");
        this.inputElement.classList.toggle("d-none", action === "cancel" || action === "save");
        parentSelectorGroup.querySelectorAll("button").forEach((button) => {
            if (button.id === `edit_${this.type}` || button.id === `add_${this.type}`) {
                // Show these if we are canceling or after saving
                button.classList.toggle("d-none", !(action === "cancel" || action === "save"));
            } else {
                // Show cancel/save during editing/adding
                button.classList.toggle("d-none", (action === "cancel" || action === "save"));
            }
        });

        // Re-enable all disabled elements if cancel/save
        if (action === "cancel" || action === "save") {
            document.querySelectorAll(".product-card input, .product-card button, .product-card select, .product-card textarea").forEach((element) => {
                element.disabled = false;
            });
        } else {
            // Disable all elements outside current selector-group if editing/adding
            document.querySelectorAll(".product-card input, .product-card button, .product-card select, .product-card textarea").forEach((element) => {
                if (!element.closest(".selector-group") || element.closest(".selector-group") !== parentSelectorGroup) {
                    element.disabled = true;
                }
            });
        }

        // Focus on input if visible
        if (!this.inputElement.classList.contains("d-none") && (action === "add" || action === "edit")) {
            this.inputElement.focus();
        }
    }

    handleSave() {
        const newName = this.inputElement.value.trim();
        if (!newName) return; // no empty submissions

        const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
        const currentValue = selectedOption ? selectedOption.value : null;

        // Prepare data to send to the server
        const payload = {
            action: this.lastAction,
            type: this.type,
            name: newName,
            current_value: currentValue,
            product_id: this.selectElement.id.split('-').pop() // extract product ID from select ID if needed
        };

        // Send AJAX request to your Django endpoint
        fetch(`/products/${this.type}/save/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": this.getCSRFToken(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update UI: Add or update the option in the dropdown
                if (this.lastAction === "add") {
                    const newOption = document.createElement("option");
                    newOption.value = data.slug;
                    newOption.textContent = data.name;
                    this.selectElement.add(newOption);
                    this.selectElement.value = data.slug;
                } else if (this.lastAction === "edit") {
                    if (selectedOption) {
                        selectedOption.value = data.slug;
                        selectedOption.textContent = data.name;
                    }
                }
                this.lastAction = null;
            } else {
                console.error("Error saving:", data.error);
            }
        })
        .catch(error => console.error("Request failed:", error));
    }

    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}

// Initialize handlers on DOM load
document.addEventListener('DOMContentLoaded', () => {
    new ProductCardHandler();
    new StarRatingHandler('#star-rating', 'id_rating');
    new ReviewHandler('.filter', '.review-container', '#no-reviews-message');
    new ReviewSilenceHandler('.toggle-silence-btn', '.review-container');
    new ProductActivationHandler('.toggle-product-btn');
    new ProductActivationHandler('.toggle-variant-btn');
    new SelectorHandler("category");
    new SelectorHandler("size");
});

