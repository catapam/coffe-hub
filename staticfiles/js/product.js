/**
 * Previews an uploaded image by updating the source of a specified image element.
 * @param {HTMLInputElement} input - The file input element.
 * @param {string} imageId - The ID of the image element to update.
 */
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

/**
 * Handles the interactions and updates for product cards, such as size selection, stock updates, and button states.
 */
class ProductCardHandler {
    constructor() {
        this.disabledClass = "disabled";
        this.outOfStockClass = "text-danger";
        this.init();
    }

    /**
     * Initializes event listeners for size selectors, image inputs, and other interactions.
     */
    init() {
        const sizeSelectors = document.querySelectorAll(".size");

        this.handleBuyButton();
        this.handleReviewSubmission();

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

    /**
     * Updates the product card with the selected size's details.
     * @param {HTMLSelectElement} sizeSelect - The size selection dropdown.
     */
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

    /**
     * Updates the variant state (active/inactive) and related UI elements.
     * @param {HTMLElement} cardElement - The product card element.
     * @param {boolean} isActive - Whether the variant is active.
     * @param {string} variantId - The ID of the variant.
     */
    updateVariantState(cardElement, isActive, variantId) {
        const variantButton = cardElement.querySelector(".toggle-variant-btn");
        const variantBadge = cardElement.querySelector(`#badge-size-${cardElement.querySelector('.size').id.split('-')[2]}`);
        const saveButton = cardElement.querySelector(`.save-product-btn`);

        if (variantBadge) {
            variantBadge.classList.toggle("badge-active", isActive);
            variantBadge.classList.toggle("badge-inactive", !isActive);
            variantBadge.textContent = isActive ? "Size: Active" : "Size: Inactive";
        }

        if (variantId) {
            if (variantButton) {
                variantButton.setAttribute("data-url", `/products/variant/${variantId}/deactivate/`);
                variantButton.setAttribute("data-active", isActive ? "true" : "false");
                variantButton.classList.toggle("btn-danger", isActive);
                variantButton.classList.toggle("btn-success", !isActive);
                variantButton.textContent = isActive ? "Deactivate Size" : "Activate Size";
            }
            if (saveButton) {
                saveButton.setAttribute("data-variant-id", `${variantId}`);
            }
        }
    }

    /**
     * Updates the stock input field based on the selected variant.
     * @param {HTMLElement} cardElement - The product card element.
     * @param {number} stock - The stock quantity of the selected variant.
     */
    updateStockInput(cardElement, stock) {
        let stockInput = cardElement.querySelector(`#id_stock`);
        const quantityInput = cardElement.querySelector(`#quantity-select-${cardElement.querySelector('.size').id.split('-')[2]}`);

        if (stockInput) {
            stockInput.value = stock;
        } else if (quantityInput) {
            quantityInput.value = 1;
            quantityInput.max = stock;
        } else {
            stockInput = cardElement.querySelector(`#stock-select-${cardElement.querySelector('.size').id.split('-')[2]}`);
            if (stockInput) {
                stockInput.value = `${stock}`;
            }
        }
    }

    /**
     * Updates the price display based on stock and variant information.
     * @param {HTMLElement} cardElement - The product card element.
     * @param {string} price - The price of the selected variant.
     * @param {number} stock - The stock quantity of the selected variant.
     */
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

    /**
     * Updates the state of the buy button based on stock availability.
     * @param {HTMLElement} cardElement - The product card element.
     * @param {number} stock - The stock quantity of the selected variant.
     */
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

    /**
     * Updates the product URL based on the selected size.
     * @param {HTMLSelectElement} sizeSelect - The size selection dropdown.
     */
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
                editLink.href = `${base_url}?size=${size}#`;
            }
        }
    }

    /**
     * Wrapper function for previewing an image.
     * @param {HTMLInputElement} input - The file input element.
     * @param {string} imageId - The ID of the image element to update.
     */
    previewImage(input, imageId) {
        previewImage(input, imageId);
    }

    /**
     * Handles the "Buy" button click event.
     */
    handleBuyButton() {
        const buyButtons = document.querySelectorAll('[id^="buy-button-"]');

        buyButtons.forEach(button => {
            button.addEventListener("click", (event) => {
                const url = button.getAttribute("data-url");
                const productId = button.getAttribute("data-product-id");
                const size = document.querySelector(`#size-select-${productId}`)?.value;
                const quantity = document.querySelector(`#quantity-select-${productId}`)?.value;

                if (!url || !productId || !size || !quantity) {
                    showToast('error', 'Please select a valid size and quantity.');
                    return;
                }

                fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": this.getCSRFToken(),
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ size, quantity }),
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showToast('success', `${data.message}`);
                        } else {
                            showToast('error', `${data.error}`);
                        }
                    })
                    .catch(error => showToast('error', `${error.message}`));
            });
        });
    }

    /**
     * Handles the product review submission event.
     */
    handleReviewSubmission() {
        const reviewForm = document.querySelector('.rating-form');
        if (!reviewForm) return;

        reviewForm.addEventListener('submit', (event) => {
            event.preventDefault();

            const formData = new FormData(reviewForm);
            const url = reviewForm.action;

            customFetch(url, {
                method: 'POST',
                body: formData,
            }).then((data) => {
                if (data.success && data.redirect_url) {
                    window.location.href = data.redirect_url; // Silent redirect
                    showToast('success', `Thank you for submitting your product review!`);

                } else if (data.errors) {
                    Object.entries(data.errors).forEach(([field, messages]) => {
                        messages.forEach(msg => showToast('error', `${field}: ${msg}`));
                    });
                }
            });
        });
    }

    /**
     * Retrieves the CSRF token for secure form submissions.
     * @returns {string} - The CSRF token.
     */
    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}

