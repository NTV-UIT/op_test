// API Configuration
const API_BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    health: '/api/health',
    search: '/api/search',
    products: '/api/products',
    stats: '/api/stats'
};

// Global state
let currentPage = 1;
let currentSearchResults = [];
let searchStartTime = 0;

// DOM Elements
const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const searchMethod = document.getElementById('search-method');
const resultCount = document.getElementById('result-count');
const loading = document.getElementById('loading');
const searchResults = document.getElementById('search-results');
const browseSection = document.getElementById('browse-section');
const resultsContainer = document.getElementById('results-container');
const productsContainer = document.getElementById('products-container');
const loadProductsBtn = document.getElementById('load-products');
const filterInput = document.getElementById('filter-input');
const pagination = document.getElementById('pagination');
const prevPageBtn = document.getElementById('prev-page');
const nextPageBtn = document.getElementById('next-page');
const pageInfo = document.getElementById('page-info');
const productModal = document.getElementById('product-modal');
const closeModal = document.getElementById('close-modal');
const modalTitle = document.getElementById('modal-title');
const modalBody = document.getElementById('modal-body');
const toastContainer = document.getElementById('toast-container');
const apiStatus = document.getElementById('api-status');
const totalProducts = document.getElementById('total-products');
const resultsCount = document.getElementById('results-count');
const searchTime = document.getElementById('search-time');

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
});

// App initialization
async function initializeApp() {
    await checkAPIHealth();
    await loadStatistics();
    showToast('Application initialized successfully!', 'success');
}

// Event listeners
function setupEventListeners() {
    // Search functionality
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Auto-clear search results when input is empty
    searchInput.addEventListener('input', function() {
        if (this.value.trim() === '') {
            clearSearchResults();
        }
    });
    
    // Browse products
    loadProductsBtn.addEventListener('click', loadProducts);
    filterInput.addEventListener('input', debounce(filterProducts, 300));
    
    // Pagination
    prevPageBtn.addEventListener('click', () => changePage(currentPage - 1));
    nextPageBtn.addEventListener('click', () => changePage(currentPage + 1));
    
    // Modal
    closeModal.addEventListener('click', hideModal);
    productModal.addEventListener('click', function(e) {
        if (e.target === productModal) {
            hideModal();
        }
    });
    
    // CRUD functionality
    setupCRUDEventListeners();
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideModal();
            closeProductFormModal();
        }
        if (e.ctrlKey && e.key === '/') {
            e.preventDefault();
            searchInput.focus();
        }
    });
}

