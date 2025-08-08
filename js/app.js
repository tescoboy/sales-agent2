// AdCP Agent Platform - Campaign Generator
// Main application logic for campaign generation using signals and sales agents

// DOM Elements
const campaignForm = document.getElementById('campaignForm');
const advertiserNameInput = document.getElementById('advertiserName');
const campaignNameInput = document.getElementById('campaignName');
const campaignBriefTextarea = document.getElementById('campaignBrief');
const budgetInput = document.getElementById('budget');
const startDateInput = document.getElementById('startDate');
const endDateInput = document.getElementById('endDate');
const generateBtn = document.getElementById('generateBtn');
const btnText = document.getElementById('btnText');
const loadingSpinner = document.getElementById('loadingSpinner');
const resultsSection = document.getElementById('resultsSection');
const overviewContent = document.getElementById('overviewContent');
const signalsContent = document.getElementById('signalsContent');
const productsContent = document.getElementById('productsContent');
const strategyContent = document.getElementById('strategyContent');
const jsonContent = document.getElementById('jsonContent');
const copyResultsBtn = document.getElementById('copyResultsBtn');
const downloadJsonBtn = document.getElementById('downloadJsonBtn');
const newCampaignBtn = document.getElementById('newCampaignBtn');

// Global variables
let currentResults = null;

// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';

// Initialize application
function initializeApp() {
    console.log('Initializing AdCP Agent Platform...');
    setupEventListeners();
    setupDefaultDates();
    console.log('Application initialized successfully');
}

// Setup all event listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    
    // Form submission
    campaignForm.addEventListener('submit', handleFormSubmission);
    
    // Results buttons
    copyResultsBtn.addEventListener('click', copyResultsToClipboard);
    downloadJsonBtn.addEventListener('click', downloadJsonResults);
    newCampaignBtn.addEventListener('click', resetForm);
    
    console.log('Event listeners setup complete');
}

// Setup default dates
function setupDefaultDates() {
    const today = new Date();
    const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate());
    
    startDateInput.value = today.toISOString().split('T')[0];
    endDateInput.value = nextMonth.toISOString().split('T')[0];
}

// Handle form submission
async function handleFormSubmission(event) {
    event.preventDefault();
    console.log('Form submitted, processing campaign brief...');
    
    const formData = getFormData();
    
    if (!validateFormData(formData)) {
        return;
    }
    
    try {
        setLoadingState(true);
        console.log('Generating campaign strategy for:', formData);
        
        const results = await generateCampaignStrategy(formData);
        console.log('Campaign strategy generated successfully:', results);
        
        currentResults = results;
        displayResults(results);
        setLoadingState(false);
        
    } catch (error) {
        console.error('Error generating campaign strategy:', error);
        showError('Failed to generate campaign strategy. Please try again.');
        setLoadingState(false);
    }
}

// Get form data
function getFormData() {
    return {
        advertiserName: advertiserNameInput.value.trim(),
        campaignName: campaignNameInput.value.trim(),
        campaignBrief: campaignBriefTextarea.value.trim(),
        budget: parseFloat(budgetInput.value),
        startDate: startDateInput.value,
        endDate: endDateInput.value
    };
}

// Validate form data
function validateFormData(data) {
    if (!data.advertiserName) {
        showError('Please enter an advertiser name');
        return false;
    }
    
    if (!data.campaignName) {
        showError('Please enter a campaign name');
        return false;
    }
    
    if (!data.campaignBrief) {
        showError('Please enter a campaign brief');
        return false;
    }
    
    if (!data.budget || data.budget < 1000) {
        showError('Please enter a valid budget (minimum $1,000)');
        return false;
    }
    
    if (!data.startDate || !data.endDate) {
        showError('Please select start and end dates');
        return false;
    }
    
    if (new Date(data.endDate) <= new Date(data.startDate)) {
        showError('End date must be after start date');
        return false;
    }
    
    return true;
}

