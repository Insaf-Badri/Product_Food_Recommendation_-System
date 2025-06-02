let ingredients = [];
const API_BASE_URL = 'http://localhost:5000';

function showRecipeForm() {
    document.getElementById('homePage').style.display = 'none';
    document.getElementById('recipeForm').classList.add('active');
}

function showHomePage() {
    document.getElementById('recipeForm').classList.remove('active');
    document.getElementById('recipeForm').style.display = 'none';
    document.getElementById('homePage').style.display = 'flex';
    document.getElementById('resultsContainer').classList.remove('active');
}

function addIngredient() {
    const input = document.getElementById('ingredientInput');
    const ingredient = input.value.trim();
    
    if (ingredient && !ingredients.includes(ingredient)) {
        ingredients.push(ingredient);
        updateIngredientTags();
        input.value = '';
    }
}

function removeIngredient(ingredient) {
    ingredients = ingredients.filter(ing => ing !== ingredient);
    updateIngredientTags();
}

function updateIngredientTags() {
    const container = document.getElementById('ingredientTags');
    if (container) {
        container.innerHTML = ingredients.map(ingredient => 
            `<span class="ingredient-tag">
                ${ingredient}
                <span class="remove" onclick="removeIngredient('${ingredient}')">&times;</span>
            </span>`
        ).join('');
    }
}

// Enhanced ingredient input with suggestions
function setupIngredientAutocomplete() {
    const input = document.getElementById('ingredientInput');
    if (!input) return;
    
    let suggestionTimeout;

    input.addEventListener('input', function(e) {
        clearTimeout(suggestionTimeout);
        const query = e.target.value.trim();
        
        if (query.length >= 2) {
            suggestionTimeout = setTimeout(() => {
                fetchIngredientSuggestions(query);
            }, 300);
        } else {
            hideSuggestions();
        }
    });
}

async function fetchIngredientSuggestions(query) {
    try {
        const response = await fetch(`${API_BASE_URL}/ingredient-suggestions?q=${encodeURIComponent(query)}&limit=5`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.suggestions && data.suggestions.length > 0) {
            showSuggestions(data.suggestions);
        } else {
            hideSuggestions();
        }
    } catch (error) {
        console.error('Error fetching ingredient suggestions:', error);
        hideSuggestions();
    }
}

function showSuggestions(suggestions) {
    let dropdown = document.getElementById('ingredient-suggestions');
    
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'ingredient-suggestions';
        dropdown.className = 'ingredient-suggestions';
        const inputContainer = document.querySelector('.ingredients-input');
        if (inputContainer) {
            inputContainer.appendChild(dropdown);
        }
    }
    
    dropdown.innerHTML = suggestions.map(suggestion => 
        `<div class="suggestion-item" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
    ).join('');
    
    dropdown.style.display = 'block';
}

function hideSuggestions() {
    const dropdown = document.getElementById('ingredient-suggestions');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    const input = document.getElementById('ingredientInput');
    if (input) {
        input.value = suggestion;
        addIngredient();
        hideSuggestions();
    }
}

// Allow Enter key to add ingredients
document.addEventListener('DOMContentLoaded', function() {
    const ingredientInput = document.getElementById('ingredientInput');
    if (ingredientInput) {
        ingredientInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                addIngredient();
            }
        });
    }
});

// Handle form submission with API call
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('recommendationForm');
    if (form) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Gather form data safely
            const recipeTextEl = document.getElementById('recipeText');
            const maxCaloriesEl = document.getElementById('maxCalories');
            const maxSugarEl = document.getElementById('maxSugar');
            const minProteinEl = document.getElementById('minProtein');
            const nutriScoreEl = document.getElementById('nutriScore');
            const excludeAllergensEl = document.getElementById('excludeAllergens');
            
            const formData = {
                recipeText: recipeTextEl ? recipeTextEl.value : '',
                ingredients: ingredients,
                filters: {
                    maxCalories: maxCaloriesEl ? maxCaloriesEl.value || null : null,
                    maxSugar: maxSugarEl ? maxSugarEl.value || null : null,
                    minProtein: minProteinEl ? minProteinEl.value || null : null,
                    nutriScore: nutriScoreEl ? Array.from(nutriScoreEl.selectedOptions).map(opt => opt.value) : [],
                    excludeAllergens: excludeAllergensEl ? Array.from(excludeAllergensEl.selectedOptions).map(opt => opt.value) : []
                }
            };

            console.log('Sending request:', formData);
            // Show loading state
            showLoading();
            
            try {
                // Make API call to backend with improved error handling
                const response = await fetch(`${API_BASE_URL}/recommend`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                console.log('Response status:', response.status);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Server error (${response.status}): ${errorText}`);
                }

                const data = await response.json();
                console.log('Response data:', data);
                
                if (data.error) {
                    throw new Error(data.error);
                }

                displayResults(data.recommendations || []);
                
            } catch (error) {
                console.error('Error getting recommendations:', error);
                showError(error.message);
            }
        });
    }
});


