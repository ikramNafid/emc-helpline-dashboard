"""
CMRPI - EMC Helpline | Projet N°10
Tableau de bord décisionnel et analytique des signalements

Version Finale - Design Executive, responsive, interactif
- filtres période + plateforme
- réinitialisation des filtres
- comparaison entre deux périodes
- variation en %
- Top 5 des types de cyberharcèlement
- analyse croisée plateforme × type
- analyse détaillée de l'accompagnement
- détection automatique des pics
- section "À retenir"
- export CSV des données filtrées
- page Documentation

Améliorations : design Executive, cartes « À retenir » individuelles, hiérarchie visuelle renforcée, responsive.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

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


# =============================================================================
# CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="EMC Helpline — Tableau de bord",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# IDENTITÉ VISUELLE (palette modernisée)
# =============================================================================

NAVY = "#0f2942"
NAVY_LIGHT = "#1e3a5f"
NAVY_DARK = "#091b2e"

TEAL = "#0d9488"
TEAL_LIGHT = "#14b8a6"
TEAL_DARK = "#0f766e"

INDIGO = "#4f46e5"
AMBER = "#d97706"
CORAL = "#e11d48"

SLATE_BG = "#f8fafc"
CARD_BG = "#ffffff"
BORDER = "#e2e8f0"
SHADOW = "0 8px 26px rgba(15, 23, 42, 0.08)"

TEXT = "#1e293b"
TEXT_MUTED = "#64748b"
TEXT_LIGHT = "#94a3b8"

PALETTE_GRAPHIQUES = [NAVY, TEAL, INDIGO, AMBER, "#0891b2", "#7c3aed", "#059669", CORAL]

POLICE_TITRE = "Manrope"
POLICE_TEXTE = "Inter"


# =============================================================================
# CSS GLOBAL (design amélioré)
# =============================================================================

def injecter_css():
    st.html(
        f"""
        <style>

        /* =========================================================
           POLICES
        ========================================================= */

        @import url(
            'https://fonts.googleapis.com/css2?family=Manrope:wght@600;700;800&family=Inter:wght@400;500;600;700&display=swap'
        );

        html, body, [class*="css"] {{
            font-family: '{POLICE_TEXTE}', sans-serif;
        }}

        .stApp {{
            background: {SLATE_BG};
        }}

        #MainMenu, footer {{
            visibility: hidden;
        }}


        /* =========================================================
           SIDEBAR — DESIGN PREMIUM
        ========================================================= */

        section[data-testid="stSidebar"] {{
            background:
                radial-gradient(circle at 12% 6%, rgba(20,184,166,0.12), transparent 28%),
                linear-gradient(180deg, #0b2238 0%, #0f2942 48%, #0a2136 100%);
            border-right: 1px solid rgba(255,255,255,0.07);
            box-shadow: 8px 0 30px rgba(9,27,46,0.10);
            min-width: 286px;
            max-width: 286px;
        }}

        section[data-testid="stSidebar"] > div {{
            padding: 1.1rem 0.95rem 0.9rem;
        }}

        section[data-testid="stSidebar"] * {{
            font-family: '{POLICE_TEXTE}', sans-serif;
        }}

        /* --- identité --- */
        .side-brand {{
            position: relative;
            padding: 14px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 16px;
            background: linear-gradient(145deg, rgba(255,255,255,0.075), rgba(255,255,255,0.025));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
            overflow: hidden;
        }}

        .side-brand::after {{
            content: "";
            position: absolute;
            width: 105px;
            height: 105px;
            right: -48px;
            top: -50px;
            border-radius: 50%;
            background: rgba(20,184,166,0.10);
        }}

        .side-brand-row {{
            display: flex;
            align-items: center;
            gap: 11px;
            position: relative;
            z-index: 1;
        }}

        .side-brand-icon {{
            width: 42px;
            height: 42px;
            min-width: 42px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: linear-gradient(145deg, #14b8a6, #0d9488);
            box-shadow: 0 7px 18px rgba(13,148,136,0.28);
            font-size: 21px;
        }}

        .side-brand-title {{
            color: #ffffff;
            font-family: '{POLICE_TITRE}', sans-serif;
            font-size: 17px;
            font-weight: 800;
            line-height: 1.15;
        }}

        .side-brand-sub {{
            color: #aebed0;
            font-size: 10px;
            margin-top: 4px;
            line-height: 1.3;
        }}

        .side-project {{
            display: inline-flex;
            margin-top: 12px;
            padding: 5px 8px;
            border-radius: 7px;
            background: rgba(255,255,255,0.055);
            color: #c8d5e2;
            font-size: 9px;
            font-weight: 700;
            letter-spacing: 0.04em;
        }}

        .side-divider {{
            height: 1px;
            background: linear-gradient(90deg, rgba(255,255,255,0.11), rgba(255,255,255,0.02));
            margin: 14px 2px;
        }}

        /* --- sections --- */
        .side-section-title {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #d9e4ef;
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.10em;
            margin: 15px 2px 7px;
        }}

        .side-section-icon {{
            width: 23px;
            height: 23px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 7px;
            background: rgba(20,184,166,0.11);
            border: 1px solid rgba(20,184,166,0.14);
            font-size: 11px;
        }}

        /* --- période --- */
        section[data-testid="stSidebar"] [data-testid="stSlider"] {{
            padding: 3px 4px 2px;
        }}

        section[data-testid="stSidebar"] [data-testid="stSlider"] label {{
            display: none;
        }}

        section[data-testid="stSidebar"] [data-baseweb="slider"] {{
            margin: 0 2px;
        }}

        section[data-testid="stSidebar"] [data-testid="stTickBarMin"],
        section[data-testid="stSidebar"] [data-testid="stTickBarMax"] {{
            color: #9fb0c2 !important;
            font-size: 9px !important;
        }}

        /* --- plateformes --- */
        section[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div {{
            background: rgba(255,255,255,0.055) !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
            border-radius: 11px !important;
            min-height: 46px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"] {{
            background: transparent !important;
        }}

        section[data-testid="stSidebar"] [data-baseweb="tag"] {{
            background: #178f86 !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
            border-radius: 6px !important;
            color: white !important;
            font-size: 10px !important;
            font-weight: 600 !important;
        }}

        section[data-testid="stSidebar"] [data-baseweb="tag"] span {{
            color: white !important;
        }}

        section[data-testid="stSidebar"] [data-baseweb="select"] input {{
            color: #dbe7f2 !important;
        }}

        /* --- bouton --- */
        section[data-testid="stSidebar"] .stButton {{
            margin-top: 11px;
        }}

        section[data-testid="stSidebar"] .stButton button {{
            width: 100%;
            min-height: 38px;
            background: linear-gradient(135deg, #14b8a6, #0d9488);
            color: white !important;
            font-size: 11px;
            font-weight: 700;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 10px;
            box-shadow: 0 7px 16px rgba(13,148,136,0.18);
            transition: transform .18s ease, box-shadow .18s ease;
        }}

        section[data-testid="stSidebar"] .stButton button:hover {{
            transform: translateY(-1px);
            box-shadow: 0 9px 20px rgba(13,148,136,0.25);
        }}

        /* --- statut --- */
        .side-status {{
            margin-top: 4px;
            padding: 11px 12px;
            border: 1px solid rgba(255,255,255,0.075);
            border-radius: 12px;
            background: rgba(255,255,255,0.045);
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .side-status-icon {{
            width: 31px;
            height: 31px;
            min-width: 31px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 9px;
            background: rgba(20,184,166,0.12);
            font-size: 15px;
        }}

        .side-status-label {{
            color: #91a7bb;
            font-size: 9px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .07em;
        }}

        .side-status-value {{
            color: white;
            font-family: '{POLICE_TITRE}', sans-serif;
            font-size: 19px;
            font-weight: 800;
            line-height: 1.1;
            margin-top: 2px;
        }}

        .side-help {{
            color: #8fa5b9;
            font-size: 9px;
            line-height: 1.45;
            margin: 7px 2px 0;
        }}

        /* --- export --- */
        section[data-testid="stSidebar"] .stDownloadButton {{
            margin-top: 10px;
        }}

        section[data-testid="stSidebar"] .stDownloadButton button {{
            width: 100%;
            min-height: 36px;
            background: rgba(255,255,255,0.055) !important;
            color: #d4dfeb !important;
            border: 1px solid rgba(255,255,255,0.09) !important;
            border-radius: 10px !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            transition: all .18s ease;
        }}

        section[data-testid="stSidebar"] .stDownloadButton button:hover {{
            background: rgba(255,255,255,0.09) !important;
            border-color: rgba(20,184,166,0.35) !important;
        }}

        section[data-testid="stSidebar"] .stCaption {{
            color: #8fa5b9 !important;
            font-size: 9px !important;
            line-height: 1.45;
        }}

        section[data-testid="stSidebar"] [data-testid="stAlert"] {{
            background: rgba(245,158,11,0.09) !important;
            border: 1px solid rgba(245,158,11,0.18) !important;
            border-radius: 9px !important;
        }}

        .side-footer {{
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid rgba(255,255,255,0.06);
            text-align: center;
            color: #6f879c;
            font-size: 8px;
            letter-spacing: .04em;
        }}

        /* =========================================================
           TITRES GLOBAUX
        ========================================================= */

        h1, h2, h3 {{
            font-family: '{POLICE_TITRE}', sans-serif !important;
            color: {NAVY} !important;
        }}


        /* =========================================================
           BANDEAU (en-tête)
        ========================================================= */

        .bandeau {{
            width: 100%;
            background: linear-gradient(135deg, {NAVY} 0%, {NAVY_LIGHT} 100%);
            padding: 20px 30px;
            border-radius: 0 0 20px 20px;
            box-shadow: 0 8px 30px rgba(15, 41, 66, 0.2);
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }}
        .bandeau::after {{
            content: "";
            position: absolute;
            top: -60%;
            right: -5%;
            width: 250px;
            height: 250px;
            background: rgba(13, 148, 136, 0.06);
            border-radius: 50%;
            pointer-events: none;
        }}
        .bandeau-contenu {{
            display: flex;
            align-items: center;
            gap: 18px;
            position: relative;
            z-index: 2;
        }}
        .bandeau-icone {{
            width: 56px;
            height: 56px;
            min-width: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: {TEAL};
            border-radius: 14px;
            font-size: 28px;
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.3);
        }}
        .bandeau-titre {{
            color: white;
            font-family: '{POLICE_TITRE}', sans-serif;
            font-size: 24px;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 2px;
        }}
        .bandeau-sous-titre {{
            color: #b9c8d8;
            font-size: 13px;
            font-weight: 500;
            line-height: 1.4;
        }}


        /* =========================================================
           KPI CARDS (modernisées)
        ========================================================= */

        .kpi-card {{
            background: {CARD_BG};
            border: none;
            border-radius: 16px;
            padding: 20px 22px;
            min-height: 120px;
            box-shadow: {SHADOW};
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            display: flex;
            flex-direction: column;
        }}
        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
        }}
        .kpi-card::before {{
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            background: var(--accent);
            border-radius: 0 4px 4px 0;
        }}
        .kpi-top {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }}
        .kpi-icon {{
            font-size: 24px;
            opacity: 0.8;
        }}
        .carte-label {{
            color: {TEXT_MUTED};
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        .carte-valeur {{
            color: {NAVY};
            font-family: '{POLICE_TITRE}', sans-serif;
            font-size: 30px;
            font-weight: 800;
            line-height: 1.15;
            margin-top: 2px;
        }}
        .carte-detail {{
            color: {TEXT_MUTED};
            font-size: 13px;
            font-weight: 500;
            margin-top: 4px;
        }}


        /* =========================================================
           SECTION « À RETENIR » — DESIGN PREMIUM / EXECUTIVE
        ========================================================= */

        .retient-header {{
            display: flex;
            align-items: center;
            gap: 13px;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-left: 2px;
        }}
        .retient-icon {{
            width: 38px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(145deg, #fffaf0, #fff6df);
            border: 1px solid #f0dfbd;
            border-radius: 10px;
            font-size: 18px;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
        }}
        .retient-title {{
            color: {NAVY};
            font-family: '{POLICE_TITRE}', sans-serif;
            font-size: 21px;
            font-weight: 800;
            line-height: 1.15;
            letter-spacing: -0.01em;
        }}
        .retient-subtitle {{
            color: {TEXT_MUTED};
            font-size: 12px;
            margin-top: 3px;
            font-weight: 500;
        }}

        /* Cartes « À retenir » — version Executive
           Les 7 cartes restent indépendantes et conservent leur identité. */
        .insight-panel {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
            align-items: stretch;
        }}

        .insight-item {{
            --accent: {NAVY};
            position: relative;
            min-height: 108px;
            padding: 16px 17px 15px 18px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
            border: 1px solid #e3e9ef;
            border-radius: 11px;
            box-shadow: 0 2px 8px rgba(15,23,42,.045);
            overflow: hidden;
            transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
        }}
        .insight-item::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: var(--accent);
        }}
        .insight-item::after {{
            content: '';
            position: absolute;
            width: 80px; height: 80px;
            right: -42px; bottom: -42px;
            border-radius: 50%;
            background: var(--accent);
            opacity: .035;
            pointer-events: none;
        }}
        .insight-item:hover {{
            transform: translateY(-2px);
            border-color: color-mix(in srgb, var(--accent) 24%, #e3e9ef);
            box-shadow: 0 7px 20px rgba(15,23,42,.075);
        }}

        .insight-top {{
            display: flex;
            align-items: center;
            gap: 9px;
            margin-bottom: 10px;
        }}
        .insight-icon {{
            width: 30px; height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            font-size: 14px;
            flex: 0 0 30px;
            border: 1px solid rgba(15,23,42,.035);
        }}
        .insight-label {{
            color: #64748b;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: .075em;
            font-weight: 800;
            line-height: 1.25;
        }}
        .insight-text {{
            color: #475569;
            font-size: 12px;
            line-height: 1.45;
            padding-left: 1px;
            max-width: 96%;
        }}
        .insight-text strong {{
            display: inline-block;
            color: {NAVY};
            font-family: '{POLICE_TITRE}', sans-serif;
            font-size: 15px;
            font-weight: 800;
            line-height: 1.2;
            margin-right: 2px;
        }}

        /* Les cartes profil reprennent exactement le même langage visuel. */
        .insight-profile {{
            --accent: {NAVY_LIGHT};
            position: relative;
            min-height: 108px;
            padding: 16px 17px 15px 18px;
            background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
            border: 1px solid #e3e9ef;
            border-radius: 11px;
            box-shadow: 0 2px 8px rgba(15,23,42,.045);
            overflow: hidden;
        }}
        .insight-profile::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, {NAVY_LIGHT}, {AMBER});
        }}
        .insight-profile .insight-top {{ margin-bottom: 10px; }}
        .profil-synthese {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 7px;
        }}
        .profil-mini {{
            background: #f8fafc;
            border: 1px solid #e7edf3;
            border-left: 3px solid var(--mini-accent);
            border-radius: 7px;
            padding: 6px 9px;
        }}
        .profil-mini-label {{
            color: #7a8796;
            font-size: 7.5px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .06em;
            margin-bottom: 1px;
        }}
        .profil-mini-value {{
            color: {NAVY};
            font-size: 11px;
            font-weight: 800;
            line-height: 1.2;
        }}
        .profil-mini-detail {{
            color: #64748b;
            font-size: 8.5px;
            margin-top: 1px;
        }}

        @media (max-width: 1150px) {{
            .insight-panel {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        }}
        @media (max-width: 800px) {{
            .insight-panel {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
        }}
        @media (max-width: 560px) {{
            .insight-panel {{ grid-template-columns: 1fr; gap: 10px; }}
        }}

        /* =========================================================
           GRAPHIQUES - LÉGENDE
        ========================================================= */

        .legende-graphique {{
            font-size: 13px;
            color: {TEXT_MUTED};
            background: #f1f5f9;
            border-left: 4px solid {TEAL};
            padding: 8px 14px;
            border-radius: 0 8px 8px 0;
            margin-top: -10px;
        }}


        /* =========================================================
           ALERTE PIC
        ========================================================= */

        .alerte-pic {{
            background: #fff7ed;
            border: 1px solid #fed7aa;
            border-left: 5px solid {AMBER};
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 10px;
            color: #9a3412;
            font-size: 14px;
        }}


        /* =========================================================
           DOCUMENTATION
        ========================================================= */

        .doc-card {{
            background: white;
            border: none;
            border-radius: 14px;
            padding: 24px;
            margin-bottom: 16px;
            box-shadow: {SHADOW};
        }}
        .doc-card h3 {{
            margin-top: 0 !important;
        }}


        /* =========================================================
           TABS
        ========================================================= */

        button[data-baseweb="tab"] {{
            font-family: '{POLICE_TEXTE}', sans-serif;
            font-weight: 600;
            font-size: 14px;
            padding: 10px 18px;
            border-radius: 8px 8px 0 0;
            transition: all 0.2s;
        }}
        button[data-baseweb="tab"][aria-selected="true"] {{
            background: {CARD_BG};
            border-bottom: 3px solid {TEAL};
        }}
        button[data-baseweb="tab"]:hover {{
            background: #f1f5f9;
        }}


        /* =========================================================
           PIED DE PAGE
        ========================================================= */

        .footer {{
            text-align: center;
            color: {TEXT_MUTED};
            font-size: 12px;
            padding: 18px 0;
            border-top: 1px solid {BORDER};
            margin-top: 30px;
        }}

        </style>
        """
    )


injecter_css()


# =============================================================================
# FONCTIONS HTML
# =============================================================================

def afficher_html(contenu):
    st.html(contenu)


def afficher_bandeau():
    afficher_html(
        f"""
        <div class="bandeau">
            <div class="bandeau-contenu">
                <div class="bandeau-icone">🛡️</div>
                <div>
                    <div class="bandeau-titre">Tableau de bord décisionnel — EMC Helpline</div>
                    <div class="bandeau-sous-titre">
                        CMRPI · Espace Maroc Cyberconfiance ·
                        Stage PFA 2026 · Projet N°10 ·
                        Stagiaire : NAFID IKRAM
                    </div>
                </div>
            </div>
        </div>
        """
    )


def carte_kpi(label, valeur, detail="", icone="📊", accent=TEAL):
    afficher_html(
        f"""
        <div class="kpi-card" style="--accent: {accent};">
            <div class="kpi-top">
                <div class="carte-label">{label}</div>
                <div class="kpi-icon">{icone}</div>
            </div>
            <div class="carte-valeur">{valeur}</div>
            <div class="carte-detail">{detail}</div>
        </div>
        """
    )


def carte_insight_html(icone, label, texte, couleur, classe="insight-item"):
    return f"""
        <div class="{classe}" style="--accent: {couleur};">
            <div class="insight-top">
                <div class="insight-icon" style="background: {couleur}14; color: {couleur};">
                    {icone}
                </div>
                <div class="insight-label">{label}</div>
            </div>
            <div class="insight-text">{texte}</div>
        </div>
    """

def carte_insight(icone, label, texte, couleur):
    afficher_html(carte_insight_html(icone, label, texte, couleur))


def legende(texte):
    afficher_html(f'<div class="legende-graphique">{texte}</div>')


def afficher_alerte_pic(mois, nombre, seuil):
    afficher_html(
        f"""
        <div class="alerte-pic">
            🚨 <strong>Pic détecté :</strong>
            {mois} — <strong>{nombre}</strong> signalement(s),
            au‑dessus du seuil automatique de {seuil:.1f}.
        </div>
        """
    )


# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def theme_graphique(fig):
    fig.update_layout(
        font_family=POLICE_TEXTE,
        title_font_family=POLICE_TITRE,
        title_font_size=18,
        title_font_color=NAVY,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, l=20, r=20, b=40),
    )
    fig.update_xaxes(gridcolor="#eef1f6", linecolor=BORDER, zeroline=False)
    fig.update_yaxes(gridcolor="#eef1f6", linecolor=BORDER, zeroline=False)
    return fig


def nom_mois(dt):
    return pd.Timestamp(dt).strftime("%b %Y")


def periode_vers_dates(df, debut_label, fin_label, labels_mois, mois_disponibles):
    i1 = labels_mois.index(debut_label)
    i2 = labels_mois.index(fin_label)
    if i1 > i2:
        i1, i2 = i2, i1
    debut = pd.Timestamp(mois_disponibles[i1])
    fin = pd.Timestamp(mois_disponibles[i2]) + pd.offsets.MonthEnd(0)
    return debut, fin


def calcul_variation(valeur_a, valeur_b):
    if valeur_a == 0:
        return np.nan if valeur_b != 0 else 0.0
    return round((valeur_b - valeur_a) / valeur_a * 100, 1)


def format_variation(v):
    if pd.isna(v):
        return "Non calculable"
    signe = "+" if v > 0 else ""
    return f"{signe}{v:.1f}%"


def extraire_top_profil(tableau, colonnes_label):
    """Retourne (libelle, pourcentage) pour la modalité la plus représentée."""
    if tableau is None or tableau.empty:
        return None

    tableau = tableau.copy()

    # Recherche souple du nom de la colonne contenant le libellé.
    colonne_label = next(
        (c for c in colonnes_label if c in tableau.columns),
        tableau.columns[0],
    )

    # Recherche souple de la colonne de pourcentage.
    colonne_pct = next(
        (c for c in ["pourcentage", "Pourcentage", "pct", "percentage"] if c in tableau.columns),
        None,
    )

    ligne = tableau.iloc[0]
    libelle = str(ligne[colonne_label]).strip()

    if colonne_pct is not None:
        try:
            pourcentage = float(ligne[colonne_pct])
            return libelle, pourcentage
        except (TypeError, ValueError):
            pass

    # Si le module KPI ne fournit pas de pourcentage, on le recalcule.
    colonne_nombre = next(
        (c for c in ["nombre", "count", "Nombre"] if c in tableau.columns),
        None,
    )
    if colonne_nombre is not None:
        try:
            total = pd.to_numeric(tableau[colonne_nombre], errors="coerce").sum()
            if total > 0:
                return libelle, float(ligne[colonne_nombre]) / total * 100
        except (TypeError, ValueError):
            pass

    return libelle, None


# =============================================================================
# CHARGEMENT DES DONNÉES (avec cache)
# =============================================================================

@st.cache_data
def charger_et_nettoyer(chemin):
    df_local = charger_donnees(chemin)
    return nettoyer_donnees(df_local)


df = charger_et_nettoyer(FICHIER_SOURCE)

if df.empty:
    st.error("Le fichier de données est vide.")
    st.stop()

colonnes_obligatoires = ["date", "plateforme"]
colonnes_manquantes = [c for c in colonnes_obligatoires if c not in df.columns]
if colonnes_manquantes:
    st.error("Colonnes nécessaires absentes : " + ", ".join(colonnes_manquantes))
    st.stop()

df = df.dropna(subset=["date"]).copy()

colonnes_optionnelles = {
    "cyberharcelementType": "Non renseigné",
    "accompagnement": "Non renseigné",
    "typeAccompagnement": "Non renseigné",
    "genre": "Non renseigné",
    "age": np.nan,
}
for colonne, valeur_defaut in colonnes_optionnelles.items():
    if colonne not in df.columns:
        df[colonne] = valeur_defaut

df["plateforme"] = df["plateforme"].fillna("Non renseigné").astype(str).str.strip()
df["cyberharcelementType"] = df["cyberharcelementType"].fillna("Non renseigné").astype(str).str.strip()
df["accompagnement"] = df["accompagnement"].fillna("Non renseigné").astype(str).str.strip()
df["typeAccompagnement"] = df["typeAccompagnement"].fillna("Non renseigné").astype(str).str.strip()

if not pd.api.types.is_datetime64_any_dtype(df["date"]):
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"]).copy()

if df.empty:
    st.error("Aucune date valide trouvée.")
    st.stop()


# =============================================================================
# EN-TÊTE
# =============================================================================

afficher_bandeau()


# =============================================================================
# FILTRES (sidebar) — Version corrigée
# =============================================================================

mois_disponibles = (
    df["date"]
    .dt.to_period("M")
    .dt.to_timestamp()
    .drop_duplicates()
    .sort_values()
    .to_numpy()
)

if len(mois_disponibles) == 0:
    st.error("Aucun mois valide trouvé.")
    st.stop()

labels_mois = [pd.Timestamp(m).strftime("%b %Y") for m in mois_disponibles]

plateformes_disponibles = sorted(df["plateforme"].dropna().astype(str).unique().tolist())
if len(plateformes_disponibles) == 0:
    st.error("Aucune plateforme disponible.")
    st.stop()


# Session state
if "periode_filtre" not in st.session_state:
    st.session_state.periode_filtre = (labels_mois[0], labels_mois[-1])
if "plateformes_filtre" not in st.session_state:
    st.session_state.plateformes_filtre = plateformes_disponibles.copy()


# Sidebar
with st.sidebar:
    # Identité / marque
    st.markdown(
        """
        <div class="side-brand">
            <div class="side-brand-row">
                <div class="side-brand-icon">🛡️</div>
                <div>
                    <div class="side-brand-title">EMC Helpline</div>
                    <div class="side-brand-sub">Tableau de bord décisionnel</div>
                </div>
            </div>
            <div class="side-project">◈ PROJET N°10 · CMRPI</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Filtres
    st.markdown(
        """
        <div class="side-section-title">
            <span class="side-section-icon">📅</span>
            <span>Période d'analyse</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    periode_selectionnee = st.select_slider(
        "Période (par mois)",
        options=labels_mois,
        value=st.session_state.periode_filtre,
        label_visibility="collapsed",
    )
    st.session_state.periode_filtre = periode_selectionnee

    st.markdown(
        """
        <div class="side-section-title">
            <span class="side-section-icon">◫</span>
            <span>Plateformes</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    plateformes_choisies = st.multiselect(
        "Plateforme(s)",
        options=plateformes_disponibles,
        default=st.session_state.plateformes_filtre,
        label_visibility="collapsed",
    )
    st.session_state.plateformes_filtre = plateformes_choisies

    if not plateformes_choisies:
        st.warning("Sélectionnez au moins une plateforme.")
        st.stop()

    # Actions
    if st.button("↻  Réinitialiser les filtres", width="stretch"):
        st.session_state.periode_filtre = (labels_mois[0], labels_mois[-1])
        st.session_state.plateformes_filtre = plateformes_disponibles.copy()
        st.rerun()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)

    placeholder_resume = st.empty()

    st.markdown(
        '<div class="side-help">Les indicateurs et graphiques se recalculent automatiquement selon les filtres actifs.</div>',
        unsafe_allow_html=True,
    )

# ---- Calcul du df_filtre ----
mois_debut_label, mois_fin_label = st.session_state.periode_filtre
mois_debut, mois_fin = periode_vers_dates(
    df, mois_debut_label, mois_fin_label, labels_mois, mois_disponibles
)

df_filtre = df[
    (df["date"] >= mois_debut)
    & (df["date"] <= mois_fin)
    & (df["plateforme"].isin(st.session_state.plateformes_filtre))
].copy()

# Mise à jour du résumé et du bouton d'export dans le sidebar
with st.sidebar:
    with placeholder_resume.container():
        nb_signaux = len(df_filtre)
        st.markdown(
            f"""
            <div class="side-status">
                <div class="side-status-icon">📊</div>
                <div>
                    <div class="side-status-label">Signalements affichés</div>
                    <div class="side-status-value">{nb_signaux}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    csv_filtre = df_filtre.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "⬇  Exporter les données filtrées",
        data=csv_filtre,
        file_name="emc_helpline_donnees_filtrees.csv",
        mime="text/csv",
        width="stretch",
    )

    st.markdown(
        """
        <div class="side-footer">
            EMC HELPLINE · CMRPI<br>
            Analyse décisionnelle · 2025
        </div>
        """,
        unsafe_allow_html=True,
    )


# =============================================================================
# KPI CARDS
# =============================================================================

kpi4_f = kpi4_taux_accompagnement(df_filtre)
if not isinstance(kpi4_f, dict):
    kpi4_f = dict(kpi4_f)
kpi4_f["taux_global"] = float(kpi4_f.get("taux_global", 0))
kpi4_f["nb_oui"] = int(kpi4_f.get("nb_oui", 0))

kpi1_f = kpi1_volume_par_mois(df_filtre)
if not kpi1_f.empty:
    mois_pic = kpi1_f.loc[kpi1_f["nombre_signalements"].idxmax()]
else:
    mois_pic = None

col1, col2, col3, col4 = st.columns(4)

with col1:
    carte_kpi(
        "Signalements",
        len(df_filtre),
        "sur la période filtrée",
        icone="📊",
        accent=NAVY,
    )
with col2:
    carte_kpi(
        "Taux d'accompagnement",
        f"{kpi4_f['taux_global']}%",
        "demande explicite d'aide",
        icone="🤝",
        accent=TEAL,
    )
with col3:
    if mois_pic is not None:
        carte_kpi(
            "Mois le plus actif",
            nom_mois(mois_pic["mois"]),
            f"{int(mois_pic['nombre_signalements'])} signalements",
            icone="📈",
            accent=AMBER,
        )
    else:
        carte_kpi("Mois le plus actif", "—", "Aucune donnée", icone="📈", accent=AMBER)
with col4:
    carte_kpi(
        "Plateformes sélectionnées",
        len(st.session_state.plateformes_filtre),
        "plateforme(s) active(s)",
        icone="📱",
        accent=INDIGO,
    )


# =============================================================================
# SECTION À RETENIR
# =============================================================================

kpi2_f = kpi2_repartition_type(df_filtre)
kpi3_f = kpi3_repartition_plateforme(df_filtre)
kpi5_f = kpi5_profil_victimes(df_filtre)

# Profil synthétique des victimes : ces deux indicateurs sont affichés
# dans « À retenir » et restent cohérents avec l'onglet « Profil des victimes ».
top_genre = extraire_top_profil(kpi5_f.get("genre"), ["genre", "Genre"])
top_age = extraire_top_profil(kpi5_f.get("age"), ["tranche_age", "tranche d'âge", "age", "Age"])

afficher_html(
    """
    <div class="retient-header">
        <div class="retient-icon">💡</div>
        <div>
            <div class="retient-title">À retenir</div>
            <div class="retient-subtitle">Les principaux enseignements de la période sélectionnée</div>
        </div>
    </div>
    """
)

insights = []

# Les informations sont volontairement courtes dans « À retenir » :
# la section sert de synthèse décisionnelle, tandis que les onglets
# présentent les analyses détaillées.

insights.append(
    {
        "icone": "📊",
        "label": "Volume analysé",
        "texte": f"<strong>{len(df_filtre)}</strong> signalement(s) sur la période et les plateformes sélectionnées.",
        "couleur": NAVY,
    }
)

if not kpi2_f.empty:
    top_type = kpi2_f.iloc[0]
    insights.append(
        {
            "icone": "⚠️",
            "label": "Type dominant",
            "texte": f"<strong>{top_type['cyberharcelementType']}</strong> · {top_type['pourcentage']}% des signalements.",
            "couleur": CORAL,
        }
    )

if not kpi3_f.empty:
    top_plateforme = kpi3_f.iloc[0]
    insights.append(
        {
            "icone": "📱",
            "label": "Plateforme dominante",
            "texte": f"<strong>{top_plateforme['plateforme']}</strong> · {top_plateforme['pourcentage']}% des signalements.",
            "couleur": INDIGO,
        }
    )

insights.append(
    {
        "icone": "🤝",
        "label": "Accompagnement",
        "texte": f"<strong>{kpi4_f['taux_global']}%</strong> des signalements correspondent à une demande explicite d'aide.",
        "couleur": TEAL,
    }
)

if mois_pic is not None:
    insights.append(
        {
            "icone": "📈",
            "label": "Période la plus active",
            "texte": f"<strong>{nom_mois(mois_pic['mois'])}</strong> · {int(mois_pic['nombre_signalements'])} signalement(s).",
            "couleur": AMBER,
        }
    )

# Genre et âge : deux indicateurs indépendants dans « À retenir ».
if top_genre is not None:
    libelle_genre, pct_genre = top_genre
    genre_detail = f"{pct_genre:.1f}%" if pct_genre is not None else "—"
    insights.append(
        {
            "icone": "👤",
            "label": "Genre majoritaire",
            "texte": f"<strong>{libelle_genre}</strong> · {genre_detail} des signalements renseignés.",
            "couleur": NAVY_LIGHT,
        }
    )

if top_age is not None:
    libelle_age, pct_age = top_age
    age_detail = f"{pct_age:.1f}%" if pct_age is not None else "—"
    insights.append(
        {
            "icone": "🎂",
            "label": "Tranche d'âge dominante",
            "texte": f"<strong>{libelle_age}</strong> · {age_detail} des signalements renseignés.",
            "couleur": AMBER,
        }
    )

# Une seule surface visuelle : plus légère et plus cohérente.
panneau = '<div class="insight-panel">'
for insight in insights:
    panneau += carte_insight_html(
        insight["icone"],
        insight["label"],
        insight["texte"],
        insight["couleur"],
        classe="insight-item",
    )
panneau += '</div>'
afficher_html(panneau)

st.write("")


# =============================================================================
# ONGLETS
# =============================================================================

(
    onglet1,
    onglet2,
    onglet3,
    onglet4,
    onglet5,
    onglet6,
) = st.tabs(
    [
        "📈 Volume & Types",
        "📱 Plateformes",
        "🤝 Accompagnement",
        "👥 Profil des victimes",
        "📊 Comparaison & Analyses",
        "📖 Documentation",
    ]
)


# =============================================================================
# ONGLET 1 — Volume & Types
# =============================================================================

with onglet1:
    with st.container(border=True):
        kpi1 = kpi1_volume_par_mois(df_filtre)
        if not kpi1.empty:
            fig1 = theme_graphique(graphique_kpi1(kpi1))
            fig1.update_layout(title="Évolution mensuelle des signalements")
            fig1.update_traces(line_color=NAVY, marker_color=NAVY)
            st.plotly_chart(fig1, use_container_width=True)
            if (kpi1["nombre_signalements"] == 0).any():
                legende(
                    "⚠️ Un ou plusieurs mois de la période sélectionnée ne comportent aucun signalement dans le fichier fourni."
                )

    st.write("")
    with st.container(border=True):
        if not kpi2_f.empty:
            fig2 = theme_graphique(graphique_kpi2(kpi2_f))
            fig2.update_layout(title="Répartition par type de cyberharcèlement")
            st.plotly_chart(fig2, use_container_width=True)
            type_principal = kpi2_f.iloc[0]
            legende(
                f"Type le plus fréquent sur la période : <strong>{type_principal['cyberharcelementType']}</strong> ({type_principal['pourcentage']}%)."
            )


# =============================================================================
# ONGLET 2 — Plateformes
# =============================================================================

with onglet2:
    with st.container(border=True):
        if not kpi3_f.empty:
            fig3 = theme_graphique(graphique_kpi3(kpi3_f))
            fig3.update_layout(title="Répartition par plateforme")
            st.plotly_chart(fig3, use_container_width=True)
            plateforme_principale = kpi3_f.iloc[0]
            legende(
                f"Plateforme la plus représentée : <strong>{plateforme_principale['plateforme']}</strong> ({plateforme_principale['pourcentage']}%)."
            )


# =============================================================================
# ONGLET 3 — Accompagnement (avec jauge personnalisée, sous-titre supprimé)
# =============================================================================

with onglet3:
    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            fig4 = graphique_kpi4(kpi4_f)
            # Suppression du sous-titre "KPI 4 - ..."
            fig4.update_layout(title=None, title_text="")
            if fig4.data and fig4.data[0].type == 'indicator':
                fig4.data[0].title = None  # <-- suppression définitive
                # Personnalisation de la jauge
                gauge_obj = fig4.data[0].gauge
                gauge_obj.bar.color = TEAL
                gauge_obj.steps = [
                    {'range': [0, 20], 'color': '#f1f5f9'},
                    {'range': [20, 40], 'color': '#e2e8f0'},
                    {'range': [40, 60], 'color': '#cbd5e1'},
                    {'range': [60, 80], 'color': '#94a3b8'},
                    {'range': [80, 100], 'color': '#64748b'},
                ]
                fig4.data[0].number.font.size = 40
                fig4.data[0].number.font.color = NAVY
                fig4.data[0].number.suffix = '%'
                gauge_obj.bar.thickness = 0.4
            # Titre personnalisé
            fig4.update_layout(
                title=dict(
                    text="Part des demandes d'accompagnement",
                    font=dict(size=18, color=NAVY, family=POLICE_TITRE),
                    x=0.5,
                    xanchor='center'
                )
            )
            fig4 = theme_graphique(fig4)
            fig4.update_layout(height=280, margin=dict(t=60, b=20, l=20, r=20))
            st.plotly_chart(fig4, use_container_width=True)

    with c2:
        with st.container(border=True):
            if kpi4_f["nb_oui"] > 0:
                fig4d = graphique_kpi4_detail(kpi4_f)
                fig4d.update_layout(title=None, title_text="")
                fig4d.update_layout(
                    title=dict(
                        text="Types d'accompagnement demandés",
                        font=dict(size=18, color=NAVY, family=POLICE_TITRE),
                        x=0.5,
                        xanchor='center'
                    )
                )
                fig4d = theme_graphique(fig4d)
                st.plotly_chart(fig4d, use_container_width=True)
            else:
                st.info("Aucune demande d'accompagnement sur la période sélectionnée.")

    st.write("")
    st.subheader("🔎 Analyse détaillée de l'accompagnement")

    total = len(df_filtre)
    nb_oui = int(kpi4_f["nb_oui"])
    nb_non = total - nb_oui

    a1, a2, a3 = st.columns(3)
    with a1:
        carte_kpi(
            "Demandes d'accompagnement",
            nb_oui,
            f"sur {total} signalements",
            icone="🤝",
            accent=TEAL,
        )
    with a2:
        pourcentage_sans = round(nb_non / total * 100, 1) if total > 0 else 0
        carte_kpi(
            "Sans accompagnement",
            nb_non,
            f"soit {pourcentage_sans}%",
            icone="❌",
            accent=INDIGO,
        )
    with a3:
        carte_kpi(
            "Taux d'accompagnement",
            f"{kpi4_f['taux_global']}%",
            "demande explicite d'aide",
            icone="📊",
            accent=AMBER,
        )

    # Graphique alternatif des types d'accompagnement (propre)
    if nb_oui > 0:
        types_bruts = df_filtre.loc[
            df_filtre["accompagnement"].astype(str).str.strip().str.lower() == "oui",
            "typeAccompagnement"
        ]

        types_propres = []
        for val in types_bruts:
            if pd.notna(val) and val.strip():
                for t in val.replace(';', ',').split(','):
                    t = t.strip()
                    if t and t != "Non renseigné":
                        types_propres.append(t)

        if types_propres:
            detail_accomp = pd.Series(types_propres).value_counts().reset_index()
            detail_accomp.columns = ["typeAccompagnement", "nombre"]

            fig_accomp = px.bar(
                detail_accomp,
                x="typeAccompagnement",
                y="nombre",
                text="nombre",
                title="Répartition des types d'accompagnement demandés",
                labels={"typeAccompagnement": "Type d'accompagnement", "nombre": "Nombre de demandes"},
                color_discrete_sequence=[TEAL],
            )
            fig_accomp.update_traces(textposition="outside", marker_line_width=0)
            st.plotly_chart(theme_graphique(fig_accomp), use_container_width=True)
        else:
            st.info("Aucun type d'accompagnement spécifié pour les demandes.")


# =============================================================================
# ONGLET 4 — Profil des victimes
# =============================================================================

with onglet4:
    kpi5 = kpi5_f
    fig_genre, fig_age = graphique_kpi5(kpi5)

    c1, c2 = st.columns(2)

    with c1:
        with st.container(border=True):
            if not kpi5["genre"].empty:
                fig_genre = theme_graphique(fig_genre)
                fig_genre.update_layout(title="Répartition par genre")
                st.plotly_chart(fig_genre, use_container_width=True)
            else:
                st.info("Aucune donnée de genre renseignée sur la période sélectionnée.")

    with c2:
        with st.container(border=True):
            if not kpi5["age"].empty:
                fig_age = theme_graphique(fig_age)
                fig_age.update_layout(title="Répartition par tranche d'âge")
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("Aucune donnée d'âge renseignée sur la période sélectionnée.")


# =============================================================================
# ONGLET 5 — Comparaison & Analyses (amélioré)
# =============================================================================

with onglet5:
    st.subheader("⭐ Comparaison entre deux périodes")
    st.caption(
        "Sélectionne deux périodes pour comparer le volume de signalements et calculer automatiquement la variation en pourcentage."
    )

    ca, cb = st.columns(2)
    with ca:
        st.markdown("### 📅 Période A")
        periode_a = st.select_slider(
            "Période A",
            options=labels_mois,
            value=(labels_mois[0], labels_mois[len(labels_mois)//2]),
            key="periode_comparaison_a",
        )
    with cb:
        st.markdown("### 📅 Période B")
        periode_b = st.select_slider(
            "Période B",
            options=labels_mois,
            value=(labels_mois[len(labels_mois)//2], labels_mois[-1]),
            key="periode_comparaison_b",
        )

    a_debut, a_fin = periode_vers_dates(df, periode_a[0], periode_a[1], labels_mois, mois_disponibles)
    b_debut, b_fin = periode_vers_dates(df, periode_b[0], periode_b[1], labels_mois, mois_disponibles)

    df_a = df[(df["date"] >= a_debut) & (df["date"] <= a_fin) & (df["plateforme"].isin(st.session_state.plateformes_filtre))].copy()
    df_b = df[(df["date"] >= b_debut) & (df["date"] <= b_fin) & (df["plateforme"].isin(st.session_state.plateformes_filtre))].copy()

    nb_a = len(df_a)
    nb_b = len(df_b)
    variation = calcul_variation(nb_a, nb_b)

    c1, c2, c3 = st.columns(3)
    with c1:
        carte_kpi(
            "Signalements — période A",
            nb_a,
            f"{periode_a[0]} → {periode_a[1]}",
            icone="📊",
            accent=NAVY,
        )
    with c2:
        carte_kpi(
            "Signalements — période B",
            nb_b,
            f"{periode_b[0]} → {periode_b[1]}",
            icone="📊",
            accent=INDIGO,
        )
    with c3:
        accent_variation = TEAL if (pd.notna(variation) and variation <= 0) else CORAL
        carte_kpi(
            "Variation A → B",
            format_variation(variation),
            "évolution du volume",
            icone="📈",
            accent=accent_variation,
        )

    st.write("")
    comp_df = pd.DataFrame({"Période": ["A", "B"], "Signalements": [nb_a, nb_b]})
    fig_comp = px.bar(
        comp_df,
        x="Période",
        y="Signalements",
        text="Signalements",
        title="Comparaison du volume de signalements",
        color="Période",
        color_discrete_sequence=[NAVY, TEAL],
    )
    fig_comp.update_traces(textposition="outside", marker_line_width=0)
    st.plotly_chart(theme_graphique(fig_comp), use_container_width=True)

    st.divider()

    # Top 5
    st.subheader("⭐ Top 5 des types de cyberharcèlement")
    top5 = df_filtre["cyberharcelementType"].value_counts().head(5).reset_index()
    top5.columns = ["cyberharcelementType", "nombre"]
    if not top5.empty:
        fig_top5 = px.bar(
            top5.sort_values("nombre"),
            x="nombre",
            y="cyberharcelementType",
            orientation="h",
            text="nombre",
            title="Top 5 des types de cyberharcèlement",
            labels={"cyberharcelementType": "Type", "nombre": "Nombre de signalements"},
            color_discrete_sequence=[NAVY],
        )
        fig_top5.update_traces(textposition="outside", marker_line_width=0)
        st.plotly_chart(theme_graphique(fig_top5), use_container_width=True)

    st.divider()

    # Analyse croisée
    st.subheader("⭐ Analyse croisée : plateforme × type")
    croise = pd.crosstab(df_filtre["plateforme"], df_filtre["cyberharcelementType"])
    if not croise.empty:
        fig_croise = px.bar(
            croise,
            barmode="stack",
            title="Répartition des types de cyberharcèlement par plateforme",
            labels={"value": "Nombre de signalements", "plateforme": "Plateforme", "variable": "Type de cyberharcèlement"},
            color_discrete_sequence=PALETTE_GRAPHIQUES,
        )
        st.plotly_chart(theme_graphique(fig_croise), use_container_width=True)
        st.dataframe(croise, use_container_width=True)

    st.divider()

    # Pics
    st.subheader("⭐ Détection automatique des pics")
    serie_pic = kpi1_volume_par_mois(df_filtre).copy()
    if len(serie_pic) >= 2:
        moyenne = float(serie_pic["nombre_signalements"].mean())
        ecart_type = float(serie_pic["nombre_signalements"].std(ddof=0))
        seuil_pic = moyenne + ecart_type
        serie_pic["pic"] = serie_pic["nombre_signalements"] > seuil_pic
        pics = serie_pic[serie_pic["pic"]].copy()
        if not pics.empty:
            for _, ligne in pics.iterrows():
                afficher_alerte_pic(nom_mois(ligne["mois"]), int(ligne["nombre_signalements"]), seuil_pic)
        else:
            st.success("Aucun pic automatique détecté sur la période sélectionnée.")
        st.caption(
            f"Règle utilisée : pic = volume mensuel supérieur à moyenne + écart‑type ({seuil_pic:.1f})."
        )
    else:
        st.info("Pas assez de mois pour effectuer une détection automatique des pics.")


# =============================================================================
# ONGLET 6 — Documentation
# =============================================================================

with onglet6:
    st.subheader("📖 Documentation du tableau de bord")

    afficher_html(
        f"""
        <div class="doc-card">
            <h3>🎯 Objectif</h3>
            <p>
                Ce tableau de bord permet d'explorer les signalements EMC Helpline,
                d'identifier les tendances principales et de faciliter l'analyse décisionnelle
                à partir des données disponibles.
            </p>
        </div>
        """
    )

    st.markdown("### 📌 Sources et données")
    st.write("Source principale : fichier Excel `signalements-_1_.xlsx`.")
    st.write(f"Nombre total de signalements dans le fichier : **{len(df)}**.")
    st.write(f"Nombre de signalements actuellement filtrés : **{len(df_filtre)}**.")

    st.markdown("### 📊 KPI principaux")
    documentation_kpi = pd.DataFrame(
        {
            "KPI": ["KPI 1", "KPI 2", "KPI 3", "KPI 4", "KPI 5"],
            "Indicateur": [
                "Volume de signalements par mois",
                "Répartition par type de cyberharcèlement",
                "Répartition par plateforme",
                "Taux de demande d'accompagnement",
                "Profil des victimes (genre et âge)",
            ],
            "Utilité": [
                "Suivre l'évolution temporelle des signalements.",
                "Identifier les formes de cyberharcèlement les plus fréquentes.",
                "Identifier les plateformes les plus représentées.",
                "Mesurer la proportion de signalements demandant un accompagnement.",
                "Analyser la répartition des victimes selon le genre et la tranche d'âge, avec synthèse des modalités dominantes dans « À retenir ».",
            ],
        }
    )
    st.dataframe(documentation_kpi, use_container_width=True, hide_index=True)

    st.markdown("### 🎛️ Filtres disponibles")
    st.markdown(
        """
        - **Période :** sélection d'un intervalle de mois.
        - **Plateforme(s) :** sélection d'une ou plusieurs plateformes.
        - **Réinitialiser les filtres :** revient à la période complète et à toutes les plateformes.
        """
    )

    st.markdown("### ⭐ Analyses complémentaires")
    st.markdown(
        """
        - Comparaison entre deux périodes.
        - Variation du volume en pourcentage.
        - Top 5 des types de cyberharcèlement.
        - Analyse croisée plateforme × type.
        - Analyse détaillée de l'accompagnement.
        - Détection automatique des pics.
        - Synthèse automatique « À retenir ».
        - Export CSV des données filtrées.
        """
    )

    st.markdown("### 🧹 Préparation des données")
    st.markdown(
        """
        Les données sont chargées et nettoyées par les fonctions du module `kpi_dashboard.py`.
        Le nettoyage porte notamment sur les espaces, la casse, les dates et la gestion des valeurs manquantes.
        """
    )

    st.markdown("### ⚠️ Limites")
    st.markdown(
        """
        - Les résultats dépendent directement de la qualité et de la complétude du fichier source.
        - Une absence de signalement dans un mois ne signifie pas nécessairement une absence réelle de cyberharcèlement.
        - La détection des pics est un indicateur exploratoire basé sur la règle moyenne + écart‑type.
        """
    )

    st.markdown("### 🛠️ Technologies")
    st.markdown("**Python · Pandas · Plotly · Streamlit · Excel**")


# =============================================================================
# PIED DE PAGE
# =============================================================================

st.write("")
afficher_html(
    f"""
    <div class="footer">
        Données issues de signalements-_1_.xlsx ·
        {len(df)} signalements au total ·
        {len(df_filtre)} affichés selon les filtres actifs ·
        Tableau de bord réalisé avec Python, pandas, Plotly et Streamlit.
    </div>
    """
)