/**
 * Manages the star rating interactions for product reviews.
 */
class StarRatingHandler {
    constructor(starContainerSelector, ratingInputSelector) {
        this.starContainer = document.querySelector(starContainerSelector);
        this.ratingInput = document.querySelector(ratingInputSelector);

        if (this.starContainer && this.ratingInput) {
            this.init();
        }
    }

    /**
     * Initializes event listeners for the stars in the star rating system.
     */
    init() {
        this.stars = this.starContainer.querySelectorAll('.star');
        this.stars.forEach(star => {
            star.addEventListener('click', () => this.handleClick(star));
            star.addEventListener('mouseover', () => this.handleMouseOver(star));
            star.addEventListener('mouseout', () => this.handleMouseOut());
        });
    }

    /**
     * Handles the click event on a star, setting the rating.
     * @param {HTMLElement} star - The clicked star element.
     */
    handleClick(star) {
        const chosenValue = parseInt(star.getAttribute('data-value'), 10);
        let currentRating = parseInt(this.ratingInput?.value || '0', 10);

        if (currentRating === chosenValue && currentRating > 0) {
            currentRating -= 1;  // Allow deselecting the star
        } else {
            currentRating = chosenValue;
        }

        this.ratingInput.value = currentRating;
        this.updateStars(currentRating, 'filled');
    }

    /**
     * Handles the mouseover event on a star, displaying a hover effect.
     * @param {HTMLElement} star - The hovered star element.
     */
    handleMouseOver(star) {
        const hoverValue = parseInt(star.getAttribute('data-value'), 10);
        this.updateStars(hoverValue, 'hovered');
        this.updateStars(hoverValue, 'unhovered');
    }

    /**
     * Handles the mouseout event on the star container, removing hover effects.
     */
    handleMouseOut() {
        this.stars.forEach(s => s.classList.remove('hovered'));
        this.stars.forEach(s => s.classList.remove('unhovered'));
    }

    /**
     * Updates the star elements' classes based on the rating.
     * @param {number} value - The rating value to apply.
     * @param {string} className - The class to update (e.g., 'filled', 'hovered').
     */
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

/**
 * Filters reviews based on their ratings.
 */
class ReviewFilterHandler {
    constructor(filterSelector, reviewSelector, noResultsMessageSelector) {
        this.filters = document.querySelectorAll(filterSelector);
        this.reviews = document.querySelectorAll(reviewSelector);
        this.noResultsMessage = document.querySelector(noResultsMessageSelector);

        if (this.filters.length > 0 && this.reviews.length > 0) {
            this.init();
        }
    }

    /**
     * Initializes event listeners for the review filters.
     */
    init() {
        this.filters.forEach(filter => {
            filter.addEventListener('click', () => {
                const filterValue = filter.dataset.filter ? parseInt(filter.dataset.filter, 10) : "all";
                this.filterReviews(filterValue);
            });
        });
    }