// Enhanced ingredient input with suggestions
function setupIngredientAutocomplete() {
    const input = document.getElementById('ingredientInput');
    if (!input) return;
    
    let suggestionTimeout;

    input.addEventListener('input', function(e) {
        clearTimeout(suggestionTimeout);
        const query = e.target.value.trim();
        
        if (query.length >= 2) {
            suggestionTimeout = setTimeout(() => {
                fetchIngredientSuggestions(query);
            }, 300);
        } else {
            hideSuggestions();
        }
    });

    // Hide suggestions when clicking outside hnaya bch matbanch dik lktba likant katban 
    document.addEventListener('click', function(e) {
        const dropdown = document.getElementById('ingredient-suggestions');
        const inputContainer = document.querySelector('.ingredients-input');
        
        if (dropdown && inputContainer && !inputContainer.contains(e.target)) {
            hideSuggestions();
        }
    });

    
    input.addEventListener('blur', function() {
        setTimeout(() => {
            hideSuggestions();
        }, 150);
    });
}

function showSuggestions(suggestions) {
    let dropdown = document.getElementById('ingredient-suggestions');
    
    if (!dropdown) {
        dropdown = document.createElement('div');
        dropdown.id = 'ingredient-suggestions';
        dropdown.className = 'ingredient-suggestions';
        const inputContainer = document.querySelector('.ingredients-input');
        if (inputContainer) {
            inputContainer.appendChild(dropdown);
        }
    }
    
    dropdown.innerHTML = suggestions.map(suggestion => 
        `<div class="suggestion-item" onclick="selectSuggestion('${suggestion}')">${suggestion}</div>`
    ).join('');
    
    dropdown.style.display = 'block';
}

function hideSuggestions() {
    const dropdown = document.getElementById('ingredient-suggestions');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
}

function selectSuggestion(suggestion) {
    const input = document.getElementById('ingredientInput');
    if (input) {
        input.value = suggestion;
        addIngredient();
        hideSuggestions();
    }
}

