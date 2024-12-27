/**
 * Utility class to handle CSRF tokens.
 */
class CSRFTokenHandler {
    /**
     * Retrieves the CSRF token from the DOM.
     * @returns {string} The CSRF token value, or an empty string if not found.
     */
    static getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : '';
    }
}

/**
 * Class to handle removing items via button clicks.
 */
class RemoveItemHandler {
    /**
     * Initializes the RemoveItemHandler instance.
     * @param {string} buttonSelector - CSS selector for the buttons.
     */
    constructor(buttonSelector) {
        this.buttons = document.querySelectorAll(buttonSelector);
        if (this.buttons.length > 0) {
            this.init();
        }
    }

    /**
     * Adds click event listeners to the buttons.
     */
    init() {
        this.buttons.forEach((button) => {
            button.addEventListener('click', (event) => this.handleRemove(event));
        });
    }

    /**
     * Handles the removal of an item when a button is clicked.
     * @param {Event} event - The click event.
     */
    async handleRemove(event) {
        const button = event.target.closest('button');
        const url = button.getAttribute('data-url');
        const size = button.getAttribute('data-size');

        if (!url || !size) {
            showToast('error', 'Invalid item data. Please try again or refresh the page.');
            return;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRFTokenHandler.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ size }),
            });

            const data = await response.json();
            if (data.success) {
                showToast('success', data.message || 'Item removed successfully.');
                setTimeout(() => location.reload(), 500);
            } else {
                showToast('error', data.error || 'Failed to remove the item.');
            }
        } catch (error) {
            showToast('error', 'An unexpected error occurred.');
        }
    }
}

/**
 * Class to handle updating items via button clicks.
 */
class UpdateItemHandler {
    /**
     * Initializes the UpdateItemHandler instance.
     * @param {string} buttonSelector - CSS selector for the update buttons.
     * @param {string} quantitySelector - CSS selector for the quantity inputs.
     */
    constructor(buttonSelector, quantitySelector) {
        this.buttons = document.querySelectorAll(buttonSelector);
        this.quantitySelector = quantitySelector;

        if (this.buttons.length > 0) {
            this.init();
        }
    }

    /**
     * Adds click event listeners to the update buttons.
     */
    init() {
        this.buttons.forEach((button) => {
            button.addEventListener('click', (event) => this.handleUpdate(event));
        });
    }

    /**
     * Handles updating an item's quantity when a button is clicked.
     * @param {Event} event - The click event.
     */
    async handleUpdate(event) {
        const button = event.target.closest('button');
        const url = button.getAttribute('data-url');
        const itemId = button.getAttribute('data-item-id');
        const size = button.getAttribute('data-size');

        const quantityInput = document.querySelector(
            `${this.quantitySelector}[data-item-id="${itemId}"][data-size="${size}"]`
        );

        if (!quantityInput) {
            showToast('error', 'Unable to find the quantity input field. Please try again.');
            return;
        }

        const quantity = parseInt(quantityInput.value, 10);

        if (!url || isNaN(quantity) || quantity <= 0) {
            showToast('error', 'Invalid item data. Please ensure the quantity is correct.');
            return;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': CSRFTokenHandler.getCSRFToken(),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ size, quantity }),
            });

            const data = await response.json();
            if (data.success) {
                showToast('success', data.message || 'Cart updated successfully.');
                setTimeout(() => location.reload(), 500);
            } else {
                showToast('error', data.error || 'Failed to update the cart.');
            }
        } catch (error) {
            showToast('error', 'An unexpected error occurred.');
        }
    }
}

/**
 * Class to manage the cart, handling quantity changes and button visibility.
 */
class CartHandler {
    /**
     * Initializes the CartHandler instance.
     * @param {string} quantitySelector - CSS selector for quantity inputs.
     * @param {string} updateButtonSelector - CSS selector for update buttons.
     * @param {string} deleteButtonSelector - CSS selector for delete buttons.
     */
    constructor(quantitySelector, updateButtonSelector, deleteButtonSelector) {
        this.quantitySelector = quantitySelector;
        this.updateButtonSelector = updateButtonSelector;
        this.deleteButtonSelector = deleteButtonSelector;
        this.init();
    }

    /**
     * Adds input event listeners to quantity fields.
     */
    init() {
        const quantityInputs = document.querySelectorAll(this.quantitySelector);
        quantityInputs.forEach(input => {
            input.addEventListener('input', (event) => this.handleQuantityChange(event));
        });
    }

    /**
     * Handles changes to the quantity input fields.
     * @param {Event} event - The input event.
     */
    handleQuantityChange(event) {
        const inputField = event.target;
        const initialQuantity = parseInt(inputField.getAttribute('data-initial-quantity'), 10);
        const currentQuantity = parseInt(inputField.value, 10);

        const cardElement = inputField.closest('.row');
        const updateButton = cardElement.querySelector(this.updateButtonSelector);
        const deleteButton = cardElement.querySelector(this.deleteButtonSelector);

        if (currentQuantity !== initialQuantity && currentQuantity > 0) {
            updateButton.classList.remove('d-none');
            deleteButton.classList.add('d-none');
        } else {
            updateButton.classList.add('d-none');
            deleteButton.classList.remove('d-none');
        }
    }
}

/**
 * Initializes all event listeners and handlers once the DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', () => {
    const cartHandler = new CartHandler('.cart-quantity', '.btn-update', '.btn-remove');
    const removeItemHandler = new RemoveItemHandler('.btn-remove');
    const updateItemHandler = new UpdateItemHandler('.btn-update', 'input[type="number"]');

    window.cartHandler = cartHandler;
    window.removeItemHandler = removeItemHandler;
    window.updateItemHandler = updateItemHandler;
});

