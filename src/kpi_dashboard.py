"""
CMRPI - EMC Helpline | Projet N°10 - Tableau de bord décisionnel
Jalon 2 (1er - 15 août 2026) : Nettoyage des données, calcul des 5 KPI, graphiques Plotly

Auteure : NAFID IKRAM
Encadrante : Dr. Yasmina Al Marouni

Ce script :
  1. Charge le fichier signalements-_1_.xlsx
  2. Nettoie les données (casse, espaces, valeurs manquantes)
  3. Calcule les 5 KPI définis et validés au Jalon 1
  4. Génère un graphique Plotly par KPI (fig.show() ouvre chaque graphique
     dans le navigateur ; ces mêmes objets "fig" seront réutilisés tels
     quels au Jalon 3 dans l'application Streamlit avec st.plotly_chart(fig))
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# CHARTE GRAPHIQUE (cohérente sur les 7 graphiques et le tableau de bord)
# ---------------------------------------------------------------------------

COULEUR_PRIMAIRE = "#1e3a5f"    # bleu marine — titres, accents forts
COULEUR_ACCENT = "#2563eb"      # bleu vif — courbes, barres principales
COULEUR_SUCCES = "#0d9488"      # teal — indicateurs positifs
COULEUR_ALERTE = "#f59e0b"      # ambre — points d'attention
PALETTE_CATEGORIELLE = [
    "#1e3a5f", "#2563eb", "#0d9488", "#f59e0b",
    "#dc2626", "#7c3aed", "#64748b", "#0891b2",
]
POLICE = "Segoe UI, Helvetica, Arial, sans-serif"


def appliquer_theme(fig):
    """Applique une mise en forme cohérente (police, fond, titre) à toute figure."""
    fig.update_layout(
        font=dict(family=POLICE, size=13, color="#1f2937"),
        title_font=dict(family=POLICE, size=16, color=COULEUR_PRIMAIRE),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=60, b=50, l=50, r=30),
    )
    fig.update_xaxes(gridcolor="#eef1f5", linecolor="#d1d5db")
    fig.update_yaxes(gridcolor="#eef1f5", linecolor="#d1d5db")
    return fig

# ---------------------------------------------------------------------------
# 0. CONFIGURATION
# ---------------------------------------------------------------------------

FICHIER_SOURCE = "data/signalements-_1_.xlsx"   # adapte le chemin si besoin


# ---------------------------------------------------------------------------
# 1. CHARGEMENT DES DONNÉES
# ---------------------------------------------------------------------------

def charger_donnees(chemin: str) -> pd.DataFrame:
    """Charge le fichier Excel des signalements."""
    df = pd.read_excel(chemin)
    print(f"Données chargées : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    return df


# ---------------------------------------------------------------------------
# 2. NETTOYAGE DES DONNÉES
# ---------------------------------------------------------------------------
#
# Rappel des constats du Jalon 1 :
#   - Casse incohérente : "Oui"/"oui"/"OUI", "fr"/"FR"
#   - Espaces parasites : " Diffamation" vs "Diffamation"
#   - Valeurs manquantes : genre (5), age (9), titulaire/emetteur (10 chacun)
#
# Stratégie retenue :
#   - Colonnes texte : strip() des espaces + normalisation de la casse
#     (première lettre majuscule, reste minuscule -> "Oui", "Non", "Fr", "Ar")
#   - Valeurs manquantes : on les GARDE (on ne les supprime pas), mais on les
#     exclut explicitement du calcul des pourcentages quand c'est pertinent
#     (comme précisé dans le Jalon 1 pour le KPI 5). On les remplace par
#     l'étiquette "Non renseigné" pour qu'elles restent visibles si besoin.

def nettoyer_donnees(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Colonnes texte à nettoyer : suppression des espaces + normalisation de casse
    colonnes_texte = [
        "titulaire", "emetteur", "cyberharcelementType", "plateforme",
        "accompagnement", "genre", "age", "typeAccompagnement",
        "langue", "anonymat",
    ]
    for col in colonnes_texte:
        # 1) strip() : enlève les espaces en début/fin
        # 2) normalisation de la casse pour les colonnes à valeurs fixes
        df[col] = df[col].astype("string").str.strip()

    # Normalisation spécifique de la casse (Oui/Non, fr/ar)
    # .str.capitalize() -> "OUI" devient "Oui", "oui" devient "Oui"
    for col in ["titulaire", "accompagnement", "anonymat"]:
        df[col] = df[col].str.capitalize()

    df["langue"] = df["langue"].str.lower()  # "FR" -> "fr"

    # La colonne date est déjà au format datetime après read_excel ;
    # on s'assure du type au cas où le fichier source varie
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Valeurs manquantes : on les identifie clairement plutôt que de les
    # laisser en NaN silencieux (plus simple à visualiser sur les graphiques)
    for col in ["titulaire", "emetteur", "genre", "age"]:
        df[col] = df[col].fillna("Non renseigné")

    print("Nettoyage terminé.")
    print(df[colonnes_texte].nunique())
    return df


# ---------------------------------------------------------------------------
# 3. CALCUL DES 5 KPI
# ---------------------------------------------------------------------------

def kpi1_volume_par_mois(df: pd.DataFrame) -> pd.DataFrame:
    """KPI 1 - Volume de signalements par mois.

    Important : on complète avec les mois SANS aucun signalement (valeur 0),
    entre le premier et le dernier mois présents dans les données. Sans ça,
    un mois vide (ex. mai-octobre) n'apparaîtrait pas du tout dans le
    résultat, et le graphique tracerait une ligne diagonale directe entre
    les deux mois voisins au lieu de passer par 0.
    """
    serie = (
        df.assign(mois=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby("mois")["id"]
        .count()
    )
    tous_les_mois = pd.date_range(
        df["date"].min().to_period("M").to_timestamp(),
        df["date"].max().to_period("M").to_timestamp(),
        freq="MS",
    )
    serie = serie.reindex(tous_les_mois, fill_value=0)
    serie = serie.rename_axis("mois").reset_index(name="nombre_signalements")
    return serie


def kpi2_repartition_type(df: pd.DataFrame) -> pd.DataFrame:
    """KPI 2 - Répartition (%) par type de cyberharcèlement."""
    total = len(df)
    serie = (
        df.groupby("cyberharcelementType")["id"]
        .count()
        .reset_index(name="nombre")
        .assign(pourcentage=lambda d: (d["nombre"] / total * 100).round(1))
        .sort_values("nombre", ascending=False)
    )
    return serie


def kpi3_repartition_plateforme(df: pd.DataFrame) -> pd.DataFrame:
    """KPI 3 - Répartition (%) par plateforme."""
    total = len(df)
    serie = (
        df.groupby("plateforme")["id"]
        .count()
        .reset_index(name="nombre")
        .assign(pourcentage=lambda d: (d["nombre"] / total * 100).round(1))
        .sort_values("nombre", ascending=False)
    )
    return serie


def kpi4_taux_accompagnement(df: pd.DataFrame) -> dict:
    """KPI 4 - Taux global de demande d'accompagnement + détail par type."""
    total = len(df)
    nb_oui = (df["accompagnement"] == "Oui").sum()
    taux_global = round(nb_oui / total * 100, 1)

    # Détail du type d'accompagnement, uniquement pour les "Oui"
    detail = (
        df.loc[df["accompagnement"] == "Oui", "typeAccompagnement"]
        .value_counts()
        .reset_index()
    )
    detail.columns = ["typeAccompagnement", "nombre"]

    return {"taux_global": taux_global, "nb_oui": nb_oui, "total": total, "detail": detail}