function showLoading() {
    const resultsContainer = document.getElementById('resultsContainer');
    const resultsContent = document.getElementById('resultsContent');
    
    if (resultsContent) {
        resultsContent.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                Analyzing your recipe and finding the best ingredients...
            </div>
        `;
    }
    
    if (resultsContainer) {
        resultsContainer.classList.add('active');
    }
}

function showError(message) {
    const resultsContent = document.getElementById('resultsContent');
    if (resultsContent) {
        resultsContent.innerHTML = `
            <div class="error-message">
                <h4> Oops! Something went wrong</h4>
                <p>${message}</p>
                <p>Please check:</p>
                <ul>
                    <li>Flask server is running on http://localhost:5000</li>
                    <li>Your recommender model is loaded</li>
                    <li>Network connection is stable</li>
                </ul>
                <button onclick="checkBackendHealth()" class="retry-btn">Test Connection</button>
            </div>
        `;
    }
}

function displayResults(results) {
    const resultsContent = document.getElementById('resultsContent');
    
    if (!resultsContent) return;
    
    if (!results || results.length === 0) {
        resultsContent.innerHTML = `
            <div class="no-results">
                <h4>🔍 No products found</h4>
                <p>Try adjusting your filters or adding different ingredients.</p>
            </div>
        `;
        return;
    }

    resultsContent.innerHTML = results.map(product => {
        const scorePercent = (product.score || 0);
        const healthClass = getHealthClass(product.healthCategory);
        
        return `
        <div class="product-card" style="--score-percent: ${scorePercent};">
            <div class="product-header">
                <div class="product-name">${product.name || 'Unknown Product'}</div>
                <div class="product-brand">by ${product.brand || 'Unknown Brand'}</div>
                ${product.matched_ingredients > 0 ? 
                    `<div class="matched-ingredients">${product.matched_ingredients} ingredient${product.matched_ingredients > 1 ? 's' : ''} matched</div>` 
                    : ''
                }
            </div>
            <div class="product-info">
                <div class="info-item">
                    <strong>Match Score</strong>
                    <div class="score-value">${(scorePercent * 100).toFixed(0)}%</div>
                </div>
                <div class="info-item">
                    <strong>Calories</strong>
                    <div>${product.calories || 0} <span style="font-size: 0.8rem; color: #64748b;">kcal</span></div>
                </div>
                <div class="info-item">
                    <strong>Protein</strong>
                    <div>${product.protein || 0}<span style="font-size: 0.8rem; color: #64748b;">g</span></div>
                </div>
                <div class="info-item">
                    <strong>Sugar</strong>
                    <div>${product.sugar || 0}<span style="font-size: 0.8rem; color: #64748b;">g</span></div>
                </div>
                <div class="info-item">
                    <strong>NutriScore</strong>
                    <div class="nutriscore-badge" style="background: ${getNutriScoreColor(product.nutriscore)};">
                        ${product.nutriscore || 'C'}
                    </div>
                </div>
                <div class="info-item">
                    <strong>Health Rating</strong>
                    <div class="health-category ${healthClass}">${product.healthCategory || 'Average'}</div>
                </div>
            </div>
            ${product.categories ? `<div class="product-categories">Categories: ${truncateCategories(product.categories)}</div>` : ''}
        </div>
        `;
    }).join('');
}

function getHealthClass(healthCategory) {
    if (!healthCategory) return 'average';
    const category = healthCategory.toLowerCase();
    if (category.includes('good') || category.includes('excellent')) return 'good';
    if (category.includes('poor') || category.includes('bad')) return 'poor';
    return 'average';
}

function truncateCategories(categories) {
    if (!categories) return '';
    const maxLength = 100;
    if (categories.length <= maxLength) return categories;
    return categories.substring(0, maxLength) + '...';
}

function getNutriScoreColor(score) {
    const colors = {
        'A': '#1e7b1e',
        'B': '#85bb2f', 
        'C': '#f9c23d',
        'D': '#f77c00',
        'E': '#e63946'
    };
    return colors[score] || '#666';
}
function getNutriScoreColor(score) {
    const colors = {
        'A': '#1e7b1e',
        'B': '#85bb2f',
        'C': '#f9c23d',
        'D': '#f77c00',
        'E': '#e63946'
    };
    return colors[score] || '#666';
}

// Check backend health on page load
async function checkBackendHealth() {
    try {
        console.log('Checking backend health...');
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Backend health check:', data);
        
        if (!data.recommender_loaded) {
            console.warn('Recommender system not loaded on backend');
            showError('Recommender system not loaded on backend');
        } else {
            console.log('Backend is healthy and recommender is loaded');
        }
        
        return data;
    } catch (error) {
        console.error('Backend not available:', error);
        showError(`Backend connection failed: ${error.message}`);
        return null;
    }
}

// Initialize autocomplete and check backend health
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    setupIngredientAutocomplete();
    
    // Delay backend check to ensure everything is loaded
    setTimeout(() => {
        checkBackendHealth();
    }, 1000);
});

// Add some dynamic floating animations (keep existing functionality)
function createRandomFloatingFood() {
    const foods = ['🍎', '🥕', '🍞', '🧄', '🥬', '🍅', '🥖', '🥑', '🍋', '🥔', '🥒', '🍆', '🌽', '🥦'];
    const food = foods[Math.floor(Math.random() * foods.length)];
    
    const element = document.createElement('div');
    element.className = 'floating-food';
    element.textContent = food;
    element.style.top = Math.random() * window.innerHeight + 'px';
    element.style.left = Math.random() * window.innerWidth + 'px';
    element.style.animationDuration = (Math.random() * 4 + 4) + 's';
    
    document.body.appendChild(element);
    
    setTimeout(() => {
        element.remove();
    }, 8000);
}

// Create new floating food every 3 seconds
setInterval(createRandomFloatingFood, 3000);