"""
CMRPI - EMC Helpline | Projet N°10 - Tableau de bord décisionnel
Jalon 3 (16 - 31 août 2026) : Assemblage du tableau de bord interactif Streamlit

Auteure : NAFID IKRAM
Encadrante : Mme Rachida Margdane

Cette application :
  1. Réutilise TELLES QUELLES les fonctions de nettoyage et de calcul des
     5 KPI écrites au Jalon 2 (import depuis kpi_dashboard.py) — aucune
     logique de calcul n'est dupliquée ni réécrite ici.
  2. Ajoute 2 filtres simples : par période (mois) et par plateforme.
  3. Assemble les 7 graphiques Plotly du Jalon 2 dans une page unique,
     avec une identité visuelle propre (couleurs, typographie, cartes).

Lancement : streamlit run app.py
"""

import streamlit as st
import pandas as pd

from kpi_dashboard import (
    FICHIER_SOURCE,
    charger_donnees,
    nettoyer_donnees,
    kpi1_volume_par_mois,
    kpi2_repartition_type,
    kpi3_repartition_plateforme,
    kpi4_taux_accompagnement,
    kpi5_profil_victimes,
    graphique_kpi1,
    graphique_kpi2,
    graphique_kpi3,
    graphique_kpi4,
    graphique_kpi4_detail,
    graphique_kpi5,
)

# ---------------------------------------------------------------------------
# IDENTITÉ VISUELLE — tokens de design
# ---------------------------------------------------------------------------

NAVY = "#0f2942"       # couleur principale (confiance, institutionnel)
TEAL = "#0d9488"       # accent (action, sécurité)
INDIGO = "#4f46e5"     # accent secondaire
AMBER = "#d97706"      # alerte / mise en avant
CORAL = "#e11d48"      # alerte forte, usage rare
SLATE_BG = "#f4f6f9"   # fond de page
CARD_BG = "#ffffff"
BORDER = "#e2e8f0"
TEXT_MUTED = "#64748b"

PALETTE_GRAPHIQUES = [NAVY, TEAL, INDIGO, AMBER, "#0891b2", "#7c3aed", "#059669", CORAL]

POLICE_TITRE = "Manrope"
POLICE_TEXTE = "Inter"


# ---------------------------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="EMC Helpline — Tableau de bord",
    page_icon="🛡️",
    layout="wide",
)


