import streamlit as st
import pandas as pd
import altair as alt

# 1. Título de la app
st.set_page_config(page_title="Dashboard Inventario", layout="wide")
st.title("Dashboard de Inventario y Ventas")

# 2. Cargar datos
@st.cache_data
def load_data(path):
    # Lee el Excel usando pandas
    return pd.read_excel(path, engine="openpyxl")

df = load_data("Data_Dashboard.xlsx")

# 3. Selector de División principal
divisiones = ["Almacen", "Taller"]
seleccion_div = st.sidebar.radio("División", divisiones)

# Filtrar el DataFrame por la división elegida
# Ajusta el .str.capitalize() si tus valores vienen en mayúsculas o minúsculas distintas
df = df[df["COMERCIO"].str.capitalize() == seleccion_div]

# Muestra un vistazo de los datos (puedes comentar esta línea después)
#st.dataframe(df.head())

# 4. Filtros
categorias = ["Todas"] + sorted(df["CATEGORIA"].unique().tolist())
subcats    = ["Todas"] + sorted(df["SUBCATEGORIA"].unique().tolist())
marcas     = ["Todas"] + sorted(df["MARCA"].unique().tolist())

col1, col2, col3 = st.columns(3)
with col1:
    sel_cat = st.selectbox("Categoría", categorias)
with col2:
    sel_sub = st.selectbox("Subcategoría", subcats)
with col3:
    sel_mar = st.selectbox("Marca", marcas)

# Aplica filtros al DataFrame
df_filtrado = df.copy()
if sel_cat != "Todas":
    df_filtrado = df_filtrado[df_filtrado["CATEGORIA"] == sel_cat]
if sel_sub != "Todas":
    df_filtrado = df_filtrado[df_filtrado["SUBCATEGORIA"] == sel_sub]
if sel_mar != "Todas":
    df_filtrado = df_filtrado[df_filtrado["MARCA"] == sel_mar]

# 4. Cálculo de KPIs (usa round() en lugar de .round())
avg_dsi   = round(df_filtrado["PROMEDIO_DIAS_VENTAS"].mean(), 1)
margin_pct  = round(df_filtrado["margen_bruto_%"].mean(), 1)
avg_beneficio = round(df_filtrado["beneficio_promedio_por_producto"].mean(), 1)
total_skus  = df_filtrado["CODIGO"].nunique()

# Mostrar KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("DSI Promedio", f"{avg_dsi}")
k2.metric("Margen Bruto %", f"{margin_pct}%")
k3.metric("Beneficio Neto Promedio", f"${avg_beneficio}")
k4.metric("Total SKUs", f"{total_skus}")

# 5. DSI por categoría
dsi_cat = (
    df_filtrado
    .groupby("CATEGORIA")["PROMEDIO_DIAS_VENTAS"]
    .mean()
    .reset_index()
    .rename(columns={"PROMEDIO_DIAS_VENTAS":"DSI Promedio"})
)

chart_bar = (
    alt.Chart(dsi_cat)
    .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
    .encode(
        x=alt.X("CATEGORIA:N", title="Categoría"),
        y=alt.Y("DSI Promedio:Q", title="Promedio DSI"),
        tooltip=["CATEGORIA", "DSI Promedio"]
    )
    .properties(height=250)
)
st.altair_chart(chart_bar, use_container_width=True)

# Distribución de SKUs
dist_cat = (
    df_filtrado
    .groupby("CATEGORIA")["CODIGO"]
    .nunique()
    .reset_index()
    .rename(columns={"CODIGO":"Conteo_SKU"})
)

pie = (
    alt.Chart(dist_cat)
    .mark_arc(innerRadius=50)
    .encode(
        theta=alt.Theta("Conteo_SKU:Q"),
        color=alt.Color("CATEGORIA:N", legend=alt.Legend(title="Categoría")),
        tooltip=["CATEGORIA", "Conteo_SKU"]
    )
    .properties(height=300)
)
st.altair_chart(pie, use_container_width=True)


# Top 5 slow movers
top_slow = (
    df_filtrado
    .sort_values("PROMEDIO_DIAS_VENTAS", ascending=False)
    .head(5)
    [["PRODUCTO", "MARCA", "PROMEDIO_DIAS_VENTAS", "beneficio_promedio_por_producto"]]
    .rename(columns={"PROMEDIO_DIAS_VENTAS":"DSI", "beneficio_promedio_por_producto":"BENEFICIO PROMEDIO"})
)

st.subheader("Top Slow Movers")
st.table(top_slow)