// API Functions
async function makeAPICall(endpoint, options = {}) {
    try {
        const response = await fetch(API_BASE_URL + endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        showToast(`API Error: ${error.message}`, 'error');
        throw error;
    }
}

async function checkAPIHealth() {
    try {
        const response = await makeAPICall(API_ENDPOINTS.health);
        if (response.status === 'healthy') {
            apiStatus.textContent = 'Online';
            apiStatus.className = 'stat-value online';
            apiStatus.style.color = '#28a745';
        } else {
            throw new Error('API not healthy');
        }
    } catch (error) {
        apiStatus.textContent = 'Offline';
        apiStatus.className = 'stat-value offline';
        apiStatus.style.color = '#dc3545';
    }
}

async function loadStatistics() {
    try {
        const response = await makeAPICall(API_ENDPOINTS.stats);
        if (response.success) {
            totalProducts.textContent = response.statistics.total_products.toLocaleString();
        }
    } catch (error) {
        totalProducts.textContent = 'Error';
    }
}

// Search functionality
async function performSearch() {
    const query = searchInput.value.trim();
    if (!query) {
        showToast('Please enter a search query', 'warning');
        searchInput.focus();
        return;
    }
    
    const method = searchMethod.value;
    const topK = parseInt(resultCount.value);
    
    // Show loading state
    showLoading(true);
    hideSection(browseSection);
    searchStartTime = performance.now();
    
    try {
        const response = await makeAPICall(API_ENDPOINTS.search, {
            method: 'POST',
            body: JSON.stringify({
                query: query,
                method: method,
                top_k: topK
            })
        });
        
        if (response.success) {
            currentSearchResults = response.results;
            displaySearchResults(response);
            
            const searchDuration = ((performance.now() - searchStartTime) / 1000).toFixed(2);
            searchTime.textContent = `(${searchDuration}s)`;
            
            showToast(`Found ${response.results.length} results`, 'success');
        } else {
            throw new Error(response.error || 'Search failed');
        }
    } catch (error) {
        showToast(`Search failed: ${error.message}`, 'error');
        showLoading(false);
    }
}

function displaySearchResults(response) {
    showLoading(false);
    showSection(searchResults);
    showSection(browseSection);  // Hiển thị lại Browse Products section
    
    resultsCount.textContent = `${response.total_results} results for "${response.query}"`;
    
    resultsContainer.innerHTML = '';
    
    if (response.results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h3>No results found</h3>
                <p>Try adjusting your search query or search method.</p>
            </div>
        `;
        return;
    }
    
    response.results.forEach(product => {
        const productCard = createProductCard(product, true);
        resultsContainer.appendChild(productCard);
    });
}

// Product browsing
async function loadProducts(page = 1, search = '') {
    try {
        showLoading(true);
        
        const params = new URLSearchParams({
            page: page,
            limit: 20
        });
        
        if (search) {
            params.append('search', search);
        }
        
        const response = await makeAPICall(`${API_ENDPOINTS.products}?${params}`);
        
        if (response.success) {
            displayProducts(response);
            updatePagination(response.pagination);
            currentPage = page;
            
            showLoading(false);
            showSection(browseSection);
            hideSection(searchResults);
            
            showToast(`Loaded ${response.products.length} products`, 'success');
        } else {
            throw new Error(response.error || 'Failed to load products');
        }
    } catch (error) {
        showLoading(false);
        showToast(`Failed to load products: ${error.message}`, 'error');
    }
}

function displayProducts(response) {
    productsContainer.innerHTML = '';
    
    if (response.products.length === 0) {
        productsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-box-open"></i>
                <h3>No products found</h3>
                <p>Try adjusting your filter or load all products.</p>
            </div>
        `;
        return;
    }
    
    response.products.forEach(product => {
        const productCard = createProductCard(product, false);
        productsContainer.appendChild(productCard);
    });
}

// Create product card
function createProductCard(product, showScore = false) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.onclick = (e) => {
        // Don't show detail if clicking on action buttons
        if (!e.target.closest('.product-actions')) {
            showProductDetail(product);
        }
    };
    
    const scoreHtml = showScore ? `<div class="product-score">${(product.score * 100).toFixed(1)}%</div>` : '';
    
    card.innerHTML = `
        <div class="product-header">
            <div class="product-name">${escapeHtml(product.name || 'N/A')}</div>
            ${scoreHtml}
        </div>
        <div class="product-brand">${escapeHtml(product.brand || 'N/A')}</div>
        <div class="product-info">
            <div><strong>Categories:</strong> ${escapeHtml(product.categories || 'N/A')}</div>
            <div><strong>Manufacturer:</strong> ${escapeHtml(product.manufacturer || 'N/A')}</div>
            ${product.ingredients ? `
                <div class="product-ingredients">
                    <strong>Ingredients:</strong> ${truncateText(escapeHtml(product.ingredients), 100)}
                </div>
            ` : ''}
        </div>
        <div class="product-actions">
            <button class="btn-small btn-edit" onclick="openEditProductModal(${product.id}); event.stopPropagation();">
                <i class="fas fa-edit"></i> Edit
            </button>
            <button class="btn-small btn-delete" onclick="deleteProduct(${product.id}, '${escapeHtml(product.name || '')}'); event.stopPropagation();">
                <i class="fas fa-trash"></i> Delete
            </button>
        </div>
    `;
    
    return card;
}

