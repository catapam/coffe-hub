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

        this.updatePriceDisplay(cardElement, price, stock);
        this.updateBuyButton(cardElement, stock);
        this.updateStockInput(cardElement, stock);
    }

    updateStockInput(cardElement, stock) {
        let stockInput = cardElement.querySelector(`#id_stock`);
        const quantityInput = cardElement.querySelector(`#quantity-select-${cardElement.querySelector('.size').id.split('-')[2]}`);

        if (stockInput) {
            stockInput.value = stock;
        } else if (quantityInput) {
            quantityInput.value = 1;
        } else {
            stockInput = `#stock-select-${cardElement.querySelector('.size').id.split('-')[2]}`;
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
    }

    handleMouseOut() {
        this.stars.forEach(s => s.classList.remove('hovered'));
    }

    updateStars(value, className) {
        this.stars.forEach(s => {
            const starValue = parseInt(s.getAttribute('data-value'), 10);
            if (className === 'filled') {
                s.classList.toggle('filled', starValue <= value);
            } else if (className === 'hovered') {
                s.classList.toggle('hovered', starValue <= value);
            }
        });
    }
}

class ReviewFilterHandler {
    constructor(filterSelector, reviewSelector) {
        this.filters = document.querySelectorAll(filterSelector);
        this.reviews = document.querySelectorAll(reviewSelector);

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
        this.reviews.forEach(review => {
            const reviewRating = parseInt(review.getAttribute("data-rating"), 10);

            if (filterValue === "all" || reviewRating === filterValue) {
                review.style.display = "block";
            } else {
                review.style.display = "none";
            }
        });
    }
}

class ReviewActionHandler {
    constructor(actionSelector) {
        this.actions = document.querySelectorAll(actionSelector);
        if (this.actions.length > 0) {
            this.init();
        }
    }

    init() {
        this.actions.forEach(action => {
            action.addEventListener('click', (event) => {
                event.preventDefault();
                const reviewId = action.dataset.reviewId;
                const isSilenced = action.dataset.silenced === "true";

                // Send an AJAX request to toggle silenced state
                fetch(`/reviews/toggle/${reviewId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ silenced: !isSilenced })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Update the button UI based on new state
                        action.dataset.silenced = (!isSilenced).toString();
                        action.classList.toggle("btn-primary", !isSilenced);
                        action.classList.toggle("btn-secondary", isSilenced);
                        action.innerHTML = isSilenced
                            ? '<i class="fa-solid fa-comment-slash"></i>'
                            : '<i class="fa-solid fa-comment"></i>';
                    } else {
                        console.error("Failed to toggle silenced state.");
                    }
                })
                .catch(error => console.error("Error toggling silenced state:", error));
            });
        });
    }
}

// Initialize handlers on DOM load
document.addEventListener("DOMContentLoaded", () => {
    new ProductCardHandler();
    new StarRatingHandler('#star-rating', 'id_rating');
    new ReviewFilterHandler('.filter', '.review');
    new ReviewActionHandler('.toggle-silence');
});
