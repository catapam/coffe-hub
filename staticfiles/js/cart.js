class CSRFTokenHandler {
    static getCSRFToken() {
        const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : '';
    }
}

class RemoveItemHandler {
    constructor(buttonSelector) {
        this.buttons = document.querySelectorAll(buttonSelector);
        if (this.buttons.length > 0) {
            this.init();
        }
    }

    init() {
        this.buttons.forEach((button) => {
            button.addEventListener('click', (event) => this.handleRemove(event));
        });
    }

    async handleRemove(event) {
        const button = event.target.closest('button');
        const url = button.getAttribute('data-url');
        const size = button.getAttribute('data-size');

        if (!url || !size) {
            console.error('Invalid item data:', { url, size });
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
                console.error('Server error on remove:', data);
                showToast('error', data.error || 'Failed to remove the item.');
            }
        } catch (error) {
            console.error('Error during remove request:', error);
            showToast('error', 'An unexpected error occurred.');
        }
    }
}

class UpdateItemHandler {
    constructor(buttonSelector, quantitySelector) {
        this.buttons = document.querySelectorAll(buttonSelector);
        this.quantitySelector = quantitySelector;

        if (this.buttons.length > 0) {
            this.init();
        }
    }

    init() {
        this.buttons.forEach((button) => {
            button.addEventListener('click', (event) => this.handleUpdate(event));
        });
    }

    async handleUpdate(event) {
        const button = event.target.closest('button');
        const url = button.getAttribute('data-url');
        const itemId = button.getAttribute('data-item-id');
        const size = button.getAttribute('data-size');

        const quantityInput = document.querySelector(
            `${this.quantitySelector}[data-item-id="${itemId}"][data-size="${size}"]`
        );

        if (!quantityInput) {
            console.error('Missing quantity input for item:', { itemId, size });
            showToast('error', 'Unable to find the quantity input field. Please try again.');
            return;
        }

        const quantity = parseInt(quantityInput.value, 10);

        if (!url || isNaN(quantity) || quantity <= 0) {
            console.error('Invalid update data:', { url, itemId, size, quantity });
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
                console.error('Server error on update:', data);
                showToast('error', data.error || 'Failed to update the cart.');
            }
        } catch (error) {
            console.error('Error during update request:', error);
            showToast('error', 'An unexpected error occurred.');
        }
    }
}

class CartHandler {
    constructor(quantitySelector, updateButtonSelector, deleteButtonSelector) {
        this.quantitySelector = quantitySelector;
        this.updateButtonSelector = updateButtonSelector;
        this.deleteButtonSelector = deleteButtonSelector;
        this.init();
    }

    init() {
        const quantityInputs = document.querySelectorAll(this.quantitySelector);
        quantityInputs.forEach(input => {
            input.addEventListener('input', (event) => this.handleQuantityChange(event));
        });
    }

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

document.addEventListener('DOMContentLoaded', () => {
    new CartHandler('.cart-quantity', '.btn-update', '.btn-remove');
    new RemoveItemHandler('.btn-remove');
    new UpdateItemHandler('.btn-update', 'input[type="number"]');
});
