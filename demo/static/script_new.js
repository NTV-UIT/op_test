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
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideModal();
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
    showLoading();
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
        hideLoading();
    }
}

function displaySearchResults(response) {
    hideLoading();
    showSection(searchResults);
    
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
        showLoading();
        
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
            
            hideLoading();
            showSection(browseSection);
            hideSection(searchResults);
            
            showToast(`Loaded ${response.products.length} products`, 'success');
        } else {
            throw new Error(response.error || 'Failed to load products');
        }
    } catch (error) {
        hideLoading();
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
    card.onclick = () => showProductDetail(product);
    
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
function showLoading() {
    showSection(loading);
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

function hideModal() {
    hideSection(productModal);
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