    /**
     * Filters the reviews based on the selected rating.
     * @param {number|string} filterValue - The rating value to filter by or 'all' to show all reviews.
     */
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

/**
 * Handles toggling the silence state of reviews.
 */
class ReviewSilenceHandler {
    constructor(buttonSelector, reviewContainerSelector) {
        this.buttons = document.querySelectorAll(buttonSelector);
        this.reviewContainerSelector = reviewContainerSelector;

        if (this.buttons.length > 0) {
            this.init();
        }
    }

    /**
     * Initializes event listeners for silence toggle buttons.
     */
    init() {
        this.buttons.forEach(button => {
            button.addEventListener('click', async (event) => {
                event.preventDefault();
                const url = button.getAttribute('data-url');
                const reviewId = button.getAttribute('data-review-id');

                if (!url || !reviewId) return;

                const response = await customFetch(url, { method: 'POST' });

                if (response) {
                    if (response.success) {
                        showToast('success', `Review ${response.silenced ? 'silenced' : 'unsilenced'} successfully!`);
                        this.updateReviewState(button, reviewId, response.silenced);
                    } else {
                        showToast('error', `Error toggling silence: ${response.error}`);
                    }
                }
            });
        });
    }

    /**
     * Updates the review's state in the UI based on the silence toggle response.
     * @param {HTMLElement} button - The button triggering the toggle.
     * @param {string} reviewId - The ID of the review.
     * @param {boolean} silenced - Whether the review is silenced.
     */
    updateReviewState(button, reviewId, silenced) {
        this.toggleButtonState(button, silenced);
        const reviewContainer = document.querySelector(`${this.reviewContainerSelector}[data-review-id="${reviewId}"]`);
        if (reviewContainer) {
            const commentElement = reviewContainer.querySelector('.review-comment');
            const silencedIndicator = reviewContainer.querySelector('.silenced-indicator');
            if (commentElement && silencedIndicator) {
                commentElement.classList.toggle('silenced', silenced);
                silencedIndicator.classList.toggle('d-flex', silenced);
                silencedIndicator.classList.toggle('d-none', !silenced);
            }
        }
    }

    /**
     * Toggles the state of the button based on the silenced state.
     * @param {HTMLElement} button - The button to update.
     * @param {boolean} silenced - Whether the review is silenced.
     */
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
}

/**
 * Handles activation and deactivation of products or variants.
 */
class ProductActivationHandler {
    constructor(buttonSelector) {
        this.buttons = document.querySelectorAll(buttonSelector);

        if (this.buttons.length > 0) {
            this.init();
        }
    }

    /**
     * Initializes event listeners for activation toggle buttons.
     */
    init() {
        this.buttons.forEach(button => {
            button.addEventListener("click", () => {
                const url = button.getAttribute("data-url");
                if (!url) return;

                // Include CSRF token explicitly
                const headers = {
                    "X-CSRFToken": this.getCSRFToken(),
                    "Content-Type": "application/json",
                };

                fetch(url, { method: "POST", headers })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            this.updateButtonState(button, data.active);
                            this.updateBadges(button, data);
                            showToast('success', `Successfully updated state!`);
                        } else {
                            showToast('error', `Failed to update state: ${data.error}`);
                        }
                    })
                    .catch(error => showToast('error', `Request failed: ${error}`));
            });
        });
    }

    /**
     * Updates the button's state based on activation status.
     * @param {HTMLElement} button - The button triggering the activation.
     * @param {boolean} isActive - Whether the product or variant is active.
     */
    updateButtonState(button, isActive) {
        const buttonText = button.textContent.trim().replace(/(Activate|Deactivate)/, "");
        button.classList.toggle("btn-success", !isActive);
        button.classList.toggle("btn-danger", isActive);
        button.textContent = `${isActive ? "Deactivate" : "Activate"} ${buttonText}`;
        button.setAttribute("data-active", isActive ? "true" : "false");
    }

    /**
     * Updates badges for products or variants based on activation state.
     * @param {HTMLElement} button - The button triggering the activation.
     * @param {Object} data - The response data containing activation state.
     */
    updateBadges(button, data) {
        const cardElement = button.closest(".product-card");
        if (!cardElement) return;

        const badgeContainer = cardElement.querySelector(".badge-container");
        if (!badgeContainer) return;

        const isProductButton = button.classList.contains("toggle-product-btn");
        const isSizeButton = button.classList.contains("toggle-variant-btn");

        if (isProductButton) {
            // Update Product Badge
            const productBadge = badgeContainer.querySelector(`#badge-product-${cardElement.querySelector('.size').id.split('-')[2]}`);
            if (productBadge) {
                productBadge.classList.toggle("badge-active", data.active);
                productBadge.classList.toggle("badge-inactive", !data.active);
                productBadge.textContent = `Product: ${data.active ? "Active" : "Inactive"}`;
            }
        }

        if (isSizeButton) {
            // Update Size/Variant Badge
            const variantBadge = badgeContainer.querySelector(`#badge-size-${cardElement.querySelector('.size').id.split('-')[2]}`);
            if (variantBadge) {
                variantBadge.classList.toggle("badge-active", data.active);
                variantBadge.classList.toggle("badge-inactive", !data.active);
                variantBadge.textContent = data.active ? "Size: Active" : "Size: Inactive";
            }
        }
    }

    /**
     * Retrieves the CSRF token for secure requests.
     * @returns {string} - The CSRF token.
     */
    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}

