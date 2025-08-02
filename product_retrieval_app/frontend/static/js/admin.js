// Admin panel functionality

class AdminManager {
    constructor() {
        this.addProductModal = new bootstrap.Modal('#addProductModal');
        this.addProductForm = $('#addProductForm');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Add product form submission
        this.addProductForm.on('submit', (e) => {
            e.preventDefault();
            this.addProduct();
        });
    }
    
    async addProduct() {
        const formData = {
            name: $('#productName').val().trim(),
            brand: $('#productBrand').val().trim(),
            categories: $('#productCategories').val().trim(),
            ingredients: $('#productIngredients').val().trim(),
            manufacturer: $('#productManufacturer').val().trim(),
            manufacturerNumber: $('#manufacturerNumber').val().trim()
        };
        
        // Validation
        if (!formData.name) {
            app.showToast('Product name is required', 'warning');
            return;
        }
        
        app.showLoading(true);
        
        try {
            const response = await fetch('/api/products', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                app.showToast('Product added successfully', 'success');
                this.addProductModal.hide();
                this.clearForm();
                this.refreshProducts();
            } else {
                app.showToast(data.error || 'Failed to add product', 'danger');
            }
        } catch (error) {
            console.error('Add product error:', error);
            app.showToast('Network error occurred', 'danger');
        } finally {
            app.showLoading(false);
        }
    }
    
    clearForm() {
        this.addProductForm[0].reset();
    }
    
    async refreshProducts() {
        // Reload the page to show updated products
        window.location.reload();
    }
}

// Global functions for admin panel
function showAddProductModal() {
    const modal = new bootstrap.Modal('#addProductModal');
    modal.show();
}

function showBulkUploadModal() {
    app.showToast('Bulk upload functionality coming soon', 'info');
}

function exportData() {
    app.showToast('Export functionality coming soon', 'info');
}

function rebuildIndex() {
    if (confirm('Are you sure you want to rebuild the search index? This may take some time.')) {
        app.showToast('Index rebuild functionality coming soon', 'info');
    }
}

async function editProduct(productId) {
    app.showToast(`Edit functionality for product ${productId} coming soon`, 'info');
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }
    
    app.showLoading(true);
    
    try {
        const response = await fetch(`/api/products/${productId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            app.showToast('Product deleted successfully', 'success');
            window.location.reload();
        } else {
            app.showToast(data.error || 'Failed to delete product', 'danger');
        }
    } catch (error) {
        console.error('Delete product error:', error);
        app.showToast('Network error occurred', 'danger');
    } finally {
        app.showLoading(false);
    }
}

function refreshProducts() {
    window.location.reload();
}

// Initialize admin manager when document is ready
$(document).ready(() => {
    const adminManager = new AdminManager();
});