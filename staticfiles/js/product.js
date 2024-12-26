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

        this.handleBuyButton();
        this.handleReviewSubmission()

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
        const saveButton = cardElement.querySelector(`.save-product-btn`);
        
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
            if(saveButton){
                saveButton.setAttribute("data-variant-id", `${variantId}`)
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
            quantityInput.max = stock;
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
                            showToast('success', `${data.message}`)
                        } else {
                            showToast('error', `${data.error}`)
                        }
                    })
                    .catch(error => showToast('error', `${error.message}`));
            });
        });
    }

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
    
    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }    
}

class StarRatingHandler {
    constructor(starContainerSelector, ratingInputSelector) {
        this.starContainer = document.querySelector(starContainerSelector);
        this.ratingInput = document.querySelector(ratingInputSelector);
        
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
        let currentRating = parseInt(this.ratingInput?.value || '0', 10);
 
        if (currentRating === chosenValue && currentRating > 0) {
            currentRating -= 1;  // Allow deselecting the star
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

class ReviewFilterHandler {
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

    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}

class SelectorHandler {
    constructor(type) {
        this.type = type; // 'category' or 'size'
        this.lastAction = null; // Track whether last action was 'add' or 'edit'
        this.init();
    }

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

    setElements() {
        this.selectElement = document.querySelector(`.${this.type}`);
        this.inputElement = document.querySelector(`.${this.type}-input`);
    }

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

    resetButtons() {
        this.addButton.classList.remove("d-none");
        this.editButton.classList.remove("d-none");
        this.saveButton.classList.add("d-none");
        this.cancelButton.classList.add("d-none");

        this.selectElement.classList.remove("d-none");
        this.inputElement.classList.add("d-none");

        this.enableAllInputs();
    }

    async handleSave() {
        this.setElements();
        const newName = this.inputElement.value.trim();
        if (!newName) {
            return;
        }

        const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
        const currentValue = selectedOption ? selectedOption.value : null;

        const productId = this.selectElement.id.split('-').pop(); // Restore direct product_id extraction

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

                // Use `slug` for size, `id` for category in URL update
                const identifier = this.type === 'size' ? response.slug : response.id;
                this.updateURL(identifier);
            } else if (response.error) {
                showToast('error', `Error saving ${this.type}: ${response.error}`);
            } else {
                showToast('error', `Unexpected error while saving ${this.type}.`);
            }
        } catch (error) {
            const errorMessage = error.message || 'An unexpected error occurred.';
            showToast('error', `Request failed: ${errorMessage}`);
        }
    }

    updateUI(data) {
        this.setElements();

        if (this.lastAction === "add") {
            const newOption = document.createElement("option");
            newOption.value = this.type === 'size' ? data.slug : data.id; // Use slug for size, id for category
            newOption.textContent = data.name;
            this.selectElement.add(newOption);
            this.selectElement.value = this.type === 'size' ? data.slug : data.id; // Automatically select the new option
        } else if (this.lastAction === "edit") {
            const selectedOption = this.selectElement.options[this.selectElement.selectedIndex];
            if (selectedOption) {
                selectedOption.value = this.type === 'size' ? data.slug : data.id; // Use slug for size, id for category
                selectedOption.textContent = data.name;
            }
        }

        this.resetButtons();
        this.lastAction = null;
    }

    updateURL(identifier) {
        const url = new URL(window.location.href);
        url.searchParams.set(this.type, identifier); // Use slug for size, id for category
        window.history.replaceState(null, "", url);
    }

    disableOtherInputs(parentSelectorGroup) {
        document.querySelectorAll(".product-card input, .product-card button, .product-card select, .product-card textarea").forEach((element) => {
            if (!element.closest(".selector-group") || element.closest(".selector-group") !== parentSelectorGroup) {
                element.disabled = true;
            }
        });
    }

    enableAllInputs() {
        document.querySelectorAll(".product-card input, .product-card button, .product-card select, .product-card textarea").forEach((element) => {
            element.disabled = false;
        });
    }

    getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }
}

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
            showToast('error', `Preview element with ID ${dynamicPart} not found.`)
        }
    }

    init() {
        this.imageInput.addEventListener('change', this.previewImage.bind(this));
        this.saveButtons.forEach(button => {
            button.addEventListener('click', () => {
                const productId = button.getAttribute('data-product-id');
                const variantId = button.getAttribute('data-variant-id'); // Ensure variantId is retrieved correctly
                const url = button.getAttribute('data-url');
                console.log = productId, variantId, url
                this.saveProductAndVariant(productId, variantId, url);
            });
        });
    }

    previewImage(event) {
        const file = event.target.files[0];
        if (file) {
            this.imageFile = file; // Store the selected image file
            const reader = new FileReader();
    
            reader.onload = (e) => {
                if (this.previewElement) {
                    this.previewElement.src = e.target.result; // Update the image preview
                } else {
                    showToast('error', 'Preview element not found.')
                }
            };
    
            reader.readAsDataURL(file);
        }
    }

    getCSRFToken() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }

    getProductData() {
        const categorySelector = document.querySelector('[id^="category-select-"]');

        return {
            name: document.querySelector('#id_name').value,
            description: document.querySelector('#id_description').value,
            category: categorySelector ? categorySelector.value : null,
        };
    }

    getVariantData() {
        const sizeSelector = document.querySelector('.size');
        const productId = sizeSelector ? sizeSelector.id.split('-')[2] : null;
        const sizeElement = document.querySelector(`#size-select-${productId}`);

        if (sizeSelector) {
            const size = sizeElement ? sizeElement.value : null;
            const price = document.querySelector('#id_price')?.value || null;
            const stock = document.querySelector('#id_stock')?.value || null;
            const variantId = sizeElement ? sizeElement.getAttribute('data-variant-id') : null;

            if (!size || !price || !stock) {
                showToast('warning', `Size data is incomplete: { size, price, stock }`)
                return null;
            }

            return { size, price, stock, variantId }; // Include variantId in the payload
        }
        showToast('error', 'Size selector not found.')
        return null;
    }

    saveProductAndVariant(productId, variantId, url) {
        const formData = new FormData();
        const productData = this.getProductData();
    
        if (!productData) {
            showToast('warning', `Product data is incomplete. Please fill in all fields.`);
            return;
        }

        if (variantId){
            const variantData = this.getVariantData();
            if (!variantData) {
                showToast('warning', `Size data is incomplete. Please fill in all fields.`);
                return;
            }

            if (variantId || variantData.variantId) {
                formData.append('variant_id', variantId || variantData.variantId); // Use the variantId for updates
            }

            formData.append('variant', JSON.stringify({
                size: variantData.size,
                price: variantData.price,
                stock: variantData.stock,
                id: variantData.variantId || null, // Explicitly include the ID for updates
            }));
        }
    
        if (productId) formData.append('product_id', productId);

        formData.append('product', JSON.stringify(productData));
    
        if (this.imageFile) {
            formData.append('image', this.imageFile, `${productData.name}.jpg`);
        }    
        customFetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': this.getCSRFToken(),
            },
            body: formData,
        })
            .then(data => {
                if (data.success) {
                    showToast('success', 'Product saved successfully.');
                    if (data.redirect_url) {
                        setTimeout(() => window.location.href = data.redirect_url, 2000);
                    }
                } else if (data.errors) {
                    Object.entries(data.errors).forEach(([field, errors]) => {
                        errors.forEach(error => showToast('error', `${field}: ${error}`));
                    });
                } else if (data.error) {
                    showToast('error', data.error);
                }
            })
            .catch(error => {
                showToast('error', `Request failed: ${error.message}`);
            });    
    }    
}

// Initialize handlers on DOM load
document.addEventListener('DOMContentLoaded', () => {
    new ProductCardHandler();
    new StarRatingHandler('#star-rating', '#id_rating');
    new ReviewFilterHandler('.filter', '.review-container', '#no-reviews-message');
    new ReviewSilenceHandler('.toggle-silence-btn', '.review-container');
    new ProductActivationHandler('.toggle-product-btn');
    new ProductActivationHandler('.toggle-variant-btn');
    new SelectorHandler("category");
    new SelectorHandler("size");
    new ProductSaveHandler('.save-product-btn');
});