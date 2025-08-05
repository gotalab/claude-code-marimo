import marimo

__generated_with = "0.14.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import pandas as pd
    import numpy as np
    import marimo as mo
    import duckdb
    import plotly.express as px
    import plotly.graph_objects as go
    from pathlib import Path
    return Path, duckdb, mo, pd, px


@app.cell
def _(Path, mo, pd):
    # Load Titanic dataset
    data_path = Path("data/raw/train.csv")

    if data_path.exists():
        df = pd.read_csv(data_path)
        print(f"✅ Loaded Titanic dataset: {df.shape}")
        print(f"Columns: {list(df.columns)}")
    else:
        raise FileNotFoundError(f"Data file not found: {data_path}")
    mo.ui.dataframe(df)
    return (df,)


@app.cell
def _(df, mo):
    _df = mo.sql(
        f"""
        SELECT 
            Pclass, 
            COUNT(DISTINCT PassengerId) as p_cnt 
        FROM df 
        GROUP BY Pclass 
        ORDER BY p_cnt DESC;
        """
    )
    return


@app.cell
def _(df, mo, pd):
    # Data quality overview
    mo.md("""
    ## Data Quality Assessment
    """)

    # Missing values analysis
    missing_data = df.isnull().sum()
    missing_pct = (missing_data / len(df) * 100).round(2)

    quality_df = pd.DataFrame({
        'Missing_Count': missing_data,
        'Missing_Percentage': missing_pct,
        'Data_Type': df.dtypes
    }).sort_values('Missing_Count', ascending=False)

    print("📊 Missing Data Summary:")
    quality_df[quality_df['Missing_Count'] > 0]
    return


@app.cell
def _(df):
    # Survival rate overview
    survival_rate = df['Survived'].mean()
    total_passengers = len(df)
    survivors = df['Survived'].sum()

    print(f"🚢 Titanic Survival Statistics:")
    print(f"Total Passengers: {total_passengers:,}")
    print(f"Survivors: {survivors:,}")
    print(f"Overall Survival Rate: {survival_rate:.1%}")

    # Survival by basic demographics
    survival_summary = df.groupby(['Sex', 'Pclass'])['Survived'].agg([
        'count', 'sum', 'mean'
    ]).round(3)
    survival_summary.columns = ['Total', 'Survived', 'Survival_Rate']
    survival_summary
    return


@app.cell
def _(df, duckdb):
    # SQL Analysis with DuckDB
    conn = duckdb.connect()
    conn.register('titanic', df)

    # Age group analysis
    age_analysis = conn.execute("""
        SELECT 
            CASE 
                WHEN Age IS NULL THEN 'Unknown'
                WHEN Age < 12 THEN 'Child'
                WHEN Age BETWEEN 12 AND 17 THEN 'Teen'
                WHEN Age BETWEEN 18 AND 35 THEN 'Young Adult'
                WHEN Age BETWEEN 36 AND 60 THEN 'Adult'
                ELSE 'Senior'
            END as age_group,
            Sex,
            COUNT(*) as passengers,
            SUM(Survived) as survivors,
            ROUND(AVG(Survived), 3) as survival_rate,
            ROUND(AVG(Fare), 2) as avg_fare
        FROM titanic
        GROUP BY age_group, Sex
        ORDER BY survival_rate DESC
    """).df()

    print("👥 Survival Analysis by Age Group and Gender:")
    age_analysis
    return (conn,)


@app.cell
def _(conn):
    # Fare and class analysis
    fare_class_analysis = conn.execute("""
        SELECT 
            Pclass,
            CASE 
                WHEN Fare < 10 THEN 'Low (< £10)'
                WHEN Fare BETWEEN 10 AND 30 THEN 'Medium (£10-30)'
                WHEN Fare BETWEEN 30 AND 100 THEN 'High (£30-100)'
                ELSE 'Premium (> £100)'
            END as fare_category,
            COUNT(*) as passengers,
            SUM(Survived) as survivors,
            ROUND(AVG(Survived), 3) as survival_rate,
            ROUND(MIN(Fare), 2) as min_fare,
            ROUND(MAX(Fare), 2) as max_fare,
            ROUND(AVG(Fare), 2) as avg_fare
        FROM titanic
        WHERE Fare IS NOT NULL
        GROUP BY Pclass, fare_category
        ORDER BY Pclass, avg_fare
    """).df()

    print("💰 Survival by Class and Fare Category:")
    fare_class_analysis
    return