/**
 * Manages adding, editing, and saving of selectors like categories or sizes.
 */
class SelectorHandler {
    constructor(type) {
        this.type = type; // 'category' or 'size'
        this.lastAction = null; // Track whether last action was 'add' or 'edit'
        this.init();
    }

    /**
     * Initializes event listeners for add, edit, cancel, and save actions.
     */
    init() {
        this.addButton = document.querySelector(`#add_${this.type}`);
        this.editButton = document.querySelector(`#edit_${this.type}`);
        this.cancelButton = document.querySelector(`#cancel_${this.type}`);
        this.saveButton = document.querySelector(`#save_${this.type}`);

        if (this.addButton && this.editButton && this.cancelButton && this.saveButton) {
            this.setElements();

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
            this.saveButton.addEventListener("click", async (event) => {
                this.toggleInput(event, "save");
                await this.handleSave();
            });
        }
    }

    /**
     * Sets up references to selector and input elements.
     */
    setElements() {
        this.selectElement = document.querySelector(`.${this.type}`);
        this.inputElement = document.querySelector(`.${this.type}-input`);
    }

    /**
     * Toggles visibility of elements and handles input for add, edit, or cancel actions.
     * @param {Event} event - The triggering event.
     * @param {string} action - The action being performed ('add', 'edit', or 'cancel').
     */
    toggleInput(event, action) {
        this.setElements();
        const clickedButton = event.target;
        const parentSelectorGroup = clickedButton.closest(".selector-group");

        if (!this.selectElement || !this.inputElement) {
            return;
        }

        if (action === "edit") {
            const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
            this.inputElement.value = selectedOption ? selectedOption.textContent.trim() : "";
        } else if (action === "add") {
            this.inputElement.value = "";
            this.inputElement.placeholder = `New ${this.type}`;
        }

        // Toggle visibility
        this.selectElement.classList.toggle("d-none", action === "add" || action === "edit");
        this.inputElement.classList.toggle("d-none", action === "cancel" || action === "save");

        this.addButton.classList.toggle("d-none", action !== "cancel");
        this.editButton.classList.toggle("d-none", action !== "cancel");
        this.saveButton.classList.toggle("d-none", action === "cancel");
        this.cancelButton.classList.toggle("d-none", action === "cancel");

        if (action === "add" || action === "edit") {
            this.disableOtherInputs(parentSelectorGroup);
        } else {
            this.enableAllInputs();
        }

        if (!this.inputElement.classList.contains("d-none") && (action === "add" || action === "edit")) {
            this.inputElement.focus();
        }

        if (action === "save") {
            this.resetButtons();
        }
    }

    /**
     * Resets buttons and visibility to default state.
     */
    resetButtons() {
        this.addButton.classList.remove("d-none");
        this.editButton.classList.remove("d-none");
        this.saveButton.classList.add("d-none");
        this.cancelButton.classList.add("d-none");

        this.selectElement.classList.remove("d-none");
        this.inputElement.classList.add("d-none");

        this.enableAllInputs();
    }