// Product detail modal
async function showProductDetail(product) {
    try {
        // If we only have basic product info, fetch full details
        if (typeof product.id !== 'undefined') {
            const response = await makeAPICall(`${API_ENDPOINTS.products}/${product.id}`);
            if (response.success) {
                product = response.product;
            }
        }
        
        modalTitle.textContent = product.name || 'Product Details';
        modalBody.innerHTML = `
            <div class="product-detail">
                <div class="detail-section">
                    <h4><i class="fas fa-tag"></i> Basic Information</h4>
                    <table class="detail-table">
                        <tr><td><strong>Name:</strong></td><td>${escapeHtml(product.name || 'N/A')}</td></tr>
                        <tr><td><strong>Brand:</strong></td><td>${escapeHtml(product.brand || 'N/A')}</td></tr>
                        <tr><td><strong>Categories:</strong></td><td>${escapeHtml(product.categories || 'N/A')}</td></tr>
                        <tr><td><strong>Manufacturer:</strong></td><td>${escapeHtml(product.manufacturer || 'N/A')}</td></tr>
                        <tr><td><strong>Manufacturer Code:</strong></td><td>${escapeHtml(product.manufacturerNumber || 'N/A')}</td></tr>
                    </table>
                </div>
                
                ${product.ingredients ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-list"></i> Ingredients</h4>
                        <div class="ingredients-text">${escapeHtml(product.ingredients)}</div>
                    </div>
                ` : ''}
                
                ${product.score ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-chart-line"></i> Search Relevance</h4>
                        <div class="score-display">
                            <div class="score-bar">
                                <div class="score-fill" style="width: ${product.score * 100}%"></div>
                            </div>
                            <span class="score-text">${(product.score * 100).toFixed(1)}% match</span>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        showSection(productModal);
    } catch (error) {
        showToast(`Failed to load product details: ${error.message}`, 'error');
    }
}

// Pagination
function updatePagination(paginationData) {
    if (paginationData.total_pages <= 1) {
        hideSection(pagination);
        return;
    }
    
    showSection(pagination);
    
    pageInfo.textContent = `Page ${paginationData.page} of ${paginationData.total_pages} (${paginationData.total_count} total)`;
    
    prevPageBtn.disabled = !paginationData.has_prev;
    nextPageBtn.disabled = !paginationData.has_next;
}

function changePage(page) {
    const search = filterInput.value.trim();
    loadProducts(page, search);
}

// Filter functionality
function filterProducts() {
    const search = filterInput.value.trim();
    currentPage = 1;
    loadProducts(1, search);
}

// Utility functions
function showLoading(show = true) {
    if (show) {
        showSection(loading);
    } else {
        hideSection(loading);
    }
}

function hideLoading() {
    hideSection(loading);
}

function showSection(element) {
    element.classList.remove('hidden');
}

function hideSection(element) {
    element.classList.add('hidden');
}

function hideModal(modal = productModal) {
    hideSection(modal);
}

function showModal(modal) {
    showSection(modal);
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span>${escapeHtml(message)}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Add some CSS for elements created by JS
const additionalCSS = `
    .no-results {
        text-align: center;
        padding: 60px 20px;
        color: #666;
        grid-column: 1 / -1;
    }
    
    .no-results i {
        font-size: 3rem;
        color: #ddd;
        margin-bottom: 20px;
    }
    
    .no-results h3 {
        font-size: 1.3rem;
        margin-bottom: 10px;
        color: #333;
    }
    
    .detail-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    
    .detail-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #f0f0f0;
        vertical-align: top;
    }
    
    .detail-table td:first-child {
        width: 150px;
        color: #666;
    }
    
    .detail-section {
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .detail-section:last-child {
        border-bottom: none;
    }
    
    .detail-section h4 {
        color: #333;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .ingredients-text {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        line-height: 1.6;
        color: #555;
    }
    
    .score-display {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .score-bar {
        flex: 1;
        height: 8px;
        background: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
    }
    
    .score-fill {
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    
    .score-text {
        font-weight: 600;
        color: #333;
    }
    
    .toast-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    
    .toast-close {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 2px;
        border-radius: 50%;
        transition: background-color 0.3s ease;
    }
    
    .toast-close:hover {
        background: #f0f0f0;
    }
    
    .online {
        color: #28a745 !important;
    }
    
    .offline {
        color: #dc3545 !important;
    }
`;

// Inject additional CSS
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalCSS;
document.head.appendChild(styleSheet);

// Keyboard shortcut hint
console.log('💡 Tip: Press Ctrl+/ to focus on search input');

// ====== CRUD FUNCTIONALITY ======

// DOM Elements for CRUD
const addProductBtn = document.getElementById('add-product');
const productFormModal = document.getElementById('product-form-modal');
const closeFormModal = document.getElementById('close-form-modal');
const cancelForm = document.getElementById('cancel-form');
const productForm = document.getElementById('product-form');
const formModalTitle = document.getElementById('form-modal-title');
const submitForm = document.getElementById('submit-form');

// CRUD state
let isEditMode = false;
let editingProductId = null;

// Setup CRUD event listeners
function setupCRUDEventListeners() {
    if (addProductBtn) {
        addProductBtn.addEventListener('click', openAddProductModal);
    }
    
    if (closeFormModal) {
        closeFormModal.addEventListener('click', closeProductFormModal);
    }
    
    if (cancelForm) {
        cancelForm.addEventListener('click', closeProductFormModal);
    }
    
    if (productForm) {
        productForm.addEventListener('submit', handleProductSubmit);
    }
    
    // Close modal when clicking outside
    if (productFormModal) {
        productFormModal.addEventListener('click', function(e) {
            if (e.target === productFormModal) {
                closeProductFormModal();
            }
        });
    }
}

// Open add product modal
function openAddProductModal() {
    isEditMode = false;
    editingProductId = null;
    formModalTitle.textContent = 'Add New Product';
    submitForm.textContent = 'Add Product';
    productForm.reset();
    showModal(productFormModal);
}

// Open edit product modal
function openEditProductModal(productId) {
    isEditMode = true;
    editingProductId = productId;
    formModalTitle.textContent = 'Edit Product';
    submitForm.textContent = 'Update Product';
    
    // Load product data
    loadProductForEdit(productId);
    showModal(productFormModal);
}

// Load product data for editing
async function loadProductForEdit(productId) {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.products}/${productId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success && data.product) {
            populateForm(data.product);
        } else {
            throw new Error('Failed to load product data');
        }
    } catch (error) {
        console.error('Error loading product:', error);
        showToast('Failed to load product data', 'error');
    } finally {
        showLoading(false);
    }
}

