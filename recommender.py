import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Optional
import builtins

class RecipeProductRecommender:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.vectorizer = None
        self.tfidf_matrix = None
        self.ingredient_vectorizer = None
        self.ingredient_tfidf_matrix = None

        # Column mapping for nutritional data
        self.nutrition_cols = {
            'calories': 'energy-kcal_100g',
            'carbs': 'carbohydrates_100g',
            'sugars': 'sugars_100g',
            'proteins': 'proteins_100g'
        }

        # Dietary restriction columns
        self.dietary_cols = {
            'gluten_free': 'is_gluten_free',
            'low_sugar': 'is_low_sugar',
            'high_protein': 'is_high_protein',
            'low_calorie': 'is_low_calorie',
            'dairy_free': 'is_dairy_free',
            'nut_free': 'is_nut_free',
            'soy_free': 'is_soy_free',
            'egg_free': 'is_egg_free'
        }

        self._prepare_data()
        self._setup_vectorizers()

    def _prepare_data(self):
        # Handle missing values for text columns
        text_cols = ['product_name', 'brands', 'categories', 'ingredients_text', 'allergens']
        for col in text_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].fillna('')

        # Create comprehensive search text
        health_flags_text = self.df.get('health_flags', pd.Series('')).fillna('').str.replace('_', ' ')
        allergen_friendly_text = self.df.get('allergen_friendly', pd.Series('')).fillna('').str.replace('_', ' ')

        self.df['search_text'] = (
            self.df.get('product_name', pd.Series('')).str.lower() + ' ' +
            self.df.get('brands', pd.Series('')).str.lower() + ' ' +
            self.df.get('categories', pd.Series('')).str.lower() + ' ' +
            self.df.get('ingredients_text', pd.Series('')).str.lower() + ' ' +
            health_flags_text.str.lower() + ' ' +
            allergen_friendly_text.str.lower()
        ).str.strip()

        # Clean ingredients text for better processing
        self.df['cleaned_ingredients'] = self.df.get('ingredients_text', pd.Series('')).fillna('').apply(self._clean_ingredient_text)

        # Calculate health score if not available
        if 'health_score' not in self.df.columns:
            self.df['health_score'] = self._calculate_health_score()

        # Clean numerical columns
        for col in self.nutrition_cols.values():
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)

        # Ensure boolean columns are properly typed
        for col in self.dietary_cols.values():
            if col in self.df.columns:
                self.df[col] = self.df[col].astype(bool)

    def _clean_ingredient_text(self, text: str) -> str:
        """Clean and normalize ingredient text."""
        if not text:
            return ""

        # Remove common prefixes and suffixes
        text = re.sub(r'\b(organic|natural|fresh|dried|powdered|extract)\b', '', text.lower())
        # Remove percentages and numbers in parentheses
        text = re.sub(r'\([^)]*\d+[^)]*\)', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _setup_vectorizers(self):
        """Setup both general and ingredient-specific vectorizers."""
        valid_texts = self.df['search_text'][self.df['search_text'].str.len() > 0]

        if len(valid_texts) == 0:
            raise ValueError("No valid text data found")

        # General vectorizer for overall search
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 3),
            min_df=2,
            max_df=0.95,
            lowercase=True,
            strip_accents='unicode',
            token_pattern=r'\b[a-zA-Z][a-zA-Z0-9]*\b'
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(self.df['search_text'])

        # Ingredient-specific vectorizer
        valid_ingredients = self.df['cleaned_ingredients'][self.df['cleaned_ingredients'].str.len() > 0]

        if len(valid_ingredients) > 0:
            self.ingredient_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1,
                max_df=0.9,
                lowercase=True,
                strip_accents='unicode'
            )

            self.ingredient_tfidf_matrix = self.ingredient_vectorizer.fit_transform(self.df['cleaned_ingredients'])

    def _calculate_health_score(self) -> pd.Series:
        """Calculate health score based on available nutritional data."""
        score = pd.Series(5.0, index=self.df.index)  # Default middle score

        # NutriScore mapping (A=best, E=worst)
        nutri_map = {'A': 8, 'B': 6, 'C': 5, 'D': 3, 'E': 1}
        if 'nutriscore_grade' in self.df.columns:
            nutri_scores = self.df['nutriscore_grade'].map(nutri_map)
            score = score.where(nutri_scores.isna(), nutri_scores)

        # Boost score based on health flags
        if 'health_flags' in self.df.columns:
            health_flags = self.df['health_flags'].fillna('')
            positive_flags = ['low_sugar', 'high_protein', 'gluten_free', 'low_calorie']
            for flag in positive_flags:
                flag_boost = health_flags.str.contains(flag, case=False).astype(int) * 0.5
                score = np.minimum(score + flag_boost, 10)

        # Adjust based on nutritional content
        if 'sugars_100g' in self.df.columns:
            sugar_penalty = np.clip(self.df['sugars_100g'] / 15, 0, 2)
            score = np.maximum(score - sugar_penalty, 1)

        if 'proteins_100g' in self.df.columns:
            protein_boost = np.clip(self.df['proteins_100g'] / 25, 0, 2)
            score = np.minimum(score + protein_boost, 10)

        if 'energy-kcal_100g' in self.df.columns:
            calorie_penalty = np.where(self.df['energy-kcal_100g'] > 500, 1, 0)
            score = np.maximum(score - calorie_penalty, 1)

        return score.fillna(5.0)

    def recommend(self,
                 recipe_text: str = "",
                 ingredients: List[str] = None,
                 dietary_preferences: List[str] = None,
                 filters: Dict = None,
                 top_n: int = 10,
                 min_similarity: float = 0.05,
                 prioritize_health: bool = True,
                 ingredient_weight: float = 0.4) -> pd.DataFrame:
        
        # Build search query
        search_query = self._build_query(recipe_text, ingredients, dietary_preferences)

        # Calculate similarities
        general_similarities = self._get_general_similarities(search_query)
        ingredient_similarities = self._get_ingredient_similarities(ingredients)

        # Combine similarities
        combined_similarities = self._combine_similarities(
            general_similarities,
            ingredient_similarities,
            ingredient_weight
        )

        # Apply filters
        valid_mask = self._apply_filters(filters, dietary_preferences)
        valid_mask &= (combined_similarities >= min_similarity)

        if not valid_mask.any():
            return pd.DataFrame()

        # Calculate final scores
        final_scores = self._calculate_scores(combined_similarities, valid_mask, prioritize_health)

        # Get top results
        top_indices = final_scores.nlargest(top_n).index

        return self._format_output(top_indices, combined_similarities, final_scores, ingredients)

    def _build_query(self, recipe_text: str, ingredients: List[str] = None,
                    dietary_preferences: List[str] = None) -> str:
        """Build search query from inputs."""
        parts = []

        if recipe_text:
            parts.append(recipe_text.lower().strip())

        if ingredients:
            clean_ingredients = [ing.lower().strip() for ing in ingredients if ing.strip()]
            parts.extend(clean_ingredients)

        if dietary_preferences:
            diet_terms = []
            for pref in dietary_preferences:
                if pref in self.dietary_cols:
                    diet_terms.append(pref.replace('_', ' '))
                    diet_terms.append(pref)
            parts.extend(diet_terms)

        return ' '.join(parts)

    def _get_general_similarities(self, query: str) -> pd.Series:
        """Calculate general cosine similarities."""
        if not query.strip():
            return pd.Series(0.0, index=self.df.index)

        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        return pd.Series(similarities, index=self.df.index)

    def _get_ingredient_similarities(self, ingredients: List[str] = None) -> pd.Series:
        """Calculate ingredient-specific similarities."""
        if not ingredients or not self.ingredient_vectorizer:
            return pd.Series(0.0, index=self.df.index)

        # Clean and combine ingredients
        clean_ingredients = [self._clean_ingredient_text(ing) for ing in ingredients if ing.strip()]
        ingredient_query = ' '.join(clean_ingredients)

        if not ingredient_query.strip():
            return pd.Series(0.0, index=self.df.index)

        query_vec = self.ingredient_vectorizer.transform([ingredient_query])
        similarities = cosine_similarity(query_vec, self.ingredient_tfidf_matrix).flatten()

        return pd.Series(similarities, index=self.df.index)

    def _combine_similarities(self, general_sim: pd.Series, ingredient_sim: pd.Series,
                            ingredient_weight: float) -> pd.Series:
        """Combine general and ingredient similarities."""
        general_weight = 1 - ingredient_weight

        return general_weight * general_sim + ingredient_weight * ingredient_sim

    def _apply_filters(self, filters: Dict = None, dietary_preferences: List[str] = None) -> pd.Series:
        """Apply filters including dietary preferences."""
        mask = pd.Series(True, index=self.df.index)

        # Apply dietary preferences as hard filters
        if dietary_preferences:
            for pref in dietary_preferences:
                if pref in self.dietary_cols:
                    col_name = self.dietary_cols[pref]
                    if col_name in self.df.columns:
                        mask &= self.df[col_name] == True

        if not filters:
            return mask

        # Nutritional filters
        if 'max_calories' in filters and 'energy-kcal_100g' in self.df.columns:
            mask &= self.df['energy-kcal_100g'] <= filters['max_calories']

        if 'max_sugar' in filters and 'sugars_100g' in self.df.columns:
            mask &= self.df['sugars_100g'] <= filters['max_sugar']

        if 'min_protein' in filters and 'proteins_100g' in self.df.columns:
            mask &= self.df['proteins_100g'] >= filters['min_protein']

        if 'max_carbs' in filters and 'carbohydrates_100g' in self.df.columns:
            mask &= self.df['carbohydrates_100g'] <= filters['max_carbs']

        # NutriScore filter
        if 'nutriscore' in filters and 'nutriscore_grade' in self.df.columns:
            allowed = filters['nutriscore']
            if isinstance(allowed, str):
                allowed = [allowed]
            mask &= self.df['nutriscore_grade'].isin(allowed)

        # Brand filter
        if 'brands' in filters and 'brands' in self.df.columns:
            brands = filters['brands']
            if isinstance(brands, str):
                brands = [brands]
            brand_mask = pd.Series(False, index=self.df.index)
            for brand in brands:
                brand_mask |= self.df['brands'].str.contains(brand, case=False, na=False)
            mask &= brand_mask

        return mask

    def _calculate_scores(self, similarities: pd.Series, valid_mask: pd.Series,
                        prioritize_health: bool = True) -> pd.Series:
        """Calculate final ranking scores."""
        scores = pd.Series(0.0, index=self.df.index)

        if not valid_mask.any():
            return scores

        valid_sim = similarities[valid_mask]
        valid_health = self.df.loc[valid_mask, 'health_score']

        # Normalize scores
        if valid_sim.max() > 0:
            norm_sim = valid_sim / valid_sim.max()
        else:
            norm_sim = pd.Series(0.0, index=valid_sim.index)

        norm_health = valid_health / 10.0

        # Calculate weighted scores
        if prioritize_health:
            scores[valid_mask] = 0.55 * norm_sim + 0.45 * norm_health
        else:
            scores[valid_mask] = 0.70 * norm_sim + 0.30 * norm_health

        return scores

    def _format_output(self, indices: pd.Index, similarities: pd.Series,
                      final_scores: pd.Series, matched_ingredients: List[str] = None) -> pd.DataFrame:
        """Format results with ingredient matching information."""
        if len(indices) == 0:
            return pd.DataFrame()

        result = self.df.loc[indices].copy()
        result['similarity_score'] = similarities.loc[indices].round(3)
        result['final_score'] = final_scores.loc[indices].round(3)

        # Add ingredient matching information
        if matched_ingredients:
            result['matched_ingredients'] = result['ingredients_text'].apply(
                lambda x: self._count_ingredient_matches(x, matched_ingredients)
            )

        # Select display columns
        display_cols = ['product_name', 'brands', 'final_score', 'similarity_score', 'health_score']

        if matched_ingredients:
            display_cols.append('matched_ingredients')

        # Add available columns
        optional_cols = ['nutriscore_grade', 'health_category', 'energy-kcal_100g',
                        'proteins_100g', 'sugars_100g', 'categories', 'ingredients_text']

        for col in optional_cols:
            if col in result.columns:
                display_cols.append(col)

        # Filter existing columns
        final_cols = [col for col in display_cols if col in result.columns]

        return result[final_cols].reset_index(drop=True)

    def _count_ingredient_matches(self, product_ingredients: str, search_ingredients: List[str]) -> int:
        """Count how many search ingredients are found in product ingredients."""
        if not product_ingredients or not search_ingredients:
            return 0

        product_lower = product_ingredients.lower()
        matches = 0

        for ingredient in search_ingredients:
            if ingredient.lower().strip() in product_lower:
                matches += 1

        return matches

    def get_ingredient_suggestions(self, partial: str, limit: int = 10) -> List[str]:
        """Get ingredient suggestions based on partial input."""
        if not partial or len(partial) < 2:
            return []

        all_ingredients = set()
        partial_lower = partial.lower()

        for ing_text in self.df['ingredients_text'].dropna():
            # Split by common separators
            ingredients = re.split(r'[,;()]\s*', ing_text.lower())
            for ing in ingredients:
                ing = ing.strip()
                if len(ing) > 2 and partial_lower in ing:
                    # Clean the ingredient suggestion
                    clean_ing = re.sub(r'\([^)]*\)', '', ing).strip()
                    if clean_ing:
                        all_ingredients.add(clean_ing)

        return sorted(all_ingredients, key=len)[:limit]

    def search_by_ingredients_only(self, ingredients: List[str], top_n: int = 10) -> pd.DataFrame:
        """Search products based only on ingredients list."""
        if not ingredients:
            return pd.DataFrame()

        return self.recommend(
            recipe_text="",
            ingredients=ingredients,
            top_n=top_n,
            ingredient_weight=0.8,  # High weight on ingredient matching
            prioritize_health=False
        )

    def get_dietary_options(self) -> Dict[str, int]:
        """Get available dietary options and their counts."""
        options = {}
        for diet_name, col_name in self.dietary_cols.items():
            if col_name in self.df.columns:
                count = self.df[col_name].sum()
                options[diet_name] = int(count)
        return options

    def get_nutrition_summary(self, product_indices: List[int] = None) -> Dict:
        """Get nutritional summary of products."""
        if product_indices:
            subset = self.df.iloc[product_indices]
        else:
            subset = self.df

        summary = {}
        for col in self.nutrition_cols.values():
            if col in subset.columns:
                col_data = subset[col].dropna()
                if len(col_data) > 0:
                    summary[col] = {
                        'mean': builtins.round(col_data.mean(), 2),
                        'median': builtins.round(col_data.median(), 2),
                        'min': col_data.min(),
                        'max': col_data.max(),
                        'count': len(col_data)
                    }
        return summary

