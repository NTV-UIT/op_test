// Product Retrieval System - Main JavaScript

class ProductRetrievalApp {
    constructor() {
        this.init();
    }
    
    init() {
        // Initialize app
        this.setupEventListeners();
        this.showNotifications();
    }
    
    setupEventListeners() {
        // Global event listeners
        $(document).ready(() => {
            // Initialize tooltips
            $('[data-bs-toggle="tooltip"]').tooltip();
            
            // Initialize any other components
            this.initializeComponents();
        });
    }
    
    initializeComponents() {
        // Add any global component initialization here
        console.log('ProductRetrievalApp initialized');
    }
    
    showNotifications() {
        // Show any system notifications
        const urlParams = new URLSearchParams(window.location.search);
        const message = urlParams.get('message');
        const type = urlParams.get('type') || 'info';
        
        if (message) {
            this.showToast(message, type);
        }
    }
    
    showToast(message, type = 'info') {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        $('#toastContainer').html(toastHtml);
        const toast = new bootstrap.Toast($('.toast')[0]);
        toast.show();
    }
    
    showLoading(show = true) {
        if (show) {
            $('body').append(`
                <div class="loading-overlay" id="loadingOverlay">
                    <div class="loading-content">
                        <div class="spinner-border text-primary mb-3" role="status"></div>
                        <p>Processing...</p>
                    </div>
                </div>
            `);
        } else {
            $('#loadingOverlay').remove();
        }
    }
}

// Initialize app
const app = new ProductRetrievalApp();