// Populate form with product data
function populateForm(product) {
    document.getElementById('product-name').value = product.name || '';
    document.getElementById('product-brand').value = product.brand || '';
    document.getElementById('product-ingredients').value = product.ingredients || '';
    document.getElementById('product-categories').value = product.categories || '';
    document.getElementById('product-manufacturer').value = product.manufacturer || '';
    document.getElementById('product-manufacturer-number').value = product.manufacturerNumber || '';
}

// Close product form modal
function closeProductFormModal() {
    hideModal(productFormModal);
    productForm.reset();
    isEditMode = false;
    editingProductId = null;
}

// Handle product form submission
async function handleProductSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(productForm);
    const productData = {
        name: formData.get('name').trim(),
        brand: formData.get('brand').trim(),
        ingredients: formData.get('ingredients').trim(),
        categories: formData.get('categories').trim(),
        manufacturer: formData.get('manufacturer').trim(),
        manufacturerNumber: formData.get('manufacturerNumber').trim()
    };
    
    // Validate required fields
    if (!productData.name || !productData.brand) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        let response;
        if (isEditMode && editingProductId !== null) {
            // Update product
            response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.products}/${editingProductId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData)
            });
        } else {
            // Add new product
            response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.products}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(productData)
            });
        }
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            const action = isEditMode ? 'updated' : 'added';
            showToast(`Product ${action} successfully!`, 'success');
            closeProductFormModal();
            
            // Refresh product list
            await loadProducts(currentPage);
            await loadStatistics();
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error saving product:', error);
        showToast(`Failed to save product: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Delete product
async function deleteProduct(productId, productName) {
    if (!confirm(`Are you sure you want to delete "${productName}"?\n\nThis action cannot be undone.`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.products}/${productId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success) {
            showToast('Product deleted successfully!', 'success');
            
            // Refresh product list
            await loadProducts(currentPage);
            await loadStatistics();
        } else {
            throw new Error(data.error || 'Unknown error');
        }
        
    } catch (error) {
        console.error('Error deleting product:', error);
        showToast(`Failed to delete product: ${error.message}`, 'error');
    } finally {
        showLoading(false);
    }
}

// Clear search results
function clearSearchResults() {
    const resultsDiv = document.getElementById('searchResults');
    if (resultsDiv) {
        resultsDiv.innerHTML = '';
    }
    
    const searchTime = document.getElementById('searchTime');
    if (searchTime) {
        searchTime.textContent = '';
    }
    
    currentSearchResults = [];
    console.log('Search results cleared');
}
