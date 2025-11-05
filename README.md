# 🍫 ChocoCrunch Analytics
An End-to-End Data Analysis Project on Global Chocolate Products

# 🧭 Introduction

ChocoCrunch Analytics is a data analytics project designed to explore and interpret global chocolate product data using a structured data science workflow. The project integrates data collection, cleaning, transformation, database management, and interactive visualization to derive meaningful insights from real-world product data.

The data was gathered from the OpenFoodFacts API, processed with Python, stored in MySQL, and visualized through a Streamlit dashboard. The goal is to study the nutritional content of chocolates, evaluate brand patterns, and highlight health-based classifications.

# 🎯 Objectives

- To collect and organize chocolate product data from an open-source API.
- To clean and standardize the dataset for analytical use.
- To create new analytical variables using feature engineering.
- To design and populate a MySQL database for structured storage.
- To visualize results through an interactive Streamlit application.

# ⚙ Tools & Technologies 

| Purpose       | Tool / Library                 |
| ------------- | ------------------------------ |
| Programming   | Python                         |
| Data Handling | Pandas, NumPy                  |
| Database      | MySQL (via SQLAlchemy)         |
| Visualization | Streamlit, Matplotlib, Seaborn |
| Data Source   | OpenFoodFacts API              |



# 📊 Project Workflow

1. Data Extraction
- Data retrieved using the OpenFoodFacts API (approximately 14,000 chocolate products).
- Extracted attributes include: product name, brand, ingredients, nutrients, additives, allergens, and NOVA processing level.

2. Data Cleaning
- Removed duplicate and incomplete entries.
- Normalized units (e.g., energy to kcal, sugar to grams).
- Handled missing and inconsistent values through imputation and filtering.

3. Feature Engineering
Derived analytical features for deeper understanding:
- sugar_to_carb_ratio
- calorie_category
- sugar_category
- is_ultra_processed (based on NOVA classification)

4. Database Construction (MySQL)
Created relational schema with key tables:
- product_info
- nutrient_info
- derived_metrics
- Used SQLAlchemy for Python–MySQL integration and query execution.

5. Exploratory Data Analysis (EDA)
- Analyzed nutrient distribution across brands.
- Explored correlations among sugar, energy, and carbohydrates.
- Visualized key statistics using Matplotlib and Seaborn.

6. Interactive Dashboard (Streamlit)
- Developed a Streamlit application for user-driven exploration.
- Enabled brand filtering, nutrient comparisons, and query-based visual insights.

# 💡 Major Insights

- A large portion of chocolate products are moderately to highly processed.
- Sugar levels vary significantly across brands, with some showing extreme ratios.
- High-calorie chocolates dominate the dataset, indicating limited healthy options.

# 🧩 Project Structure
```

ChocoCrunch-Analytics/
│
├── data/
│   ├── raw_data.csv
│   ├── cleaned_data.csv
│   └── engineered_data.csv
│
├── scripts/
│   ├── extract_api_data.py
│   ├── clean_transform.py
│   ├── feature_engineering.py
│   ├── mysql_loader.py
│   └── streamlit_dashboard.py
│
├── notebooks/
│   └── chocolate_analysis.ipynb
│
├── app.py
├── schema.sql
├── requirements.txt
└── README.md
```
## 🚀 Getting Started

#### Prerequisites
- Python 3.10+
- MySQL Database (running locally or on a server)
- Git


#### Clone Repository
```
https://github.com/Maryam-Feroz/-ChocoCrunch-Analytics.git
cd ChocoCrunch-Analytics
```

#### Install Dependencies
```
pip install -r requirements.txt
```
#### Configure Secrets
Create .streamlit/secrets.toml with your MySQL credentials:
```
[database]
db_host="127.0.0.1"
db_user="root"
db_password="your_password"
db_name="choco_crunch"
```
#### Run the Streamlit App
```
streamlit run app.py
```
The app will open in your default browser at``` http://localhost:8501.```

# 🚀 Future Enhancements

- Develop predictive ML models to classify chocolates by calorie or sugar range.
- Add visual comparisons of countries or product categories.
- Deploy the Streamlit app publicly on Streamlit Cloud.
- Automate API data refresh and MySQL synchronization.

  # 📚 References

- OpenFoodFacts API Documentation
- NOVA Food Processing Classification Framework
- Streamlit and SQLAlchemy Official Docs