def kpi5_profil_victimes(df: pd.DataFrame) -> dict:
    """KPI 5 - Profil démographique des victimes (genre, âge), NaN exclus."""
    df_genre = df[df["genre"] != "Non renseigné"]
    df_age = df[df["age"] != "Non renseigné"]

    genre = (
        df_genre["genre"].value_counts(normalize=True).mul(100).round(1)
        .reset_index()
    )
    genre.columns = ["genre", "pourcentage"]

    age = (
        df_age["age"].value_counts(normalize=True).mul(100).round(1)
        .reset_index()
    )
    age.columns = ["age", "pourcentage"]

    return {"genre": genre, "age": age}


# ---------------------------------------------------------------------------
# 4. GRAPHIQUES PLOTLY (un par KPI)
# ---------------------------------------------------------------------------

def centrer_titre(fig):
    """Centre le titre au-dessus du graphique (Plotly l'aligne à gauche par défaut)."""
    fig.update_layout(title={"x": 0.5, "xanchor": "center"})
    return fig


def graphique_kpi1(data: pd.DataFrame):
    fig = px.line(
        data, x="mois", y="nombre_signalements", markers=True,
        title="KPI 1 - Volume de signalements par mois",
        labels={"mois": "Mois", "nombre_signalements": "Nombre de signalements"},
    )
    fig.update_traces(
        line_color=COULEUR_ACCENT, line_width=3,
        marker=dict(size=8, color=COULEUR_PRIMAIRE, line=dict(width=2, color="white")),
        fill="tozeroy", fillcolor="rgba(37, 99, 235, 0.08)",
    )
    # Forcer un repère (tick) sur CHAQUE mois, même sans donnée, pour que les
    # mois absents (ex. mai-octobre) soient visibles sur l'axe plutôt que
    # simplement "sautés" par l'affichage automatique de Plotly.
    fig.update_xaxes(dtick="M1", tickformat="%b %Y")
    fig.update_layout(width=1000, height=500)
    return appliquer_theme(centrer_titre(fig))


