# Recipe Recommendation System 🍳

An AI-powered food product recommendation system that helps users discover the perfect ingredients for their recipes based on nutritional value, dietary preferences, and ingredient matching.

## 🌟 Features

### 🔍 Smart Recipe Analysis
- **Recipe Description Input**: Describe your recipe
- **Ingredient Matching**: AI analyzes and matches ingredients with available products
- **Multi-language Support**: Interface available in French 

### 🥗 Advanced Filtering Options
- **Nutritional Filters**:
- Maximum Calories (per 100g)
- Maximum Sugar content (g per 100g)
- Minimum Protein content (g per 100g)
- **NutriScore Integration**: Filter by health ratings (A-E scale)
- **Allergen Management**: Exclude specific allergens (Gluten, Milk, Eggs, etc.)

### Detailed Product Information
- **Match Score**: Percentage-based ingredient compatibility
- **Nutritional Data**: Calories, Protein, Sugar content
- **Health Rating**: NutriScore classification
- **Brand Information**: Product manufacturer details
- **Category Classification**: Product categorization

##  Getting Started

### Prerequisites
```bash
python 3.8+
pandas
numpy
scikit-learn
html css js  (for web interface)
```

### Installation
```bash
git clone https://github.com/Insaf-Badri/Product_Food_Recommendation_System.git
cd Product_Food_Recommendation_System
pip install -r requirements.txt
```


## 📁 Project Structure
```
Product_Food_Recommendation_System/
├── French-dataset/
│   └── cleaned_data.csv          # Product database (80MB)
├── models/
│   └── recipe_recommender2.pkl   # Trained ML model (463MB, stored in LFS)
├── images/
│   ├── im1.png         # Landing page screenshot
│   ├── im2.png         # Recipe input interface
│   └── im3.png      # Product recommendations view
├── app.py                        # Main Streamlit application
├── requirements.txt              # Python dependencies
├── .gitattributes               # Git LFS configuration
└── README.md                    # Project documentation
```

## 🔧 How It Works

1. **Recipe Input**: Users describe their recipe in the text area
2. **Ingredient Extraction**: AI processes the description to identify key ingredients
3. **Product Matching**: Algorithm searches the French product database for compatible items
4. **Filtering**: Applied dietary and nutritional filters narrow down results
5. **Scoring**: Each product receives a match score based on ingredient compatibility
6. **Recommendation**: Top-rated products are displayed with detailed nutritional information

## 📈 Algorithm Details

The recommendation system uses:
- **Natural Language Processing** for recipe analysis
- **Ingredient Matching Algorithm** for product compatibility
- **Nutritional Scoring System** based on health metrics
- **Filter Integration** for personalized recommendations

## 🎯 Example Use Cases

- **Dietary Restrictions**: Find gluten-free alternatives for traditional recipes
- **Health-Conscious Cooking**: Discover low-sugar, high-protein ingredients
- **Recipe Optimization**: Improve nutritional value of existing recipes
- **Product Discovery**: Explore new brands and product categories

## 📊 Dataset Information

- **Product Database**: 80MB+ French food product dataset
- **Coverage**: Wide range of food categories and brands
- **Nutritional Data**: Comprehensive macro and micronutrient information
- **Health Ratings**: NutriScore classifications for all products

## 🛠️ Technical Stack

- **Backend**: Python, Pandas, NumPy
- **Machine Learning**: Scikit-learn, Custom recommendation algorithms
- **Frontend**: Streamlit with custom CSS styling
- **Data Storage**: CSV database with Git LFS for large files
- **Deployment**: Streamlit Cloud compatible

## 🎨 User Interface

### Screenshots

#### 1. Landing Page
![Landing Page](images/im2.png)

#### 2. Recipe Input Interface
![Recipe Input](images/im3.png)
*User-friendly form for entering recipe descriptions, ingredients, and dietary preferences*

#### 3. Product Recommendations
![Product Recommendations](images/im1.png)
*Detailed product cards showing match scores, nutritional information, and health ratings*

### Design Features
- **Modern Gradient Design**: Purple-pink aesthetic with floating food icons
- **Intuitive Forms**: Easy-to-use input fields for recipes and preferences
- **Responsive Cards**: Clean product display with key metrics
- **Interactive Filters**: Real-time filtering capabilities
- **Multi-language Support**: Interface text in French (Tahiya | Imarwa)
- **Professional Layout**: Clean, modern design with excellent UX/UI

## 🔮 Future Enhancements

- [ ] Recipe image recognition
- [ ] Meal planning integration
- [ ] Shopping list generation
- [ ] Nutritional goal tracking
- [ ] Social recipe sharing
- [ ] Multi-language expansion

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

**Insaf Badri**
**marwa sghir**
- GitHub: [@Insaf-Badri](https://github.com/Insaf-Badri)
- Project: [Product Food Recommendation System](https://github.com/Insaf-Badri/Product_Food_Recommendation_-System)



Discover the perfect ingredients for your recipes! 🍽️*