@app.cell
def _(df):
    # Family size impact
    df_family = df.copy()
    df_family['Family_Size'] = df_family['SibSp'] + df_family['Parch'] + 1
    df_family['Family_Category'] = df_family['Family_Size'].apply(
        lambda x: 'Alone' if x == 1 
                 else 'Small (2-4)' if x <= 4 
                 else 'Large (5+)'
    )

    family_survival = df_family.groupby(['Family_Category', 'Pclass'])['Survived'].agg([
        'count', 'sum', 'mean'
    ]).round(3)
    family_survival.columns = ['Total', 'Survived', 'Survival_Rate']

    print("👨‍👩‍👧‍👦 Family Size Impact on Survival:")
    family_survival
    return (df_family,)


@app.cell
def _(conn, df_family):
    # Advanced survival patterns
    conn.register('titanic_family', df_family)

    survival_patterns = conn.execute("""
        SELECT 
            Sex,
            Pclass,
            Family_Category,
            CASE 
                WHEN Age < 18 THEN 'Minor'
                ELSE 'Adult'
            END as age_category,
            COUNT(*) as passengers,
            SUM(Survived) as survivors,
            ROUND(AVG(Survived), 3) as survival_rate,
            ROUND(AVG(Fare), 2) as avg_fare
        FROM titanic_family
        WHERE Age IS NOT NULL
        GROUP BY Sex, Pclass, Family_Category, age_category
        HAVING COUNT(*) >= 5  -- Only groups with 5+ passengers
        ORDER BY survival_rate DESC
    """).df()

    print("🔍 Detailed Survival Patterns (Groups with 5+ passengers):")
    survival_patterns
    return


@app.cell
def _(df, df_family, pd):
    # Summary insights
    insights = []

    # Gender insight
    male_survival = df[df['Sex'] == 'male']['Survived'].mean()
    female_survival = df[df['Sex'] == 'female']['Survived'].mean()
    insights.append(f"👩 Women had {female_survival/male_survival:.1f}x higher survival rate than men")

    # Class insight
    class1_survival = df[df['Pclass'] == 1]['Survived'].mean()
    class3_survival = df[df['Pclass'] == 3]['Survived'].mean()
    insights.append(f"🥇 1st class passengers had {class1_survival/class3_survival:.1f}x higher survival rate than 3rd class")

    # Age insight
    children_survival = df[df['Age'] < 18]['Survived'].mean()
    adult_survival = df[df['Age'] >= 18]['Survived'].mean()
    if not pd.isna(children_survival) and not pd.isna(adult_survival):
        insights.append(f"👶 Children had {children_survival/adult_survival:.1f}x higher survival rate than adults")

    # Family insight
    alone_survival = df_family[df_family['Family_Category'] == 'Alone']['Survived'].mean()
    small_family_survival = df_family[df_family['Family_Category'] == 'Small (2-4)']['Survived'].mean()
    insights.append(f"👥 Small families had {small_family_survival/alone_survival:.1f}x higher survival rate than solo travelers")

    print("💡 Key Insights:")
    for insight in insights:
        print(f"  • {insight}")

    return