def injecter_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: '{POLICE_TEXTE}', sans-serif;
    }}

    #MainMenu, footer {{visibility: hidden;}}

    .stApp {{
        background-color: {SLATE_BG};
    }}

    /* Bandeau supérieur */
    .bandeau {{
        background: linear-gradient(90deg, {NAVY} 0%, #163a5c 100%);
        margin: -1rem -1rem 1.5rem -1rem;
        padding: 1.6rem 2.2rem;
        border-radius: 0 0 14px 14px;
        box-shadow: 0 4px 18px rgba(15, 41, 66, 0.18);
    }}
    .bandeau h1 {{
        font-family: '{POLICE_TITRE}', sans-serif;
        color: #ffffff;
        font-weight: 800;
        font-size: 1.9rem;
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .bandeau p {{
        color: #b9c8d8;
        font-size: 0.92rem;
        margin: 0.35rem 0 0 0;
    }}
    .bandeau-icone {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 46px;
        height: 46px;
        background: {TEAL};
        border-radius: 12px;
        font-size: 1.4rem;
        margin-right: 0.8rem;
    }}

    /* Titres de section (h2/h3 Streamlit) */
    h2, h3 {{
        font-family: '{POLICE_TITRE}', sans-serif !important;
        color: {NAVY} !important;
        font-weight: 700 !important;
    }}

    /* Barre latérale */
    section[data-testid="stSidebar"] {{
        background-color: {NAVY};
    }}
    section[data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}
    section[data-testid="stSidebar"] h2 {{
        color: #ffffff !important;
        font-family: '{POLICE_TITRE}', sans-serif !important;
    }}
    section[data-testid="stSidebar"] .stCaption {{
        color: #93a5b8 !important;
    }}

    /* Cartes d'indicateurs-clés */
    .carte-kpi {{
        background: {CARD_BG};
        border-radius: 12px;
        padding: 1.1rem 1.3rem;
        border: 1px solid {BORDER};
        border-left: 4px solid var(--accent-carte, {TEAL});
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
        height: 100%;
    }}
    .carte-kpi .carte-label {{
        font-size: 0.78rem;
        color: {TEXT_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.04em;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }}
    .carte-kpi .carte-valeur {{
        font-family: '{POLICE_TITRE}', sans-serif;
        font-size: 1.9rem;
        font-weight: 800;
        color: {NAVY};
        line-height: 1.1;
    }}
    .carte-kpi .carte-detail {{
        font-size: 0.8rem;
        color: {TEXT_MUTED};
        margin-top: 0.25rem;
    }}

    /* Conteneur de graphique (carte blanche) */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {CARD_BG};
        border-radius: 12px;
        border: 1px solid {BORDER};
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }}

    /* Onglets */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: #eef1f6;
        padding: 5px;
        border-radius: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        font-family: '{POLICE_TEXTE}', sans-serif;
        font-weight: 600;
        color: {TEXT_MUTED};
        padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {NAVY} !important;
        color: #ffffff !important;
    }}

    /* Légendes sous les graphiques */
    .legende-graphique {{
        font-size: 0.85rem;
        color: {TEXT_MUTED};
        background: #f8fafc;
        border-left: 3px solid {TEAL};
        padding: 0.5rem 0.8rem;
        border-radius: 0 6px 6px 0;
        margin-top: -0.3rem;
    }}
    </style>
    """, unsafe_allow_html=True)


injecter_css()


def carte_kpi(label, valeur, detail="", accent=TEAL):
    st.markdown(f"""
    <div class="carte-kpi" style="--accent-carte: {accent};">
        <div class="carte-label">{label}</div>
        <div class="carte-valeur">{valeur}</div>
        <div class="carte-detail">{detail}</div>
    </div>
    """, unsafe_allow_html=True)


def theme_graphique(fig, couleurs=None):
    """Applique l'identité visuelle du tableau de bord à un graphique Plotly
    généré par kpi_dashboard.py, sans modifier les données ni les calculs."""
    fig.update_layout(
        font_family=POLICE_TEXTE,
        title_font_family=POLICE_TITRE,
        title_font_size=17,
        title_font_color=NAVY,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, l=10, r=10, b=10),
    )
    fig.update_xaxes(gridcolor="#eef1f6", linecolor=BORDER)
    fig.update_yaxes(gridcolor="#eef1f6", linecolor=BORDER)
    if couleurs:
        try:
            fig.update_traces(marker_color=couleurs)
        except Exception:
            pass
    return fig


def legende(texte):
    st.markdown(f'<div class="legende-graphique">{texte}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# CHARGEMENT ET NETTOYAGE (mis en cache pour ne pas recharger à chaque clic)
# ---------------------------------------------------------------------------

@st.cache_data
def charger_et_nettoyer(chemin: str) -> pd.DataFrame:
    df = charger_donnees(chemin)
    df = nettoyer_donnees(df)
    return df


df = charger_et_nettoyer(FICHIER_SOURCE)


# ---------------------------------------------------------------------------
# EN-TÊTE
# ---------------------------------------------------------------------------

st.markdown("""
<div class="bandeau">
    <div style="display:flex; align-items:center;">
        <div class="bandeau-icone">🛡️</div>
        <div>
            <h1>Tableau de bord décisionnel — EMC Helpline</h1>
            <p>CMRPI · Espace Maroc Cyberconfiance · Stage PFA 2026 · Projet N°10 · Stagiaire : NAFID IKRAM</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# BARRE LATÉRALE — FILTRES
# ---------------------------------------------------------------------------

st.sidebar.markdown("## 🔎 Filtres")

# --- Filtre 1 : par période (mois) ---
mois_disponibles = (
    df["date"].dt.to_period("M").dt.to_timestamp().sort_values().unique()
)
labels_mois = [pd.Timestamp(m).strftime("%b %Y") for m in mois_disponibles]
mois_debut_label, mois_fin_label = st.sidebar.select_slider(
    "Période (par mois)",
    options=labels_mois,
    value=(labels_mois[0], labels_mois[-1]),
)
idx_debut = labels_mois.index(mois_debut_label)
idx_fin = labels_mois.index(mois_fin_label)
mois_debut = pd.Timestamp(mois_disponibles[idx_debut])
mois_fin = pd.Timestamp(mois_disponibles[idx_fin]) + pd.offsets.MonthEnd(0)

# --- Filtre 2 : par plateforme ---
plateformes_disponibles = sorted(df["plateforme"].dropna().unique())
plateformes_choisies = st.sidebar.multiselect(
    "Plateforme(s)",
    options=plateformes_disponibles,
    default=plateformes_disponibles,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Astuce : réduis la période ou sélectionne une seule plateforme pour "
    "affiner l'analyse. Les indicateurs et graphiques se recalculent "
    "automatiquement."
)

# --- Application des filtres ---
df_filtre = df[
    (df["date"] >= mois_debut)
    & (df["date"] <= mois_fin)
    & (df["plateforme"].isin(plateformes_choisies))
]

if df_filtre.empty:
    st.warning(
        "Aucun signalement ne correspond aux filtres sélectionnés. "
        "Élargis la période ou les plateformes dans la barre latérale."
    )
    st.stop()


# ---------------------------------------------------------------------------
# INDICATEURS-CLÉS (cartes en en-tête)
# ---------------------------------------------------------------------------

