// Search functionality

class SearchManager {
    constructor() {
        this.searchForm = $('#searchForm');
        this.searchQuery = $('#searchQuery');
        this.searchMethod = $('#searchMethod');
        this.topK = $('#topK');
        this.loadingIndicator = $('#loadingIndicator');
        this.searchResults = $('#searchResults');
        this.noResults = $('#noResults');
        this.resultsContainer = $('#resultsContainer');
        this.resultsCount = $('#resultsCount');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupAutocomplete();
    }
    
    setupEventListeners() {
        // Search form submission
        this.searchForm.on('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });
        
        // Real-time search (optional)
        this.searchQuery.on('input', this.debounce(() => {
            const query = this.searchQuery.val().trim();
            if (query.length >= 3) {
                // Optionally trigger search for long queries
                // this.performSearch();
            }
        }, 500));
        
        // Enter key handling
        this.searchQuery.on('keypress', (e) => {
            if (e.which === 13) {
                e.preventDefault();
                this.performSearch();
            }
        });
    }
    
    setupAutocomplete() {
        // Could implement autocomplete here
        // For now, just add placeholder functionality
        this.searchQuery.attr('placeholder', 
            'Try: "organic juice", "gluten-free snacks", "coconut water"...');
    }
    
    async performSearch() {
        const query = this.searchQuery.val().trim();
        const method = this.searchMethod.val();
        const topK = parseInt(this.topK.val());
        
        if (!query) {
            app.showToast('Please enter a search query', 'warning');
            return;
        }
        
        this.showLoading(true);
        this.hideResults();
        
        try {
            const response = await fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: query,
                    method: method,
                    top_k: topK
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.results, query);
            } else {
                this.showError(data.error || 'Search failed');
            }
        } catch (error) {
            console.error('Search error:', error);
            this.showError('Network error occurred');
        } finally {
            this.showLoading(false);
        }
    }
    
    displayResults(results, query) {
        if (!results || results.length === 0) {
            this.showNoResults();
            return;
        }
        
        this.resultsCount.text(`${results.length} results`);
        
        let html = '';
        results.forEach((result, index) => {
            const scoreColor = this.getScoreColor(result.score);
            const methodBadge = result.method === 'hybrid' ? 'primary' : 'secondary';
            
            html += `
                <div class="search-result-item fade-in">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="flex-grow-1">
                            <h5 class="mb-1">
                                <span class="badge bg-light text-dark me-2">#${index + 1}</span>
                                ${this.highlightQuery(result.name, query)}
                            </h5>
                            <p class="text-muted mb-2">
                                <i class="fas fa-tag me-1"></i>${result.brand}
                                <span class="mx-2">•</span>
                                <i class="fas fa-fingerprint me-1"></i>ID: ${result.id}
                            </p>
                        </div>
                        <div class="text-end">
                            <span class="search-score" style="background-color: ${scoreColor}">
                                ${(result.score * 100).toFixed(1)}%
                            </span>
                        </div>
                    </div>
                    
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <span class="badge bg-${methodBadge} search-method-badge">
                                ${result.method.replace('_', ' ').toUpperCase()}
                            </span>
                            ${result.response_time ? `
                                <span class="badge bg-info search-method-badge">
                                    ${result.response_time.toFixed(1)}ms
                                </span>
                            ` : ''}
                        </div>
                        <div>
                            <button class="btn btn-sm btn-outline-primary" onclick="viewProductDetails(${result.id})">
                                <i class="fas fa-eye me-1"></i>View Details
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });
        
        this.resultsContainer.html(html);
        this.searchResults.show();
        
        // Scroll to results
        $('html, body').animate({
            scrollTop: this.searchResults.offset().top - 100
        }, 500);
    }
    
    highlightQuery(text, query) {
        if (!query) return text;
        
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    getScoreColor(score) {
        if (score >= 0.8) return '#28a745'; // Green
        if (score >= 0.6) return '#ffc107'; // Yellow
        if (score >= 0.4) return '#fd7e14'; // Orange
        return '#dc3545'; // Red
    }
    
    showLoading(show) {
        if (show) {
            this.loadingIndicator.show();
        } else {
            this.loadingIndicator.hide();
        }
    }
    
    hideResults() {
        this.searchResults.hide();
        this.noResults.hide();
    }
    
    showNoResults() {
        this.noResults.show();
    }
    
    showError(message) {
        app.showToast(message, 'danger');
    }
    
    debounce(func, wait) {
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
}

// Global functions
function clearSearch() {
    $('#searchQuery').val('');
    $('#searchResults').hide();
    $('#noResults').hide();
    $('#searchQuery').focus();
}

function viewProductDetails(productId) {
    // Implement product details view
    app.showToast(`Viewing details for product ID: ${productId}`, 'info');
}

// Initialize search manager when document is ready
$(document).ready(() => {
    const searchManager = new SearchManager();
});