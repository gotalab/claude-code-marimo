import marimo

__generated_with = "0.10.6"
app = marimo.App(width="medium")


@app.cell
def __():
    import pandas as pd
    import marimo as mo
    import duckdb
    return duckdb, mo, pd


@app.cell
def __(pd):
    # Create sample data
    data = {
        'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
        'age': [25, 30, 35, 28, 32],
        'city': ['Tokyo', 'Osaka', 'Kyoto', 'Tokyo', 'Osaka'],
        'salary': [50000, 60000, 70000, 55000, 65000]
    }
    
    df = pd.DataFrame(data)
    df
    return data, df


@app.cell
def __(df):
    # Basic statistics
    stats = df.describe()
    stats
    return (stats,)


@app.cell
def __(df):
    # Group by city
    city_stats = df.groupby('city').agg({
        'age': 'mean',
        'salary': ['mean', 'count']
    }).round(2)
    city_stats
    return (city_stats,)


@app.cell
def __(df):
    # Filter high earners
    high_earners = df[df['salary'] > 60000]
    high_earners
    return (high_earners,)


@app.cell
def __(df):
    # Data visualization preparation
    age_salary_corr = df['age'].corr(df['salary'])
    print(f"Age-Salary correlation: {age_salary_corr:.3f}")
    
    # Add new calculated column
    df_enhanced = df.copy()
    df_enhanced['salary_per_age'] = df_enhanced['salary'] / df_enhanced['age']
    df_enhanced = df_enhanced.sort_values('salary_per_age', ascending=False)
    df_enhanced
    return age_salary_corr, df_enhanced


@app.cell
def __(df):
    # Summary statistics by city
    summary = df.pivot_table(
        values=['age', 'salary'], 
        index='city', 
        aggfunc=['mean', 'std']
    ).round(2)
    summary
    return (summary,)


@app.cell
def __(df, duckdb):
    # SQL analysis with DuckDB
    conn = duckdb.connect()
    
    # Register DataFrame as a table
    conn.register('employees', df)
    
    # SQL query: City-wise employee analysis
    sql_result = conn.execute("""
        SELECT 
            city,
            COUNT(*) as employee_count,
            AVG(age) as avg_age,
            AVG(salary) as avg_salary,
            MIN(salary) as min_salary,
            MAX(salary) as max_salary,
            ROUND(AVG(salary) / AVG(age), 2) as salary_per_age_ratio
        FROM employees 
        GROUP BY city
        ORDER BY avg_salary DESC
    """).df()
    
    sql_result
    return conn, sql_result


@app.cell
def __(conn):
    # Advanced SQL: Window functions
    advanced_sql = conn.execute("""
        SELECT 
            name,
            city,
            age,
            salary,
            RANK() OVER (PARTITION BY city ORDER BY salary DESC) as salary_rank_in_city,
            salary - AVG(salary) OVER (PARTITION BY city) as salary_diff_from_city_avg,
            CASE 
                WHEN salary > AVG(salary) OVER () THEN 'Above Average'
                ELSE 'Below Average'
            END as performance_category
        FROM employees
        ORDER BY city, salary DESC
    """).df()
    
    advanced_sql
    return (advanced_sql,)


@app.cell
def __(df, pd):
    # Load Titanic dataset and basic analysis
    import os
    
    # Check if data exists
    data_path = "data/raw/train.csv"
    if os.path.exists(data_path):
        titanic = pd.read_csv(data_path)
        print(f"Titanic dataset shape: {titanic.shape}")
        print(f"\nColumns: {list(titanic.columns)}")
        print(f"\nMissing values:\n{titanic.isnull().sum()}")
        
        # Survival rate by class
        survival_by_class = titanic.groupby('Pclass')['Survived'].agg(['count', 'sum', 'mean']).round(3)
        survival_by_class.columns = ['Total', 'Survived', 'Survival_Rate']
        survival_by_class
    else:
        print(f"Data file not found at {data_path}")
        titanic = None
        survival_by_class = None
    
    return titanic, survival_by_class


@app.cell
def __(titanic, conn):
    # SQL analysis on Titanic data
    if titanic is not None:
        # Register Titanic data as SQL table
        conn.register('titanic', titanic)
        
        # Complex SQL query: Age groups and survival analysis
        titanic_analysis = conn.execute("""
            SELECT 
                CASE 
                    WHEN Age < 18 THEN 'Child'
                    WHEN Age BETWEEN 18 AND 35 THEN 'Young Adult'
                    WHEN Age BETWEEN 36 AND 60 THEN 'Adult'
                    ELSE 'Senior'
                END as age_group,
                Sex,
                Pclass,
                COUNT(*) as total_passengers,
                SUM(Survived) as survivors,
                ROUND(AVG(Survived), 3) as survival_rate,
                ROUND(AVG(Fare), 2) as avg_fare
            FROM titanic 
            WHERE Age IS NOT NULL
            GROUP BY age_group, Sex, Pclass
            ORDER BY survival_rate DESC
        """).df()
        
        titanic_analysis
    else:
        titanic_analysis = None
        
    return (titanic_analysis,)


@app.cell
def __(df, titanic):
    # Intentional errors to demonstrate debugging
    print("Testing error handling...")
    
    # Error 1: KeyError - accessing non-existent column
    try:
        result1 = df['non_existent_column']
    except KeyError as e:
        print(f"KeyError: {e}")
    
    # Error 2: Division by zero
    try:
        result2 = 10 / 0
    except ZeroDivisionError as e:
        print(f"ZeroDivisionError: {e}")
    
    # Error 3: Wrong function usage
    try:
        result3 = titanic.groupby('InvalidColumn').mean()
    except KeyError as e:
        print(f"GroupBy KeyError: {e}")
    
    # Error 4: Type error with string operation
    try:
        result4 = "hello" + 5
    except TypeError as e:
        print(f"TypeError: {e}")
    
    print("All errors caught successfully!")
    return None


if __name__ == "__main__":
    app.run()