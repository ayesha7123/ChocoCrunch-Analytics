import pandas as pd
import streamlit as st
import pymysql
from sqlalchemy import create_engine
import altair as alt
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np

# --- DB Connection ---
def get_engine():
    db = st.secrets["database"]
    engine = create_engine(
        f"mysql+pymysql://{db['db_user']}:{db['db_pass']}@{db['db_host']}/{db['db_name']}"
    )
    return engine

engine = get_engine()
conn = engine.connect()

# --- Streamlit App ---
# --- Streamlit App ---
st.markdown("""
    <!-- Load Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@1,700&display=swap" rel="stylesheet">

    <!-- Main Title: Elegant Serif, Italic -->
    <h1 style='
        text-align: center; 
        color: #8B0000; 
        font-family: "Playfair Display", serif; 
        font-style: italic;
        font-size: 48px;
    '>
        🍫 ChocoCrunch Analytics: Sweet Insights, Bitter Truths
    </h1>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:2px solid #8B0000;'>", unsafe_allow_html=True)


# --- Tabs ---
tabs = st.tabs(["Product Info", "Nutrient Info", "Derived Metrics","Join Queries"])

# --- Helper function for normal queries ---
def run_query(query):
    df = pd.read_sql(query, engine)
    return df

# -----------------------------
# Tab 1: Product Info
# -----------------------------
with tabs[0]:
    st.header("📦 Product Info Queries")

    product_queries = {
        "1. Count products per brand": """
            SELECT brand, COUNT(product_name) AS total_products
            FROM product_info
            WHERE brand IS NOT NULL
            GROUP BY brand
            ORDER BY total_products DESC;
        """,
        "2. Count unique products per brand": """
            SELECT brand, COUNT(DISTINCT product_name) AS unique_products
            FROM product_info
            WHERE brand IS NOT NULL
            GROUP BY brand
            ORDER BY unique_products DESC;
        """,
        "3. Top 5 brands by product count": """
            SELECT brand, COUNT(product_name) AS total_products
            FROM product_info
            WHERE brand IS NOT NULL
            GROUP BY brand
            ORDER BY total_products DESC
            LIMIT 5;
        """,
        "4. Products with missing product name": """
            SELECT brand, COUNT(*) AS missing_names
            FROM product_info
            WHERE product_name IS NULL
            GROUP BY brand
            ORDER BY missing_names DESC;
        """,
        "5. Number of unique brands": """
            SELECT COUNT(DISTINCT brand) AS unique_brands
            FROM product_info
            WHERE brand IS NOT NULL;
        """,
        "6. Products with code starting with '3'": """
            SELECT product_name
            FROM product_info
            WHERE CAST(product_code AS CHAR) LIKE '3%'
            AND product_name IS NOT NULL
            AND TRIM(product_name) != '';
        """
    }

    selected_query = st.selectbox("Choose a Product Info Query", list(product_queries.keys()))
    query = product_queries[selected_query]

    # --- For everything except query 6, use run_query() ---
    if selected_query != "6. Products with code starting with '3'":
        df = run_query(query)
        st.dataframe(df)

    # --- Automatic Visualizations ---
   
    # --- Count products per brand ---
    if selected_query == "1. Count products per brand":
        st.subheader("📦 Count of Products per Brand (Bar Chart)")
    
        # Slider for top N brands
        n = st.slider(
            "Select number of top brands to view",
            min_value=5,
            max_value=len(df),
            value=10,
            key="count_products_slider"
        )
        top_df = df.head(n)

        # Bar chart with custom color
        chart = alt.Chart(top_df).mark_bar(color="#B69F2E").encode(
            x=alt.X(top_df.columns[0], sort=top_df[top_df.columns[0]].tolist(), title="Brand"),
            y=alt.Y(top_df.columns[1], title="Number of Products")
        )
        st.altair_chart(chart, use_container_width=True)

        # --- Count unique products per brand ---
    elif selected_query == "2. Count unique products per brand":
        st.subheader("🛍️ Count of Unique Products per Brand (Bar Chart)")
    
        # Slider for top N brands
        n = st.slider(
            "Select number of top brands to view",
            min_value=5,
            max_value=len(df),
            value=10,
            key="unique_products_slider"
        )
        top_df = df.head(n)

        # Bar chart with a different color
        chart = alt.Chart(top_df).mark_bar(color="#16A374").encode(
            x=alt.X(top_df.columns[0], sort=top_df[top_df.columns[0]].tolist(), title="Brand"),
            y=alt.Y(top_df.columns[1], title="Number of Unique Products")
        )
        st.altair_chart(chart, use_container_width=True)


    elif selected_query == "3. Top 5 brands by product count":
        st.subheader("🏆 Top 5 Brands by Number of Products (Bar Chart)")
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y(df.columns[0], sort='-x', title="Brand"),
            x=alt.X(df.columns[1], title="Count of Products"),
            color=alt.Color(df.columns[0], legend=None)
        )
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "4. Products with missing product name":
        if df.empty or df[ df.columns[1] ] .sum() == 0:
            st.info("✅ No missing product names found for any brand.")
        else:
            n = st.slider(
                "Select number of top brands to view",
                min_value=5,
                max_value=len(df),
                value=10
            )
            
    elif selected_query == "5. Number of unique brands":
            st.metric(label="Unique Brands", value=int(df.iloc[0, 0]))

    elif selected_query == "6. Products with code starting with '3'":
    # Run the query manually with product_code included
        query_fixed = """
        SELECT product_code, product_name
        FROM product_info
        WHERE product_code LIKE '3%%' 
        AND product_name IS NOT NULL
        AND TRIM(product_name) != ''
        """

        # engine = create_engine("mysql+pymysql://root:Maryam07@localhost/choco_crunch")
        # df_clean = pd.read_sql(query_fixed, conn)  # pandas reads directly
        df_clean = pd.read_sql(query_fixed, engine)
         
        # Convert bytes to str if needed, and strip whitespace
        df_clean['product_name'] = df_clean['product_name'].astype(str).str.strip()
        df_clean['product_code'] = df_clean['product_code'].astype(str).str.strip()

        # Display the full DataFrame
        st.dataframe(df_clean.reset_index(drop=True), height=600)

    # WordCloud using product names
        if not df_clean.empty:
            st.success(f"✅ Found {len(df_clean)} products starting with code '3'")
            st.subheader("🌟 WordCloud of Products with Code Starting with '3'")
            text = " ".join(df_clean['product_name'].astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("No product names available for WordCloud.")
# -----------------------------
# Tab 2: Nutrient Info
# -----------------------------
with tabs[1]:
    st.header("📑 Nutrient Info Queries & Visualizations")

    nutrient_queries = {
        "1. Top 10 products with highest energy_kcal_value": """
            SELECT p.product_name, n.energy_kcal_value, p.brand
            FROM product_info p
            JOIN nutrient_info n ON p.product_code=n.product_code
            ORDER BY n.energy_kcal_value DESC
            LIMIT 10;
        """,

        "2. Average sugars_value per nova_group": """
            SELECT nova_group, AVG(sugars_value) AS avg_sugar
            FROM nutrient_info
            WHERE nova_group IS NOT NULL AND TRIM(nova_group) != ''
            GROUP BY nova_group
            ORDER BY nova_group;
        """,

        "3. Count products with fat_value > 20g": """
            SELECT COUNT(*) AS fat_count
            FROM nutrient_info
            WHERE fat_value > 20
            """,

        "4. Average carbohydrates_value per product": """
            SELECT p.product_name AS `Product Name`,
            AVG(n.carbohydrates_value) AS `Average Carbs Value`
            FROM product_info p
            JOIN nutrient_info n ON n.product_code = p.product_code
            GROUP BY p.product_name
            ORDER BY `Average Carbs Value` DESC;
            """,

        "5. Products with sodium_value > 1g": """
            SELECT p.product_name, n.sodium_value
            FROM product_info p
            JOIN nutrient_info n ON p.product_code = n.product_code
            WHERE n.sodium_value > 1;
        """,

        "6. Count products with non-zero fruits-vegetables-nuts content": """
            SELECT COUNT(*) AS products_with_fv_nuts
            FROM nutrient_info
            WHERE fruits_veg_nuts_pct > 0
        """,

        "7. Products with energy_kcal_value > 500": """
            SELECT p.product_name, n.energy_kcal_value
            FROM product_info p
            JOIN nutrient_info n ON p.product_code = n.product_code
            WHERE n.energy_kcal_value > 500
            ORDER BY energy_kcal_value DESC;
        """
    }

    selected_query = st.selectbox("Choose a Nutrient Info Query", list(nutrient_queries.keys()))
    query = nutrient_queries[selected_query]

        # Run the query
    df = run_query(query)

# --- Display as KPI or DataFrame ---
    if selected_query in [
       "3. Count products with fat_value > 20g",
       "6. Count products with non-zero fruits-vegetables-nuts content"
        ]:
        st.metric(label=selected_query, value=float(df.iloc[0, 0]))

    else:
        st.dataframe(df, height=400)

# --- Automatic Visualizations ---
    if selected_query == "1. Top 10 products with highest energy_kcal_value":
        st.subheader("🔥 Top 10 Highest-Energy Products (Bar Chart)")
        # Slider to select top N products
        n = st.slider(
            "Select number of top products to view",
            min_value=5,
            max_value=len(df),
            value=10
        ) 
        # Filter top N products
        top_df = df.nlargest(n, "energy_kcal_value")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("product_name", sort="-y", title="Product"),
            y=alt.Y("energy_kcal_value", title="Energy (kcal)"),
            color=alt.Color("energy_kcal_value", scale=alt.Scale(scheme="oranges"))
        )
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "2. Average sugars_value per nova_group": 
        # Assuming df has columns: 'nova_group' and 'avg_sugar'

        st.subheader("🍬 Average Sugar Content by NOVA Group (Vertical Lollipop Chart)")

        # Base chart: vertical line from zero to value
        base = alt.Chart(df).mark_rule(color='black').encode(
            x=alt.X('nova_group:N', title='NOVA Group'),
            y=alt.Y('avg_sugar:Q', title='Average Sugar (g)')
        )

        # Circle at the top of each line with color gradient
        points = alt.Chart(df).mark_circle(size=200).encode(
            x=alt.X('nova_group:N'),
            y=alt.Y('avg_sugar:Q'),
            color=alt.Color('avg_sugar:Q', scale=alt.Scale(scheme='reds'), title='Avg Sugar (g)')
        )

        # Combine line + points
        lollipop_chart = base + points

        st.altair_chart(lollipop_chart, use_container_width=True)

    elif selected_query == "4. Average carbohydrates_value per product":
        n = st.slider(
           "Select number of top products to view",
            min_value=5,
            max_value=len(df),
            value=10
        )
        top_df = df.nlargest(n, "Average Carbs Value")  # top N products by carbs

        # Horizontal bar chart
        chart = alt.Chart(top_df).mark_bar().encode(
            y=alt.Y("Product Name:N", sort='-x', title="Product"),
            x=alt.X("Average Carbs Value:Q", title="Average Carbs (g)"),
            color=alt.Color("Average Carbs Value:Q", scale=alt.Scale(scheme="blueorange"))
        )
        st.subheader("🍞 Average Carbohydrates per Product – Top Products (Horizontal Bar Chart)")
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "5. Products with sodium_value > 1g":
        n = st.slider("Select number of top products to view", min_value=5, max_value=len(df), value=10)
        top_df = df.nlargest(n, "sodium_value")
        st.subheader("⚠️Top High-Sodium Products []>1g] – (Horizontal Bar Chart)")
        chart = alt.Chart(top_df).mark_bar().encode(
            y=alt.Y("product_name", sort="-x", title="Product"),
            x=alt.X("sodium_value", title="Sodium (g)"),
            color=alt.Color("sodium_value", scale=alt.Scale(scheme="browns"))
        )
        line = alt.Chart(pd.DataFrame({"y": [2]})).mark_rule(color="black", strokeDash=[5, 5]).encode(y="y")
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "7. Products with energy_kcal_value > 500":
        n = st.slider(
           "Select number of top products to view",
            min_value=5,
            max_value=len(df),
            value=10
        )
        top_df = df.nlargest(n, "energy_kcal_value")

        # Horizontal bar chart
        st.subheader("🔥 Products with Highest Energy Content [>500 kcal] - (Horizontal Bar Chart)")
        chart = alt.Chart(top_df).mark_bar().encode(
            y=alt.Y("product_name:N", sort='-x', title="Product"),
            x=alt.X("energy_kcal_value:Q", title="Energy (kcal)"),
            color=alt.Color("energy_kcal_value:Q", scale=alt.Scale(scheme="orangered"))
        )
        st.altair_chart(chart, use_container_width=True)

# -----------------------------
# Tab 3: Derived Metrics
# -----------------------------
with tabs[2]:
    st.header("📊 Derived Metrics Queries & Visualizations")

    derived_queries = {
        "1. Count products per calorie_category": """
            SELECT calorie_category, COUNT(*) AS product_count
            FROM derived_metrics
            GROUP BY calorie_category
            ORDER BY product_count DESC;
        """,
        "2. Count of High Sugar products": """
            SELECT COUNT(*) AS high_sugar_count
            FROM derived_metrics
            WHERE sugar_category='High Sugar';
        """,
        "3. Average sugar_to_carb_ratio for High Calorie products": """
            SELECT AVG(sugar_to_carb_ratio) AS avg_ratio
            FROM derived_metrics
            WHERE calorie_category='High Calorie';
        """,
        "4. Products that are both High Calorie and High Sugar": """
            SELECT p.product_name, p.brand, d.calorie_category, d.sugar_category
            FROM derived_metrics d
            JOIN product_info p ON d.product_code=p.product_code
            WHERE d.calorie_category='High Calorie' AND d.sugar_category='High Sugar';
        """,
        "5. Number of products marked as ultra-processed": """
            SELECT COUNT(*) AS ultra_processed_count
            FROM derived_metrics
            WHERE is_ultra_processed='Yes';
        """,
        "6. Products with sugar_to_carb_ratio > 0.7": """
            SELECT p.product_name, p.brand, d.sugar_to_carb_ratio
            FROM derived_metrics d
            JOIN product_info p ON d.product_code=p.product_code
            WHERE d.sugar_to_carb_ratio > 0.7
            ORDER BY d.sugar_to_carb_ratio DESC;
        """,
        "7. Average sugar_to_carb_ratio per calorie_category": """
            SELECT calorie_category, AVG(sugar_to_carb_ratio) AS avg_ratio
            FROM derived_metrics
            GROUP BY calorie_category;
        """
    }

    selected_query = st.selectbox("Choose a Derived Metrics Query", list(derived_queries.keys()))
    query = derived_queries[selected_query]
    df = run_query(query)

    # Display table or KPI
    if selected_query in ["2. Count of High Sugar products", "3. Average sugar_to_carb_ratio for High Calorie products", "5. Number of products marked as ultra-processed"]:
        st.metric(label=selected_query, value=float(df.iloc[0,0]))
    else:
        st.dataframe(df)

    # Visualizations
    if selected_query == "1. Count products per calorie_category":
        st.subheader("🔥 Number of Products by Calorie Category (Bar Chart)")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("calorie_category:N", title="Calorie Category"),
            y=alt.Y("product_count:Q", title="Number of Products"),
            color=alt.Color("calorie_category:N", legend=None)
        )
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "6. Products with sugar_to_carb_ratio > 0.7":
        n = st.slider("Select number of top products to view", min_value=5, max_value=len(df), value=10)
        top_df = df.head(n)
        chart = alt.Chart(top_df).mark_bar().encode(
            y=alt.Y("product_name:N", sort='-x', title="Product"),
            x=alt.X("sugar_to_carb_ratio:Q", title="Sugar/Carb Ratio"),
            color=alt.Color("sugar_to_carb_ratio:Q", scale=alt.Scale(scheme="purples"))
        )
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "7. Average sugar_to_carb_ratio per calorie_category":
        st.subheader("🍬Average Sugar-to-Carb Ratio by Calorie Category (Bar Chart)")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("calorie_category:N", title="Calorie Category"),
            y=alt.Y("avg_ratio:Q", title="Avg Sugar/Carb Ratio"),
            color=alt.Color("avg_ratio:Q", scale=alt.Scale(scheme="browns"))
        )
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "4. Products that are both High Calorie and High Sugar":

        # Count per brand
        brand_counts = df.groupby("brand").size().reset_index(name="count").sort_values("count", ascending=False)

        st.subheader("🚨 Top Brands with High Calorie & High Sugar Products (Bar Chart)")

        # Slider for top N brands
        n = st.slider("Select number of top brands to view", min_value=3, max_value=len(brand_counts), value=5)
        top_brands = brand_counts.head(n)

        # Bar chart
        chart = alt.Chart(top_brands).mark_bar().encode(
            x=alt.X("brand:N", sort='-y', title="Brand"),
            y=alt.Y("count:Q", title="Number of High Calorie & High Sugar Products"),
            color=alt.Color("count:Q", scale=alt.Scale(scheme="reds"))
        )
        st.altair_chart(chart, use_container_width=True)

# -----------------------------
# Tab 4: Join Queries
# -----------------------------
with tabs[3]:
    st.header("📑 Join Queries & Visualizations")

    join_queries = {
        # 1. Top 5 brands with most High Calorie products
        "1. Top 5 brands with most High Calorie products": """
            SELECT p.brand, COUNT(*) AS high_calorie_count
            FROM derived_metrics d
            JOIN product_info p ON d.product_code = p.product_code
            WHERE d.calorie_category='High Calorie'
            GROUP BY p.brand
            ORDER BY high_calorie_count DESC
            LIMIT 5;
        """,

        # 2. Average energy_kcal_value for each calorie_category
        "2. Average energy_kcal_value per calorie_category": """
            SELECT d.calorie_category, AVG(n.energy_kcal_value) AS avg_energy
            FROM derived_metrics d
            JOIN nutrient_info n ON d.product_code = n.product_code
            GROUP BY d.calorie_category;
        """,

        # 3. Count of ultra-processed products per brand
        "3. Count of ultra-processed products per brand": """
            SELECT p.brand, COUNT(*) AS ultra_count
            FROM derived_metrics d
            JOIN product_info p ON d.product_code = p.product_code
            WHERE d.is_ultra_processed='Yes'
            GROUP BY p.brand
            ORDER BY ultra_count DESC;
        """,

        # 4. Products with High Sugar and High Calorie along with brand
        "4. High Sugar & High Calorie products with brand": """
            SELECT p.product_name, p.brand, n.energy_kcal_value, n.sugars_value
            FROM derived_metrics d
            JOIN product_info p ON d.product_code = p.product_code
            JOIN nutrient_info n ON d.product_code = n.product_code
            WHERE d.calorie_category='High Calorie' AND d.sugar_category='High Sugar';
        """,

        # 5. Average sugar content per brand for ultra-processed products
        "5. Average sugar value per brand (Ultra-Processed Products)": """
            SELECT p.brand, AVG(n.sugars_value) AS avg_sugars
            FROM derived_metrics d
            JOIN product_info p ON d.product_code = p.product_code
            JOIN nutrient_info n ON d.product_code = n.product_code
            WHERE d.is_ultra_processed='Yes'
            GROUP BY p.brand;
        """,

        # 6. Number of products with fruits/vegetables/nuts content in each calorie_category
        "6. Products with fruits/vegetables/nuts per calorie_category": """
            SELECT d.calorie_category, COUNT(*) AS fv_nuts_count
            FROM derived_metrics d
            JOIN nutrient_info n ON d.product_code = n.product_code
            WHERE n.fruits_veg_nuts_pct > 0
            GROUP BY d.calorie_category;
        """,

        # 7. Top 5 products by sugar_to_carb_ratio with their calorie and sugar category
        "7. Top 5 products by sugar_to_carb_ratio": """
            SELECT p.product_name, d.calorie_category, d.sugar_category, d.sugar_to_carb_ratio
            FROM derived_metrics d
            JOIN product_info p ON d.product_code = p.product_code
            ORDER BY d.sugar_to_carb_ratio DESC
            LIMIT 5;
        """
    }

    selected_query = st.selectbox("Choose a Join Query", list(join_queries.keys()))
    query = join_queries[selected_query]

    # Run the query and get dataframe
    df = run_query(query)
    st.dataframe(df, height=400)

    # --- Automatic Visualizations ---
    if selected_query == "1. Top 5 brands with most High Calorie products":
        chart = alt.Chart(df).mark_bar().encode(
            y=alt.Y("brand:N", sort='-x', title="Brand"),
            x=alt.X("high_calorie_count:Q", title="High Calorie Product Count"),
            color=alt.Color("high_calorie_count:Q", scale=alt.Scale(scheme="purplebluegreen"))
        )
        st.subheader("🏆 Top 5 Brands with Most High Calorie Products (Bar Chart)")
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "2. Average energy_kcal_value per calorie_category":
        df = pd.DataFrame({
            'calorie_category': ['High Calorie', 'Moderate Calorie', 'Low Calorie'],
            'avg_energy': [58.7, 32.6, 8.7]
        })

        # Donut chart
        chart = alt.Chart(df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta('avg_energy:Q', stack=True),
            color=alt.Color('calorie_category:N', title='Calorie Category'),
            tooltip=['calorie_category', 'avg_energy']
        )

        st.subheader("🍩 Average Energy per Calorie Category (Donut Chart)")
        st.altair_chart(chart, use_container_width=True)


    elif selected_query == "3. Count of ultra-processed products per brand":
        st.subheader("🏭 Ultra-Processed Products per Brand (Top N Selection)")

        # Slider to select top N brands
        n = st.slider(
            "Select number of top brands to view",
            min_value=5,
            max_value=len(df),
            value=10
        )

        # Sort and take top N
        top_df = df.sort_values("ultra_count", ascending=False).head(n)

        # Horizontal bar chart
        chart = alt.Chart(top_df).mark_bar().encode(
            y=alt.Y("brand:N", sort='-x', title="Brand"),
            x=alt.X("ultra_count:Q", title="Ultra-Processed Product Count"),
            color=alt.Color("ultra_count:Q", scale=alt.Scale(scheme="redpurple")),
            tooltip=["brand", "ultra_count"]
        )

        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "4. High Sugar & High Calorie products with brand":
        st.subheader("🍭 High Sugar & High Calorie Products by Brand(Scatter Plot)")

        # --- Slider to control zoom level (filtering out top % outliers) ---
        zoom_percent = st.slider(
            "Select zoom level (ignore top % outliers):",
            min_value=90,
            max_value=100,
            value=99,
            step=1
        )

         # --- Calculate percentile cutoffs based on slider ---
        x_min, x_max = df["energy_kcal_value"].quantile([(100 - zoom_percent)/100, zoom_percent/100])
        y_min, y_max = df["sugars_value"].quantile([(100 - zoom_percent)/100, zoom_percent/100])

        # --- Scatter plot ---
        chart = alt.Chart(df).mark_circle(size=100).encode(
            x=alt.X("energy_kcal_value:Q",
                title="Energy (kcal)",
                scale=alt.Scale(domain=[x_min, x_max])),
            y=alt.Y("sugars_value:Q",
                title="Sugar (g)",
                scale=alt.Scale(domain=[y_min, y_max])),
            color=alt.Color("brand:N", title="Brand"),
            tooltip=["product_name", "brand", "energy_kcal_value", "sugars_value"]
            ).interactive()

        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "5. Average sugar value per brand (Ultra-Processed Products)":
        st.subheader("🍬 Average Sugar Content per Brand (Top N selection)")

        if df.empty:
            st.warning("No data available for ultra-processed products.")
            st.stop()

        # --- Slider for top brands ---
        n = st.slider("Select number of top brands to view", min_value=5, max_value=len(df), value=10)
        top_df = df.nlargest(n, 'avg_sugars')

        chart = alt.Chart(top_df).mark_bar().encode(
            y=alt.Y('brand:N', sort='-x', title='Brand'),
            x=alt.X('avg_sugars:Q', title='Average Sugar (g)'),
            color=alt.Color('avg_sugars:Q', scale=alt.Scale(scheme='brownbluegreen'), title="Average Sugar (g)"),  # scheme applied here
            tooltip=['brand', 'avg_sugars']
        ).properties(height=400)


        st.altair_chart(chart.interactive(), use_container_width=True)

    elif selected_query == "6. Products with fruits/vegetables/nuts per calorie_category":
        st.subheader("🥗 Products with Fruits/Vegetables/Nuts by Calorie Category (Stacked Bar Chart)")
        
        # Assuming df has 'calorie_category', 'fv_nuts_count', 'total_products'
        df['total_products'] = df['fv_nuts_count'].sum()  # or compute per calorie_category if needed
        df['other_products'] = df['total_products'] - df['fv_nuts_count']

        # Melt for stacked bar
        df_melted = df.melt(
            id_vars='calorie_category',
            value_vars=['fv_nuts_count', 'other_products'],
            var_name='Product Type',
            value_name='Count'
        )

        # Stacked bar chart
        chart = alt.Chart(df_melted).mark_bar().encode(
            x=alt.X('calorie_category:N', title='Calorie Category'),
            y=alt.Y('Count:Q', title='Number of Products'),
            color=alt.Color('Product Type:N', scale=alt.Scale(scheme='greens'), title='Product Type'),
            tooltip=['calorie_category', 'Product Type', 'Count']
        ).properties(height=400)
        st.altair_chart(chart, use_container_width=True)

    elif selected_query == "7. Top 5 products by sugar_to_carb_ratio":
        # Donut chart
        st.subheader("🍭 Top 5 Products by Sugar-to-Carb Ratio (Donut Chart)")
        chart = alt.Chart(df).mark_arc(innerRadius=90).encode(
            theta=alt.Theta("sugar_to_carb_ratio:Q"),
            color=alt.Color("product_name:N", title="Product"),
            tooltip=["product_name", "calorie_category", "sugar_category", "sugar_to_carb_ratio"]
        )
        st.altair_chart(chart, use_container_width=True)




