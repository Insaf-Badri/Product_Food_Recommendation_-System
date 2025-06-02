import traceback
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import joblib
from typing import List, Dict
import logging 
from recommender import RecipeProductRecommender

app = Flask(__name__)

CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

@app.route('/')
def home():
    return render_template('index.html')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


recommender = None

def load_recommender(model_path: str = 'recipe_recommender2.pkl'):
    global recommender
    try:
        with open(model_path, 'rb') as f:
            recommender = joblib.load(f)
        logger.info("Recommender system loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading recommender: {str(e)}")
        return False

def format_recommendation_response(recommendations_df: pd.DataFrame) -> List[Dict]:
    if recommendations_df.empty:
        return []
    
    results = []
    for _, row in recommendations_df.iterrows():
        try:
            # Extract nutritional information
            calories = row.get('energy-kcal_100g', 0)
            protein = row.get('proteins_100g', 0)
            sugar = row.get('sugars_100g', 0)
            
            
            score = row.get('final_score', 0)
            
            # Get health category based on nutriscore or health score
            nutriscore = row.get('nutriscore_grade', 'C')
            health_score = row.get('health_score', 5)
            
            if health_score >= 7:
                health_category = "Excellent"
            elif health_score >= 5:
                health_category = "Good"
            elif health_score >= 3:
                health_category = "Average"
            else:
                health_category = "Poor"
            
            product = {
                "name": str(row.get('product_name', 'Unknown Product')),
                "brand": str(row.get('brands', 'Unknown Brand')),
                "score": float(score) if pd.notna(score) else 0.0,
                "calories": int(calories) if pd.notna(calories) and calories > 0 else 0,
                "protein": round(float(protein), 1) if pd.notna(protein) else 0.0,
                "sugar": round(float(sugar), 1) if pd.notna(sugar) else 0.0,
                "nutriscore": str(nutriscore).upper() if pd.notna(nutriscore) else "C",
                "healthCategory": health_category,
                "categories": str(row.get('categories', '')),
                "ingredients": str(row.get('ingredients_text', '')),
                "matched_ingredients": int(row.get('matched_ingredients', 0)) if 'matched_ingredients' in row else 0
            }
            results.append(product)
        except Exception as e:
            logger.error(f"Error formatting product: {str(e)}")
            continue
    
    return results

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "recommender_loaded": recommender is not None
    })

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    if recommender is None:
        return jsonify({
            "error": "Recommender system not loaded",
            "recommendations": []
        }), 500
    
    try:
        # Add better error handling
        if not request.is_json:
            return jsonify({
                "error": "Request must be JSON",
                "recommendations": []
            }), 400
            
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "Invalid JSON data",
                "recommendations": []
            }), 400
        
        # Extract parameters from request
        recipe_text = data.get('recipeText', '')
        ingredients = data.get('ingredients', [])
        filters = data.get('filters', {})
        
        logger.info(f"Received request - Recipe: '{recipe_text[:50]}...', Ingredients: {ingredients}, Filters: {filters}")
      
        processed_filters = {}
        
        # Nutritional filters
        try:
            if filters.get('maxCalories'):
                processed_filters['max_calories'] = float(filters['maxCalories'])
            
            if filters.get('maxSugar'):
                processed_filters['max_sugar'] = float(filters['maxSugar'])
            
            if filters.get('minProtein'):
                processed_filters['min_protein'] = float(filters['minProtein'])
        except ValueError as e:
            return jsonify({
                "error": f"Invalid numeric filter value: {str(e)}",
                "recommendations": []
            }), 400
        
        # NutriScore filter
        if filters.get('nutriScore') and len(filters['nutriScore']) > 0:
            processed_filters['nutriscore'] = filters['nutriScore']
        
        # Dietary preferences (allergen exclusions)
        dietary_preferences = []
        exclude_allergens = filters.get('excludeAllergens', [])
        
        # Map allergens to dietary preferences
        allergen_mapping = {
            'gluten': 'gluten_free',
            'milk': 'dairy_free', 
            'nuts': 'nut_free',
            'soy': 'soy_free',
            'eggs': 'egg_free'
        }
        
        for allergen in exclude_allergens:
            if allergen in allergen_mapping:
                dietary_preferences.append(allergen_mapping[allergen])
        
        # Get recommendations from the model
        recommendations_df = recommender.recommend(
            recipe_text=recipe_text,
            ingredients=ingredients,
            dietary_preferences=dietary_preferences,
            filters=processed_filters,
            top_n=10,
            min_similarity=0.01,
            prioritize_health=True,
            ingredient_weight=0.4
        )
        
        # Format response
        formatted_results = format_recommendation_response(recommendations_df)
        
        logger.info(f"Returning {len(formatted_results)} recommendations")
        
        return jsonify({
            "recommendations": formatted_results,
            "total_found": len(formatted_results),
            "query_info": {
                "recipe_text": recipe_text,
                "ingredients": ingredients,
                "filters_applied": len(processed_filters) > 0 or len(dietary_preferences) > 0
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing recommendation request: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "recommendations": []
        }), 500

@app.route('/ingredient-suggestions', methods=['GET'])
def get_ingredient_suggestions():
    if recommender is None:
        return jsonify({"suggestions": []})
    
    try:
        partial = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        # Check if recommender has the method
        if hasattr(recommender, 'get_ingredient_suggestions'):
            suggestions = recommender.get_ingredient_suggestions(partial, limit)
        else:
            print("Recommender does not support ingredient suggestions, using fallback.")
        
        return jsonify({
            "suggestions": suggestions,
            "query": partial
        })
        
    except Exception as e:
        logger.error(f"Error getting ingredient suggestions: {str(e)}")
        return jsonify({"suggestions": []})

@app.route('/dietary-options', methods=['GET'])
def get_dietary_options():
    if recommender is None:
        return jsonify({"options": {}})
    
    try:
        if hasattr(recommender, 'get_dietary_options'):
            options = recommender.get_dietary_options()
        else:
            # Fallback options
            options = {
                "allergens": ["gluten", "milk", "nuts", "soy", "eggs"],
                "nutriscore": ["A", "B", "C", "D", "E"]
            }
        return jsonify({"options": options})
        
    except Exception as e:
        logger.error(f"Error getting dietary options: {str(e)}")
        return jsonify({"options": {}})
    

@app.route('/nutrition-summary', methods=['POST'])
def get_nutrition_summary():
    if recommender is None:
        return jsonify({"summary": {}})
    
    try:
        data = request.get_json()
        indices = data.get('indices', [])
        
        if hasattr(recommender, 'get_nutrition_summary'):
            summary = recommender.get_nutrition_summary(indices if indices else None)
        else:
            summary = {"message": "Nutrition summary not available"}
        
        return jsonify({"summary": summary})
        
    except Exception as e:
        logger.error(f"Error getting nutrition summary: {str(e)}")
        return jsonify({"summary": {}})

if __name__ == '__main__':
    model_loaded = load_recommender()
    
    if not model_loaded:
        logger.warning("Failed to load recommender system. Some endpoints may not work.")
    
    # Run on localhost instead of 0.0.0.0 to match JavaScript expectations
    app.run(debug=True, host='localhost', port=5000)