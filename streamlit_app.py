
# ============================================================
# DSS PARA LA MEJORA DE LA PRODUCTIVIDAD DE MANO DE OBRA
# Sector metalmecánico
# Herramientas: 5S + SLP + TPM
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# 1. CONFIGURACIÓN GENERAL
# ============================================================

st.set_page_config(
    page_title="DSS | Productividad",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. ESTILO PROFESIONAL - DARK DASHBOARD
# ============================================================

st.markdown("""
<style>

/* FONDO GENERAL */
.stApp {
    background:
        radial-gradient(
            circle at 85% 5%,
            rgba(37, 99, 235, 0.10),
            transparent 25%
        ),
        #080B10;
    color: #F3F4F6;
}

/* CONTENEDOR PRINCIPAL */
.block-container {
    padding-top: 1.3rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #0D1117;
    border-right: 1px solid #242B36;
}

[data-testid="stSidebar"] * {
    color: #E5E7EB;
}

/* TÍTULOS */
h1 {
    color: #F9FAFB !important;
    font-size: 2.05rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px;
}

h2 {
    color: #F3F4F6 !important;
    font-size: 1.35rem !important;
    font-weight: 650 !important;
}

h3 {
    color: #E5E7EB !important;
    font-size: 1.05rem !important;
}

p {
    color: #CBD5E1;
}

/* KPI */
[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        #121821,
        #0E131B
    );
    border: 1px solid #252E3A;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0px 5px 18px rgba(0,0,0,0.20);
}

[data-testid="stMetricLabel"] {
    color: #94A3B8 !important;
    font-size: 0.77rem !important;
    font-weight: 500;
}

[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.45rem !important;
    font-weight: 700 !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #0D1117;
    padding: 6px;
    border-radius: 10px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    color: #94A3B8;
    padding-left: 16px;
    padding-right: 16px;
}

.stTabs [aria-selected="true"] {
    background-color: #18202C !important;
    color: #FFFFFF !important;
}

/* SELECTORES */
[data-baseweb="select"] > div {
    background-color: #111720 !important;
    border-color: #293240 !important;
}

/* FILE UPLOADER */
[data-testid="stFileUploader"] {
    background-color: #10151D;
    border-radius: 10px;
}

/* EXPANDER */
[data-testid="stExpander"] {
    background-color: #0E131B;
    border: 1px solid #252E3A;
    border-radius: 10px;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border: 1px solid #252E3A;
    border-radius: 10px;
}

/* DIVISORES */
hr {
    border-color: #202733 !important;
}

/* OCULTAR MENÚ STREAMLIT */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# 3. COLUMNAS REQUERIDAS
# ============================================================

COLUMNAS_REQUERIDAS = [
    "periodo",
    "tipo_tanque",
    "horas_hombre",
    "unidades_producidas",
    "horas_extra",
    "tiempo_busqueda_min",
    "recorrido_m",
    "paradas_h",
    "numero_fallas",
    "checklist_5s_pct"
]


# ============================================================
# 4. VALIDACIÓN DE DATOS
# ============================================================

def validar_datos(df):

    faltantes = [
        columna
        for columna in COLUMNAS_REQUERIDAS
        if columna not in df.columns
    ]

    if faltantes:
        return False, (
            "Faltan las siguientes columnas: "
            + ", ".join(faltantes)
        )

    columnas_numericas = [
        "horas_hombre",
        "unidades_producidas",
        "horas_extra",
        "tiempo_busqueda_min",
        "recorrido_m",
        "paradas_h",
        "numero_fallas",
        "checklist_5s_pct"
    ]

    for columna in columnas_numericas:

        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        )

    if df[columnas_numericas].isnull().any().any():

        return False, (
            "Existen valores vacíos o no numéricos "
            "en la base de datos."
        )

    if (df[columnas_numericas] < 0).any().any():

        return False, (
            "Se encontraron valores negativos."
        )

    if (df["horas_hombre"] <= 0).any():

        return False, (
            "Las horas-hombre deben ser mayores a cero."
        )

    if (
        (df["checklist_5s_pct"] < 0)
        |
        (df["checklist_5s_pct"] > 100)
    ).any():

        return False, (
            "El cumplimiento del Checklist 5S "
            "debe encontrarse entre 0% y 100%."
        )

    return True, "Base validada correctamente."


# ============================================================
# 5. PREPARAR AÑO Y MES
# ============================================================

def preparar_periodo(df):

    df = df.copy()

    meses = {
        "ene": 1,
        "enero": 1,
        "feb": 2,
        "febrero": 2,
        "mar": 3,
        "marzo": 3,
        "abr": 4,
        "abril": 4,
        "may": 5,
        "mayo": 5,
        "jun": 6,
        "junio": 6,
        "jul": 7,
        "julio": 7,
        "ago": 8,
        "agosto": 8,
        "sep": 9,
        "sept": 9,
        "septiembre": 9,
        "oct": 10,
        "octubre": 10,
        "nov": 11,
        "noviembre": 11,
        "dic": 12,
        "diciembre": 12
    }

    nombres_meses = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre"
    }

    def extraer_periodo(valor):

        texto = str(valor).lower().strip()

        texto = (
            texto
            .replace("/", "-")
            .replace("_", "-")
        )

        año = None
        mes = None

        partes = texto.split("-")

        for parte in partes:

            parte = parte.strip()

            if (
                parte.isdigit()
                and len(parte) == 4
            ):
                año = int(parte)

            if parte in meses:
                mes = meses[parte]

        if año is None:

            for token in texto.split():

                if (
                    token.isdigit()
                    and len(token) == 4
                ):
                    año = int(token)

        if mes is None:

            for nombre, numero in meses.items():

                if nombre in texto:
                    mes = numero
                    break

        return pd.Series([año, mes])

    df[
        ["anio", "mes_num"]
    ] = df["periodo"].apply(
        extraer_periodo
    )

    df["mes"] = (
        df["mes_num"]
        .map(nombres_meses)
    )

    return df


# ============================================================
# 6. INDICADORES
# ============================================================

def calcular_indicadores(df):

    df = df.copy()

    df["productividad_unid_hh"] = (
        df["unidades_producidas"]
        /
        df["horas_hombre"]
    )

    df["busqueda_h"] = (
        df["tiempo_busqueda_min"]
        /
        60
    )

    return df


# ============================================================
# 7. MOTOR DE DIAGNÓSTICO DSS
# ============================================================

def diagnostico_dss(df):

    # Valores máximos utilizados para normalizar
    # los indicadores a una escala comparable.

    busqueda_max = max(
        df["tiempo_busqueda_min"].max(),
        1
    )

    recorrido_max = max(
        df["recorrido_m"].max(),
        1
    )

    paradas_max = max(
        df["paradas_h"].max(),
        1
    )

    fallas_max = max(
        df["numero_fallas"].max(),
        1
    )

    # --------------------------------------------------------
    # SCORE 5S
    # 50% tiempo de búsqueda
    # 50% incumplimiento 5S
    # --------------------------------------------------------

    score_5s = (
        (
            df["tiempo_busqueda_min"].mean()
            /
            busqueda_max
        ) * 50
        +
        (
            (
                100
                -
                df["checklist_5s_pct"].mean()
            )
            /
            100
        ) * 50
    )

    # --------------------------------------------------------
    # SCORE SLP
    # Recorridos
    # --------------------------------------------------------

    score_slp = (
        df["recorrido_m"].mean()
        /
        recorrido_max
    ) * 100

    # --------------------------------------------------------
    # SCORE TPM
    # 60% paradas
    # 40% fallas
    # --------------------------------------------------------

    score_tpm = (
        (
            df["paradas_h"].mean()
            /
            paradas_max
        ) * 60
        +
        (
            df["numero_fallas"].mean()
            /
            fallas_max
        ) * 40
    )

    scores = {
        "5S": score_5s,
        "SLP": score_slp,
        "TPM": score_tpm
    }

    prioridad = max(
        scores,
        key=scores.get
    )

    recomendaciones = {

        "5S":
        """
        Priorizar acciones de clasificación, orden,
        limpieza y estandarización para disminuir
        los tiempos de búsqueda de herramientas
        y materiales.
        """,

        "SLP":
        """
        Revisar la distribución de las áreas,
        proximidad entre operaciones y flujo de
        materiales para disminuir recorridos
        innecesarios.
        """,

        "TPM":
        """
        Priorizar acciones de mantenimiento para
        disminuir fallas y paradas no programadas
        de los equipos.
        """
    }

    return (
        prioridad,
        scores,
        recomendaciones[prioridad]
    )


# ============================================================
# 8. SIMULACIÓN
# ============================================================

def simular_escenario(
    df,
    reduccion_busqueda,
    reduccion_recorrido,
    reduccion_paradas,
    mejora_5s
):

    escenario = df.copy()

    escenario[
        "busqueda_propuesta_min"
    ] = (
        escenario["tiempo_busqueda_min"]
        *
        (1 - reduccion_busqueda / 100)
    )

    escenario[
        "recorrido_propuesto_m"
    ] = (
        escenario["recorrido_m"]
        *
        (1 - reduccion_recorrido / 100)
    )

    escenario[
        "paradas_propuesta_h"
    ] = (
        escenario["paradas_h"]
        *
        (1 - reduccion_paradas / 100)
    )

    escenario[
        "checklist_5s_propuesto"
    ] = np.minimum(
        escenario["checklist_5s_pct"]
        + mejora_5s,
        100
    )

    ahorro_busqueda_h = (
        escenario["tiempo_busqueda_min"]
        -
        escenario["busqueda_propuesta_min"]
    ) / 60

    ahorro_paradas_h = (
        escenario["paradas_h"]
        -
        escenario["paradas_propuesta_h"]
    )

    escenario[
        "horas_potencialmente_recuperadas"
    ] = (
        ahorro_busqueda_h
        +
        ahorro_paradas_h
    )

    escenario[
        "horas_hombre_escenario"
    ] = (
        escenario["horas_hombre"]
        -
        escenario[
            "horas_potencialmente_recuperadas"
        ]
    ).clip(lower=0.01)

    escenario[
        "productividad_escenario"
    ] = (
        escenario["unidades_producidas"]
        /
        escenario["horas_hombre_escenario"]
    )

    return escenario


# ============================================================
# 9. SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## ◈ DSS Productividad"
    )

    st.caption(
        "Panel de análisis y soporte a decisiones"
    )

    st.divider()

    archivo = st.file_uploader(
        "Cargar archivo Excel",
        type=["xlsx"],
        help=(
            "Selecciona la base de datos "
            "del DSS en formato Excel (.xlsx)."
        )
    )

    st.caption(
        "Formato permitido: Excel (.xlsx)"
    )

    st.divider()


# ============================================================
# 10. PANTALLA INICIAL
# ============================================================

if archivo is None:

    st.markdown(
        "# Sistema de Soporte a Decisiones"
    )

    st.markdown(
        "### Mejora de la productividad de mano de obra"
    )

    st.caption(
        "Análisis basado en 5S, "
        "Systematic Layout Planning (SLP) y "
        "Total Productive Maintenance (TPM)."
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("### 01")

        st.markdown(
            "**ANALIZAR**"
        )

        st.caption(
            "Productividad, horas-hombre "
            "y pérdidas operativas."
        )

    with c2:

        st.markdown("### 02")

        st.markdown(
            "**DIAGNOSTICAR**"
        )

        st.caption(
            "Identificación de la principal "
            "oportunidad de mejora."
        )

    with c3:

        st.markdown("### 03")

        st.markdown(
            "**EVALUAR**"
        )

        st.caption(
            "Comparación entre la situación "
            "actual y escenarios propuestos."
        )

    st.info(
        "Carga el archivo Excel desde el panel "
        "lateral para iniciar el análisis."
    )

    st.stop()


# ============================================================
# 11. LEER ARCHIVO EXCEL
# ============================================================

try:

    df = pd.read_excel(
        archivo,
        sheet_name="datos_dss",
        engine="openpyxl"
    )

except ValueError:

    st.error(
        "No se encontró la hoja 'datos_dss' "
        "en el archivo Excel."
    )

    st.info(
        "La hoja principal debe llamarse "
        "exactamente: datos_dss"
    )

    st.stop()

except ImportError:

    st.error(
        "No se encuentra instalada la librería "
        "'openpyxl'."
    )

    st.info(
        "Ejecuta en la Terminal: "
        "uv add openpyxl"
    )

    st.stop()

except Exception as error:

    st.error(
        f"No se pudo leer el archivo Excel: {error}"
    )

    st.stop()


# ============================================================
# 12. LIMPIAR ENCABEZADOS
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.lower()
)


# ============================================================
# 13. VALIDACIÓN
# ============================================================

valido, mensaje = validar_datos(
    df
)

if not valido:

    st.error(mensaje)

    st.warning(
        "Verifica la estructura del archivo Excel."
    )

    st.stop()


# ============================================================
# 14. PREPARAR DATOS
# ============================================================

df = preparar_periodo(df)

df = calcular_indicadores(df)


# ============================================================
# 15. FILTROS DEL DASHBOARD
# ============================================================

with st.sidebar:

    st.markdown(
        "### Filtros de análisis"
    )

    # AÑO

    anios = sorted(
        df["anio"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    filtro_anio = st.multiselect(
        "Año",
        options=anios,
        default=anios
    )

    # MES

    orden_meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre"
    ]

    meses_disponibles = [
        mes
        for mes in orden_meses
        if mes in df["mes"]
        .dropna()
        .unique()
    ]

    filtro_mes = st.multiselect(
        "Mes",
        options=meses_disponibles,
        default=meses_disponibles
    )

    # TIPO DE TANQUE

    tanques = sorted(
        df["tipo_tanque"]
        .astype(str)
        .unique()
        .tolist()
    )

    filtro_tanque = st.multiselect(
        "Tipo de tanque",
        options=tanques,
        default=tanques
    )

    st.divider()

    st.caption(
        f"Registros cargados: {len(df)}"
    )


# ============================================================
# 16. APLICAR FILTROS
# ============================================================

df_filtrado = df[
    (df["anio"].isin(filtro_anio))
    &
    (df["mes"].isin(filtro_mes))
    &
    (
        df["tipo_tanque"]
        .astype(str)
        .isin(filtro_tanque)
    )
].copy()


if df_filtrado.empty:

    st.warning(
        "No existen registros para "
        "los filtros seleccionados."
    )

    st.stop()


# ============================================================
# 17. ENCABEZADO DEL DASHBOARD
# ============================================================

titulo, estado = st.columns(
    [4, 1]
)

with titulo:

    st.title(
        "Dashboard de Productividad"
    )

    st.caption(
        "Monitoreo operativo · Diagnóstico DSS · "
        "Evaluación de escenarios"
    )

with estado:

    st.markdown(
        """
        <div style="
            background:#101820;
            border:1px solid #26313D;
            border-radius:10px;
            padding:12px;
            margin-top:7px;
            text-align:center;
            color:#B8C4D0;
            font-size:12px;
            letter-spacing:1px;
        ">
            ● SISTEMA ACTIVO
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()


# ============================================================
# 18. KPIs
# ============================================================

productividad = (
    df_filtrado[
        "unidades_producidas"
    ].sum()
    /
    df_filtrado[
        "horas_hombre"
    ].sum()
)

produccion = (
    df_filtrado[
        "unidades_producidas"
    ].sum()
)

horas_hombre = (
    df_filtrado[
        "horas_hombre"
    ].sum()
)

horas_extra = (
    df_filtrado[
        "horas_extra"
    ].sum()
)

paradas = (
    df_filtrado[
        "paradas_h"
    ].sum()
)

cumplimiento_5s = (
    df_filtrado[
        "checklist_5s_pct"
    ].mean()
)


k1, k2, k3, k4, k5, k6 = st.columns(6)


with k1:

    st.metric(
        "PRODUCTIVIDAD",
        f"{productividad:.3f}",
        help="Unidades producidas por hora-hombre"
    )


with k2:

    st.metric(
        "PRODUCCIÓN",
        f"{produccion:,.0f}"
    )


with k3:

    st.metric(
        "HORAS-HOMBRE",
        f"{horas_hombre:,.0f} h"
    )


with k4:

    st.metric(
        "HORAS EXTRA",
        f"{horas_extra:,.1f} h"
    )


with k5:

    st.metric(
        "PARADAS",
        f"{paradas:,.1f} h"
    )


with k6:

    st.metric(
        "5S",
        f"{cumplimiento_5s:.1f}%"
    )


st.write("")


# ============================================================
# 19. PESTAÑAS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "RESUMEN",
    "PÉRDIDAS OPERATIVAS",
    "DIAGNÓSTICO DSS",
    "SIMULACIÓN"
])