@app.cell
def _(df, mo, pd, px):
    # Executive Summary UI with Charts
    mo.md("""
    ---
    ## 📋 Executive Summary
    """)

    # Create survival rate charts

    # 1. Gender survival chart
    gender_data = df.groupby('Sex')['Survived'].agg(['count', 'sum', 'mean']).reset_index()
    gender_chart = px.bar(
        gender_data, 
        x='Sex', 
        y='mean',
        title='Survival Rate by Gender',
        labels={'mean': 'Survival Rate', 'Sex': 'Gender'},
        color='Sex',
        color_discrete_map={'male': '#1f77b4', 'female': '#ff7f0e'}
    )
    gender_chart.update_yaxes(tickformat='.1%')

    # 2. Class survival chart
    class_data = df.groupby('Pclass')['Survived'].agg(['count', 'sum', 'mean']).reset_index()
    class_chart = px.bar(
        class_data,
        x='Pclass',
        y='mean', 
        title='Survival Rate by Passenger Class',
        labels={'mean': 'Survival Rate', 'Pclass': 'Class'},
        color='Pclass',
        color_discrete_sequence=['#2ca02c', '#ff7f0e', '#d62728']
    )
    class_chart.update_yaxes(tickformat='.1%')
    class_chart.update_xaxes(tickmode='array', tickvals=[1, 2, 3], ticktext=['1st', '2nd', '3rd'])

    # 3. Age distribution chart
    age_bins = pd.cut(df['Age'].dropna(), bins=[0, 12, 18, 35, 60, 100], labels=['Child', 'Teen', 'Young Adult', 'Adult', 'Senior'])
    age_survival = df.groupby(age_bins)['Survived'].agg(['count', 'sum', 'mean']).reset_index()
    age_chart = px.bar(
        age_survival,
        x='Age',
        y='mean',
        title='Survival Rate by Age Group',
        labels={'mean': 'Survival Rate', 'Age': 'Age Group'},
        color='mean',
        color_continuous_scale='viridis'
    )
    age_chart.update_yaxes(tickformat='.1%')

    # 4. Overall survival pie chart
    survival_counts = df['Survived'].value_counts()
    pie_chart = px.pie(
        values=survival_counts.values,
        names=['Died', 'Survived'],
        title='Overall Survival Distribution',
        color_discrete_sequence=['#d62728', '#2ca02c']
    )

    # Create tabs with charts
    charts_tab = mo.vstack([
        mo.hstack([gender_chart, class_chart]),
        mo.hstack([age_chart, pie_chart])
    ])

    # Statistics summary chart
    demographics_data = []
    for sex in ['male', 'female']:
        for pclass in [1, 2, 3]:
            subset = df[(df['Sex'] == sex) & (df['Pclass'] == pclass)]
            if len(subset) > 0:
                demographics_data.append({
                    'Gender': sex,
                    'Class': f'{pclass}',
                    'Survival_Rate': subset['Survived'].mean(),
                    'Count': len(subset)
                })

    demographics_df = pd.DataFrame(demographics_data)
    heatmap_chart = px.scatter(
        demographics_df,
        x='Class',
        y='Gender',
        size='Count',
        color='Survival_Rate',
        title='Survival Rate Heatmap by Gender and Class',
        color_continuous_scale='RdYlGn',
        size_max=50
    )

    statistics_tab = heatmap_chart

    # Data quality chart
    exec_missing_data = df.isnull().sum()
    exec_missing_pct = (exec_missing_data / len(df) * 100)
    missing_df = pd.DataFrame({
        'Column': exec_missing_data.index,
        'Missing_Count': exec_missing_data.values,
        'Missing_Percentage': exec_missing_pct.values
    }).query('Missing_Count > 0').sort_values('Missing_Count', ascending=True)

    quality_chart = px.bar(
        missing_df,
        x='Missing_Percentage',
        y='Column',
        orientation='h',
        title='Missing Data by Column',
        labels={'Missing_Percentage': 'Missing Percentage (%)', 'Column': 'Column'},
        color='Missing_Percentage',
        color_continuous_scale='Reds'
    )

    data_quality_tab = quality_chart

    # Create tabs with charts
    exec_summary_content = mo.ui.tabs({
        "📊 Key Charts": charts_tab,
        "📈 Demographics": statistics_tab,
        "⚠️ Data Quality": data_quality_tab
    })

    exec_summary_content
    return


if __name__ == "__main__":
    app.run()
