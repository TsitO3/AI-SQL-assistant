import plotly.express as px

def create_chart(df):

    numeric_cols = df.select_dtypes(include="number").columns
    categorical_cols = df.select_dtypes(exclude="number").columns

    # ❌ pas assez de données
    if len(numeric_cols) == 0 or len(categorical_cols) == 0:
        return None

    x = categorical_cols[0]

    # CASE 1: 1 seule variable numérique
    if len(numeric_cols) == 1:

        y = numeric_cols[0]

        return px.bar(df, x=x, y=y)

    # CASE 2: plusieurs variables numériques
    else:

        # transformer en format long
        df_long = df.melt(
            id_vars=[x],
            value_vars=list(numeric_cols),
            var_name="Metric",
            value_name="Value"
        )

        return px.line(
            df_long,
            x=x,
            y="Value",
            color="Metric"
        )