# ============================================================
# 20. TAB 1 - RESUMEN
# ============================================================

with tab1:

    st.subheader(
        "Resumen de productividad"
    )

    productividad_periodo = (
        df_filtrado
        .groupby(
            [
                "anio",
                "mes_num",
                "periodo"
            ],
            as_index=False
        )
        .agg({
            "unidades_producidas": "sum",
            "horas_hombre": "sum"
        })
    )

    productividad_periodo[
        "Productividad"
    ] = (
        productividad_periodo[
            "unidades_producidas"
        ]
        /
        productividad_periodo[
            "horas_hombre"
        ]
    )

    productividad_periodo = (
        productividad_periodo
        .sort_values(
            ["anio", "mes_num"]
        )
    )

    produccion_tanque = (
        df_filtrado
        .groupby(
            "tipo_tanque",
            as_index=False
        )["unidades_producidas"]
        .sum()
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "##### Evolución de productividad"
        )

        st.line_chart(
            productividad_periodo,
            x="periodo",
            y="Productividad",
            height=245
        )


    with c2:

        st.markdown(
            "##### Producción por tipo de tanque"
        )

        st.bar_chart(
            produccion_tanque,
            x="tipo_tanque",
            y="unidades_producidas",
            height=245
        )


    horas_periodo = (
        df_filtrado
        .groupby(
            "periodo",
            as_index=False
        )
        .agg({
            "horas_hombre": "sum",
            "horas_extra": "sum"
        })
    )


    c3, c4 = st.columns(2)


    with c3:

        st.markdown(
            "##### Horas-hombre por periodo"
        )

        st.bar_chart(
            horas_periodo,
            x="periodo",
            y="horas_hombre",
            height=225
        )


    with c4:

        st.markdown(
            "##### Horas extra por periodo"
        )

        st.bar_chart(
            horas_periodo,
            x="periodo",
            y="horas_extra",
            height=225
        )