    /**
     * Handles saving of the current input, either adding or editing.
     */
    async handleSave() {
        this.setElements();
        const newName = this.inputElement.value.trim();

        // Validate empty name
        if (!newName) {
            showToast('warning', 'Empty name is not valid.');
            return;
        }

        const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
        const currentValue = selectedOption ? selectedOption.value : null;

        // If no actual changes were made
        if (currentValue && selectedOption.textContent.trim() === newName) {
            showToast('info', 'No changes made.');
            return;
        }

        const productId = this.selectElement.id.split('-').pop();

        const payload = {
            action: this.lastAction,
            type: this.type,
            name: newName,
            current_value: currentValue,
            product_id: productId || '',
        };

        try {
            const response = await customFetch(`/products/${this.type}/save/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });

            if (response && response.success) {
                this.updateUI(response);
                showToast('success', `${this.type.charAt(0).toUpperCase() + this.type.slice(1)} saved successfully!`);

                const identifier = this.type === 'size' ? response.slug : response.id;
                this.updateURL(identifier);
            } else {
                showToast('error', `Unexpected error while saving ${this.type}.`);
            }
        } catch (error) {
            const errorMessage = error.message || 'An unexpected error occurred.';
            showToast('error', `Request failed: ${errorMessage}`);
        }
    }

    /**
     * Updates the UI after saving a selector.
     * @param {Object} data - The response data from the server.
     */
    updateUI(data) {
        this.setElements();

        if (this.lastAction === "add") {
            const newOption = document.createElement("option");
            newOption.value = this.type === 'size' ? data.slug : data.id;
            newOption.textContent = data.name;
            this.selectElement.add(newOption);
            this.selectElement.value = this.type === 'size' ? data.slug : data.id;
        } else if (this.lastAction === "edit") {
            const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
            if (selectedOption) {
                selectedOption.value = this.type === 'size' ? data.slug : data.id;
                selectedOption.textContent = data.name;
            }
        }

        this.resetButtons();
        this.lastAction = null;
    }

    /**
     * Updates the URL with the new selector identifier.
     * @param {string} identifier - The new identifier (slug or id).
     */
    updateURL(identifier) {
        const url = new URL(window.location.href);
        url.searchParams.set(this.type, identifier);
        window.history.replaceState(null, "", url);
    }

    /**
     * Disables inputs in other selector groups.
     * @param {HTMLElement} parentSelectorGroup - The parent group of the active selector.
     */
    disableOtherInputs(parentSelectorGroup) {
        document.querySelectorAll(".product-card input, .product-card button, .product-card select, .product-card textarea").forEach((element) => {
            if (!element.closest(".selector-group") || element.closest(".selector-group") !== parentSelectorGroup) {
                element.disabled = true;
            }
        });
    }

    /**
     * Enables all inputs in the product card.
     */
    enableAllInputs() {
        document.querySelectorAll(".product-card input, .product-card button, .product-card select, .product-card textarea").forEach((element) => {
            element.disabled = false;
        });
    }

    /**
     * Retrieves the CSRF token for secure requests.
     * @returns {string} - The CSRF token.
     */
    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}

/**
 * Handles saving of product and variant data, including image previews and submissions.
 */
class ProductSaveHandler {
    constructor(buttonSelector) {
        const cardElement = document.querySelector(".product-card");
        const sizeElement = cardElement.querySelector('.size');
        const dynamicPart = sizeElement ? sizeElement.id.split('-')[2] : '';

        this.previewElement = document.querySelector(`#product-image-${dynamicPart}`);
        this.saveButtons = document.querySelectorAll(buttonSelector);
        this.imageInput = document.querySelector('#id_image_path'); // Assuming image input ID
        this.imageFile = null; // Temporary store for the selected image

        if (this.saveButtons.length > 0) {
            this.init();
        }

        if (!this.previewElement) {
            showToast('error', `Preview element with ID ${dynamicPart} not found.`);
        }
    }

    /**
     * Initializes event listeners for image preview and save buttons.
     */
    init() {
        this.imageInput.addEventListener('change', this.previewImage.bind(this));
        this.saveButtons.forEach(button => {
            button.addEventListener('click', () => {
                const productId = button.getAttribute('data-product-id');
                const variantId = button.getAttribute('data-variant-id'); // Ensure variantId is retrieved correctly
                const url = button.getAttribute('data-url');
                this.saveProductAndVariant(productId, variantId, url);
            });
        });
    }

    /**
     * Previews the selected image in the corresponding preview element.
     * @param {Event} event - The change event triggered by the file input.
     */
    previewImage(event) {
        const file = event.target.files[0];
        if (file) {
            this.imageFile = file; // Store the selected image file
            const reader = new FileReader();

            reader.onload = (e) => {
                if (this.previewElement) {
                    this.previewElement.src = e.target.result; // Update the image preview
                } else {
                    showToast('error', 'Preview element not found.');
                }
            };

            reader.readAsDataURL(file);
        }
    }

    /**
     * Retrieves the CSRF token for secure requests.
     * @returns {string} - The CSRF token.
     */
    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    /**
     * Retrieves product data from the input fields.
     * @returns {Object} - An object containing product data.
     */
    getProductData() {
        const categorySelector = document.querySelector('[id^="category-select-"]');

        return {
            name: document.querySelector('#id_name').value,
            description: document.querySelector('#id_description').value,
            category: categorySelector ? categorySelector.value : null,
        };
    }

    /**
     * Retrieves variant data from the input fields.
     * @returns {Object|null} - An object containing variant data or null if validation fails.
     */
    getVariantData() {
        const sizeSelector = document.querySelector('.size');
        const productId = sizeSelector ? sizeSelector.id.split('-')[2] : null;
        const sizeElement = document.querySelector(`#size-select-${productId}`);

        if (sizeSelector) {
            const size = sizeElement ? sizeElement.value : null;
            let price = document.querySelector('#id_price')?.value || null;
            let stock = document.querySelector('#id_stock')?.value || null;
            const variantId = sizeElement ? sizeElement.getAttribute('data-variant-id') : null;

            if (!price) {
                price = 0;
            }

            if (!stock) {
                stock = 0;
            }

            if (!size) {
                showToast('warning', `Size data is incomplete, select a valid size`);
                return null;
            }

            return { size, price, stock, variantId }; // Include variantId in the payload
        }
        showToast('error', 'Size selector not found.');
        return null;
    }

    /**
     * Saves product and variant data, including handling image uploads.
     * @param {string} productId - The ID of the product.
     * @param {string} variantId - The ID of the variant.
     * @param {string} url - The endpoint URL for saving data.
     */
    saveProductAndVariant(productId, variantId, url) {
        const formData = new FormData();
        const productData = this.getProductData();

        if (!productData) {
            showToast('warning', 'Product data is incomplete. Please fill in all fields: name and category.');
            return;
        }

        // Add product data to form
        formData.append('product', JSON.stringify(productData));

        if (productId) {
            formData.append('product_id', productId);
        }

        // Handle variant data if provided
        if (variantId) {
            const variantData = this.getVariantData();
            if (!variantData) {
                return;
            }

            formData.append('variant_id', variantId || variantData.variantId);
            formData.append('variant', JSON.stringify({
                size: variantData.size,
                price: variantData.price,
                stock: variantData.stock,
                id: variantData.variantId || null, // Explicitly include the ID for updates
            }));
        }

        // Handle image upload if provided
        if (this.imageFile) {
            formData.append('image', this.imageFile, `${productData.name}.jpg`);
        }

        let errorToastShown = false; // Track if an error toast is already shown

        customFetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: formData,
        })
            .then(data => {
                if (data && data.success) {
                    showToast('success', 'Product saved successfully.');
                    if (data.redirect_url) {
                        setTimeout(() => window.location.href = data.redirect_url, 2000);
                    }
                }
            })
            .catch(error => {
                if (!errorToastShown) {
                    showToast('error', `Request failed: ${error.message}`);
                }
            });
    }
}

// Initialize handlers on DOM load
document.addEventListener('DOMContentLoaded', () => {
    const productCardHandler = new ProductCardHandler();
    const starRatingHandler = new StarRatingHandler('#star-rating', '#id_rating');
    const reviewFilterHandler = new ReviewFilterHandler('.filter', '.review-container', '#no-reviews-message');
    const reviewSilenceHandler = new ReviewSilenceHandler('.toggle-silence-btn', '.review-container');
    const productActivationHandler = new ProductActivationHandler('.toggle-product-btn');
    const variantActivationHandler = new ProductActivationHandler('.toggle-variant-btn');
    const categoryHandler = new SelectorHandler("category");
    const sizeHandler = new SelectorHandler("size");
    const productSaveHandler = new ProductSaveHandler('.save-product-btn');

    window.productCardHandler = productCardHandler;
    window.starRatingHandler = starRatingHandler;
    window.reviewFilterHandler = reviewFilterHandler;
    window.reviewSilenceHandler = reviewSilenceHandler;
    window.productActivationHandler = productActivationHandler;
    window.variantActivationHandler = variantActivationHandler;
    window.categoryHandler = categoryHandler;
    window.sizeHandler = sizeHandler;
    window.productSaveHandler = productSaveHandler;
});