def graphique_kpi2(data: pd.DataFrame):
    fig = px.bar(
        data, x="cyberharcelementType", y="nombre", text="pourcentage",
        title="KPI 2 - Répartition par type de cyberharcèlement",
        labels={"cyberharcelementType": "Type", "nombre": "Nombre de signalements"},
        color_discrete_sequence=[COULEUR_ACCENT],
    )
    fig.update_traces(
        texttemplate="%{text}%", textposition="outside",
        marker_line_width=0, marker_color=COULEUR_ACCENT,
    )
    fig.update_layout(xaxis_tickangle=-30, width=900, height=500)
    return appliquer_theme(centrer_titre(fig))


def graphique_kpi3(data: pd.DataFrame):
    fig = px.pie(
        data, names="plateforme", values="nombre",
        title="KPI 3 - Répartition par plateforme",
        hole=0.45,
        color_discrete_sequence=PALETTE_CATEGORIELLE,
    )
    fig.update_traces(
        textinfo="label+percent", textfont_size=13,
        marker=dict(line=dict(color="white", width=2)),
    )
    fig.update_layout(width=700, height=500, showlegend=False)
    return appliquer_theme(centrer_titre(fig))


def graphique_kpi4(resultat: dict):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=resultat["taux_global"],
        number={"suffix": "%", "font": {"size": 44, "color": COULEUR_PRIMAIRE}},
        title={"text": "KPI 4 - Taux de demande d'accompagnement"},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#9ca3af"},
            "bar": {"color": COULEUR_SUCCES, "thickness": 0.75},
            "bgcolor": "#f1f5f9",
            "borderwidth": 0,
        },
    ))
    # Taille fixe : sans ça, une jauge s'étire pour remplir toute la fenêtre
    # du navigateur et paraît disproportionnée.
    fig.update_layout(width=600, height=400)
    return appliquer_theme(centrer_titre(fig))


def graphique_kpi4_detail(resultat: dict):
    fig = px.bar(
        resultat["detail"], x="typeAccompagnement", y="nombre",
        title="KPI 4 (détail) - Type d'accompagnement demandé",
        labels={"typeAccompagnement": "Type d'accompagnement", "nombre": "Nombre"},
        color_discrete_sequence=[COULEUR_PRIMAIRE],
    )
    fig.update_traces(marker_line_width=0)
    fig.update_layout(width=900, height=500)
    return appliquer_theme(centrer_titre(fig))


def graphique_kpi5(resultat: dict):
    fig_genre = px.pie(
        resultat["genre"], names="genre", values="pourcentage",
        title="KPI 5a - Profil des victimes par genre",
        hole=0.45,
        color_discrete_sequence=[COULEUR_PRIMAIRE, COULEUR_ALERTE],
    )
    fig_genre.update_traces(
        textinfo="label+percent", textfont_size=13,
        marker=dict(line=dict(color="white", width=2)),
    )
    fig_genre.update_layout(width=700, height=500, showlegend=False)
    appliquer_theme(centrer_titre(fig_genre))

    fig_age = px.bar(
        resultat["age"], x="age", y="pourcentage",
        title="KPI 5b - Profil des victimes par tranche d'âge",
        labels={"age": "Tranche d'âge", "pourcentage": "Pourcentage (%)"},
        color_discrete_sequence=[COULEUR_SUCCES],
    )
    fig_age.update_traces(marker_line_width=0)
    fig_age.update_layout(width=900, height=500)
    appliquer_theme(centrer_titre(fig_age))

    return fig_genre, fig_age


# ---------------------------------------------------------------------------
# 5. PROGRAMME PRINCIPAL
# ---------------------------------------------------------------------------

def main():
    df = charger_donnees(FICHIER_SOURCE)
    df = nettoyer_donnees(df)

    print("\n--- KPI 1 : Volume par mois ---")
    kpi1 = kpi1_volume_par_mois(df)
    print(kpi1)
    graphique_kpi1(kpi1).show()

    print("\n--- KPI 2 : Répartition par type ---")
    kpi2 = kpi2_repartition_type(df)
    print(kpi2)
    graphique_kpi2(kpi2).show()

    print("\n--- KPI 3 : Répartition par plateforme ---")
    kpi3 = kpi3_repartition_plateforme(df)
    print(kpi3)
    graphique_kpi3(kpi3).show()

    print("\n--- KPI 4 : Taux d'accompagnement ---")
    kpi4 = kpi4_taux_accompagnement(df)
    print(f"Taux global : {kpi4['taux_global']}% ({kpi4['nb_oui']}/{kpi4['total']})")
    print(kpi4["detail"])
    graphique_kpi4(kpi4).show()
    graphique_kpi4_detail(kpi4).show()

    print("\n--- KPI 5 : Profil démographique ---")
    kpi5 = kpi5_profil_victimes(df)
    print(kpi5["genre"])
    print(kpi5["age"])
    fig_genre, fig_age = graphique_kpi5(kpi5)
    fig_genre.show()
    fig_age.show()


if __name__ == "__main__":
    main()