# ============================================================
# 21. TAB 2 - PÉRDIDAS OPERATIVAS
# ============================================================

with tab2:

    st.subheader(
        "Análisis de pérdidas operativas"
    )

    perdidas = (
        df_filtrado
        .groupby(
            "periodo",
            as_index=False
        )
        .agg({
            "tiempo_busqueda_min": "sum",
            "recorrido_m": "sum",
            "paradas_h": "sum",
            "numero_fallas": "sum",
            "checklist_5s_pct": "mean"
        })
    )


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "##### Tiempo de búsqueda"
        )

        st.bar_chart(
            perdidas,
            x="periodo",
            y="tiempo_busqueda_min",
            height=225
        )


    with c2:

        st.markdown(
            "##### Recorridos"
        )

        st.bar_chart(
            perdidas,
            x="periodo",
            y="recorrido_m",
            height=225
        )


    c3, c4 = st.columns(2)


    with c3:

        st.markdown(
            "##### Horas de parada"
        )

        st.line_chart(
            perdidas,
            x="periodo",
            y="paradas_h",
            height=225
        )


    with c4:

        st.markdown(
            "##### Número de fallas"
        )

        st.bar_chart(
            perdidas,
            x="periodo",
            y="numero_fallas",
            height=225
        )


    st.markdown(
        "##### Cumplimiento 5S"
    )

    st.line_chart(
        perdidas,
        x="periodo",
        y="checklist_5s_pct",
        height=210
    )