kpi4_f = kpi4_taux_accompagnement(df_filtre)
kpi1_f = kpi1_volume_par_mois(df_filtre)
mois_pic = kpi1_f.loc[kpi1_f["nombre_signalements"].idxmax()]

col1, col2, col3, col4 = st.columns(4)
with col1:
    carte_kpi("Signalements (période filtrée)", f"{len(df_filtre)}", accent=NAVY)
with col2:
    carte_kpi("Taux d'accompagnement", f"{kpi4_f['taux_global']}%", accent=TEAL)
with col3:
    carte_kpi(
        "Mois le plus actif",
        pd.Timestamp(mois_pic["mois"]).strftime("%b %Y"),
        f"{int(mois_pic['nombre_signalements'])} signalements",
        accent=AMBER,
    )
with col4:
    carte_kpi("Plateformes sélectionnées", f"{len(plateformes_choisies)}", accent=INDIGO)

st.write("")
st.write("")


# ---------------------------------------------------------------------------
# ONGLETS — LES 7 GRAPHIQUES DU JALON 2
# ---------------------------------------------------------------------------

onglet1, onglet2, onglet3, onglet4 = st.tabs([
    "📈  Volume & Types",
    "📱  Plateformes",
    "🤝  Accompagnement",
    "👥  Profil des victimes",
])

with onglet1:
    with st.container(border=True):
        kpi1 = kpi1_volume_par_mois(df_filtre)
        fig1 = theme_graphique(graphique_kpi1(kpi1))
        fig1.update_traces(line_color=NAVY, marker_color=NAVY)
        st.plotly_chart(fig1, width="stretch")
        if (kpi1["nombre_signalements"] == 0).any():
            legende(
                "⚠️ Un ou plusieurs mois de la période sélectionnée ne comportent "
                "aucun signalement dans le fichier fourni."
            )

    st.write("")
    with st.container(border=True):
        kpi2 = kpi2_repartition_type(df_filtre)
        fig2 = theme_graphique(graphique_kpi2(kpi2), couleurs=PALETTE_GRAPHIQUES)
        st.plotly_chart(fig2, width="stretch")
        type_principal = kpi2.iloc[0]
        legende(
            f"Type le plus fréquent sur la période : "
            f"<strong>{type_principal['cyberharcelementType']}</strong> "
            f"({type_principal['pourcentage']}%)."
        )

with onglet2:
    with st.container(border=True):
        kpi3 = kpi3_repartition_plateforme(df_filtre)
        fig3 = theme_graphique(graphique_kpi3(kpi3), couleurs=PALETTE_GRAPHIQUES)
        st.plotly_chart(fig3, width="stretch")
        plateforme_principale = kpi3.iloc[0]
        legende(
            f"Plateforme la plus représentée : "
            f"<strong>{plateforme_principale['plateforme']}</strong> "
            f"({plateforme_principale['pourcentage']}%)."
        )

with onglet3:
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            fig4 = theme_graphique(graphique_kpi4(kpi4_f))
            fig4.update_traces(gauge_bar_color=TEAL)
            st.plotly_chart(fig4, width="stretch")
    with c2:
        with st.container(border=True):
            if kpi4_f["nb_oui"] > 0:
                fig4d = theme_graphique(graphique_kpi4_detail(kpi4_f))
                fig4d.update_traces(marker_color=INDIGO)
                st.plotly_chart(fig4d, width="stretch")
            else:
                st.info("Aucune demande d'accompagnement sur la période sélectionnée.")

with onglet4:
    kpi5 = kpi5_profil_victimes(df_filtre)
    fig_genre, fig_age = graphique_kpi5(kpi5)
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            if not kpi5["genre"].empty:
                fig_genre = theme_graphique(fig_genre, couleurs=[NAVY, AMBER])
                st.plotly_chart(fig_genre, width="stretch")
            else:
                st.info("Aucune donnée de genre renseignée sur la période sélectionnée.")
    with c2:
        with st.container(border=True):
            if not kpi5["age"].empty:
                fig_age = theme_graphique(fig_age)
                fig_age.update_traces(marker_color=TEAL)
                st.plotly_chart(fig_age, width="stretch")
            else:
                st.info("Aucune donnée d'âge renseignée sur la période sélectionnée.")


# ---------------------------------------------------------------------------
# PIED DE PAGE
# ---------------------------------------------------------------------------

st.write("")
st.markdown(f"""
<div style="text-align:center; color:{TEXT_MUTED}; font-size:0.82rem; padding: 1rem 0;
            border-top: 1px solid {BORDER}; margin-top: 1rem;">
    Données issues de signalements-_1_.xlsx · {len(df)} signalements au total
    ({len(df_filtre)} affichés selon les filtres actifs) ·
    Tableau de bord réalisé avec Python, pandas, Plotly et Streamlit.
</div>
""", unsafe_allow_html=True)
s