// Generate campaign strategy
async function generateCampaignStrategy(formData) {
    console.log('Starting campaign strategy generation for:', formData);
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate-campaign`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        
        const results = await response.json();
        console.log('Campaign strategy created:', results);
        return results;
        
    } catch (error) {
        console.error('Error calling API:', error);
        throw error;
    }
}

// Display results
function displayResults(results) {
    console.log('Displaying results:', results);
    
    // Show results section
    resultsSection.classList.remove('d-none');
    
    // Populate tabs
    populateOverviewTab(results);
    populateSignalsTab(results);
    populateProductsTab(results);
    populateStrategyTab(results);
    populateJsonTab(results);
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

// Populate overview tab
function populateOverviewTab(results) {
    const overview = `
        <div class="row">
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h5 class="card-title text-primary">
                            <i class="fas fa-info-circle me-2"></i>Campaign Overview
                        </h5>
                        <ul class="list-unstyled">
                            <li><strong>Advertiser:</strong> ${results.test_metadata.advertiser}</li>
                            <li><strong>Campaign:</strong> ${results.test_metadata.campaign_name}</li>
                            <li><strong>Budget:</strong> $${results.final_results.budget_allocation.toLocaleString()}</li>
                            <li><strong>Flight Dates:</strong> ${results.final_results.flight_dates}</li>
                            <li><strong>Status:</strong> <span class="badge bg-success">Ready</span></li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h5 class="card-title text-primary">
                            <i class="fas fa-chart-bar me-2"></i>Key Metrics
                        </h5>
                        <ul class="list-unstyled">
                            <li><strong>Signals Found:</strong> ${results.final_results.signals_available}</li>
                            <li><strong>Products Available:</strong> ${results.final_results.products_available}</li>
                            <li><strong>Platform Coverage:</strong> 3 platforms</li>
                            <li><strong>Targeting:</strong> ${results.final_results.targeting_summary}</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        <div class="row mt-4">
            <div class="col-12">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h5 class="card-title text-primary">
                            <i class="fas fa-lightbulb me-2"></i>Recommendations
                        </h5>
                        <ul class="list-unstyled">
                            ${results.final_results.recommendations.map(rec => `<li><i class="fas fa-check text-success me-2"></i>${rec}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    overviewContent.innerHTML = overview;
}

// Populate signals tab
function populateSignalsTab(results) {
    const signals = results.signals_agent.discovery?.signals || [];
    
    const signalsHtml = `
        <h5 class="text-primary mb-3">
            <i class="fas fa-signal me-2"></i>Discovered Signals (${signals.length})
        </h5>
        ${signals.map(signal => `
            <div class="card border-0 shadow-sm mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h6 class="card-title">${signal.name}</h6>
                            <p class="card-text text-muted">${signal.description}</p>
                            <div class="row">
                                <div class="col-6">
                                    <small class="text-muted">
                                        <i class="fas fa-chart-pie me-1"></i>Coverage: ${signal.coverage_percentage}%
                                    </small>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">
                                        <i class="fas fa-dollar-sign me-1"></i>CPM: $${signal.pricing?.cpm || 'N/A'}
                                    </small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <span class="badge bg-success">Active</span>
                            <br>
                            <small class="text-muted">${signal.data_provider || 'N/A'}</small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
    
    signalsContent.innerHTML = signalsHtml;
}

// Populate products tab
function populateProductsTab(results) {
    const products = results.sales_agent.products?.products || [];
    
    const productsHtml = `
        <h5 class="text-primary mb-3">
            <i class="fas fa-shopping-cart me-2"></i>Available Products (${products.length})
        </h5>
        ${products.map(product => `
            <div class="card border-0 shadow-sm mb-3">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h6 class="card-title">${product.name}</h6>
                            <p class="card-text text-muted">${product.description}</p>
                            <div class="row">
                                <div class="col-6">
                                    <small class="text-muted">
                                        <i class="fas fa-tag me-1"></i>Type: ${product.delivery_type}
                                    </small>
                                </div>
                                <div class="col-6">
                                    <small class="text-muted">
                                        <i class="fas fa-dollar-sign me-1"></i>CPM: $${product.cpm || product.price_guidance?.p50 || 'N/A'}
                                    </small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-4 text-end">
                            <span class="badge bg-primary">${product.delivery_type}</span>
                            <br>
                            <small class="text-muted">${product.policy_compliance || 'N/A'}</small>
                        </div>
                    </div>
                </div>
            </div>
        `).join('')}
    `;
    
    productsContent.innerHTML = productsHtml;
}

// Populate strategy tab
function populateStrategyTab(results) {
    const strategyHtml = `
        <h5 class="text-primary mb-3">
            <i class="fas fa-chess me-2"></i>Campaign Strategy
        </h5>
        <div class="row">
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-title">Targeting Strategy</h6>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-map-marker-alt me-2"></i>Geographic: United States</li>
                            <li><i class="fas fa-users me-2"></i>Audience: ${results.final_results.targeting_summary}</li>
                            <li><i class="fas fa-mobile-alt me-2"></i>Devices: Mobile, Desktop</li>
                            <li><i class="fas fa-chart-line me-2"></i>Content: Contextual targeting</li>
                        </ul>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <h6 class="card-title">Budget Allocation</h6>
                        <ul class="list-unstyled">
                            <li><i class="fas fa-dollar-sign me-2"></i>Total: $${results.final_results.budget_allocation.toLocaleString()}</li>
                            <li><i class="fas fa-calendar me-2"></i>Duration: ${results.final_results.flight_dates}</li>
                            <li><i class="fas fa-chart-pie me-2"></i>Pacing: Even</li>
                            <li><i class="fas fa-tasks me-2"></i>Status: Ready for execution</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    strategyContent.innerHTML = strategyHtml;
}

// Populate JSON tab
function populateJsonTab(results) {
    jsonContent.textContent = JSON.stringify(results, null, 2);
}

// Copy results to clipboard
async function copyResultsToClipboard() {
    try {
        const resultsText = JSON.stringify(currentResults, null, 2);
        await navigator.clipboard.writeText(resultsText);
        showSuccess('Results copied to clipboard!');
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        showError('Failed to copy results to clipboard');
    }
}

// Download JSON results
function downloadJsonResults() {
    if (!currentResults) {
        showError('No results to download');
        return;
    }
    
    const dataStr = JSON.stringify(currentResults, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `campaign_results_${Date.now()}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showSuccess('Results downloaded successfully!');
}

// Reset form
function resetForm() {
    campaignForm.reset();
    resultsSection.classList.add('d-none');
    currentResults = null;
    setupDefaultDates();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Set loading state
function setLoadingState(isLoading) {
    if (isLoading) {
        btnText.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
        loadingSpinner.classList.remove('d-none');
        generateBtn.disabled = true;
    } else {
        btnText.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Campaign Strategy';
        loadingSpinner.classList.add('d-none');
        generateBtn.disabled = false;
    }
}

// Show error message
function showError(message) {
    const alertHtml = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
            <i class="fas fa-exclamation-triangle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const alertHtml = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
            <i class="fas fa-check-circle me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        const alert = document.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 3000);
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);