# ============================================================
# 22. TAB 3 - DIAGNÓSTICO DSS
# ============================================================

with tab3:

    st.subheader(
        "Diagnóstico del Sistema de Soporte a Decisiones"
    )

    prioridad, scores, recomendacion = (
        diagnostico_dss(
            df_filtrado
        )
    )


    c1, c2 = st.columns(
        [1, 2]
    )


    with c1:

        st.markdown(
            "##### Prioridad identificada"
        )

        st.markdown(
            f"""
            <div style="
                background:
                    linear-gradient(
                        145deg,
                        #151C26,
                        #10151D
                    );
                border:1px solid #344153;
                border-radius:12px;
                padding:24px;
                text-align:center;
                margin-top:10px;
            ">

                <div style="
                    color:#8B98A9;
                    font-size:11px;
                    letter-spacing:1.5px;
                ">
                    PRIORIDAD DSS
                </div>

                <div style="
                    color:#FFFFFF;
                    font-size:38px;
                    font-weight:700;
                    margin-top:6px;
                ">
                    {prioridad}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with c2:

        st.markdown(
            "##### Acción recomendada"
        )

        st.info(
            recomendacion
        )


    st.write("")


    diagnostico_df = pd.DataFrame({
        "Herramienta":
            list(scores.keys()),

        "Nivel de prioridad":
            list(scores.values())
    })


    st.markdown(
        "##### Comparación de prioridades"
    )

    st.bar_chart(
        diagnostico_df,
        x="Herramienta",
        y="Nivel de prioridad",
        height=245
    )

    st.caption(
        "Los indicadores son transformados a una "
        "escala común para apoyar la comparación "
        "entre 5S, SLP y TPM."
    )


# ============================================================
# 23. TAB 4 - SIMULACIÓN
# ============================================================

with tab4:

    st.subheader(
        "Simulación de escenario de mejora"
    )

    st.caption(
        "Modifica los parámetros para evaluar "
        "un posible escenario propuesto."
    )


    s1, s2, s3, s4 = st.columns(4)


    with s1:

        reduccion_busqueda = st.slider(
            "Reducción búsqueda",
            min_value=0,
            max_value=50,
            value=20,
            step=5,
            format="%d%%"
        )


    with s2:

        reduccion_recorrido = st.slider(
            "Reducción recorridos",
            min_value=0,
            max_value=50,
            value=20,
            step=5,
            format="%d%%"
        )


    with s3:

        reduccion_paradas = st.slider(
            "Reducción paradas",
            min_value=0,
            max_value=50,
            value=15,
            step=5,
            format="%d%%"
        )


    with s4:

        mejora_5s = st.slider(
            "Mejora 5S",
            min_value=0,
            max_value=30,
            value=10,
            step=5,
            format="%d p.p."
        )


    escenario = simular_escenario(
        df_filtrado,
        reduccion_busqueda,
        reduccion_recorrido,
        reduccion_paradas,
        mejora_5s
    )


    productividad_actual = (
        escenario[
            "unidades_producidas"
        ].sum()
        /
        escenario[
            "horas_hombre"
        ].sum()
    )


    productividad_propuesta = (
        escenario[
            "unidades_producidas"
        ].sum()
        /
        escenario[
            "horas_hombre_escenario"
        ].sum()
    )


    mejora_productividad = (
        (
            productividad_propuesta
            -
            productividad_actual
        )
        /
        productividad_actual
    ) * 100


    horas_recuperadas = (
        escenario[
            "horas_potencialmente_recuperadas"
        ].sum()
    )


    k1, k2, k3 = st.columns(3)


    with k1:

        st.metric(
            "PRODUCTIVIDAD ACTUAL",
            f"{productividad_actual:.3f}"
        )


    with k2:

        st.metric(
            "PRODUCTIVIDAD PROPUESTA",
            f"{productividad_propuesta:.3f}",
            delta=f"{mejora_productividad:.1f}%"
        )


    with k3:

        st.metric(
            "HORAS POTENCIALMENTE RECUPERADAS",
            f"{horas_recuperadas:.1f} h"
        )


    st.write("")


    comparacion_productividad = pd.DataFrame({
        "Escenario": [
            "Actual",
            "Propuesto"
        ],

        "Productividad": [
            productividad_actual,
            productividad_propuesta
        ]
    })


    comparacion_perdidas = pd.DataFrame({
        "Indicador": [
            "Búsqueda (min)",
            "Recorrido (m)",
            "Paradas (h)"
        ],

        "Actual": [
            escenario[
                "tiempo_busqueda_min"
            ].sum(),

            escenario[
                "recorrido_m"
            ].sum(),

            escenario[
                "paradas_h"
            ].sum()
        ],

        "Propuesto": [
            escenario[
                "busqueda_propuesta_min"
            ].sum(),

            escenario[
                "recorrido_propuesto_m"
            ].sum(),

            escenario[
                "paradas_propuesta_h"
            ].sum()
        ]
    })


    c1, c2 = st.columns(2)


    with c1:

        st.markdown(
            "##### Productividad actual vs. propuesta"
        )

        st.bar_chart(
            comparacion_productividad,
            x="Escenario",
            y="Productividad",
            height=245
        )


    with c2:

        st.markdown(
            "##### Comparación de pérdidas"
        )

        st.dataframe(
            comparacion_perdidas,
            width="stretch",
            hide_index=True
        )


    st.warning(
        "Los resultados del escenario propuesto "
        "corresponden a una simulación para apoyar "
        "la toma de decisiones. No representan "
        "resultados reales hasta que las mejoras "
        "sean implementadas y medidas."
    )


# ============================================================
# 24. DETALLE DE LA BASE
# ============================================================

st.divider()


with st.expander(
    "Ver detalle de la base analizada"
):

    columnas_mostrar = [
        "periodo",
        "tipo_tanque",
        "horas_hombre",
        "unidades_producidas",
        "horas_extra",
        "tiempo_busqueda_min",
        "recorrido_m",
        "paradas_h",
        "numero_fallas",
        "checklist_5s_pct",
        "productividad_unid_hh"
    ]


    st.dataframe(
        df_filtrado[
            columnas_mostrar
        ],
        width="stretch",
        hide_index=True
    )


# ============================================================
# 25. PIE DE PÁGINA
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#657184;
        font-size:12px;
        padding-top:15px;
        padding-bottom:5px;
    ">
        DSS · Productividad de Mano de Obra ·
        Ingeniería Industrial
    </div>
    """,
    unsafe_allow_html=True
)
