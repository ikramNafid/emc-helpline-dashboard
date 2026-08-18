# Documentation du tableau de bord — EMC Helpline

Projet PFA 2026 · CMRPI · Fiche N°10 · Jalon 3 (16-31 août 2026)
Stagiaire : NAFID IKRAM

## 1. Objectif

Assembler les 7 graphiques Plotly produits au Jalon 2 dans une application
Streamlit interactive, avec des filtres simples, pour permettre à l'équipe
EMC Helpline d'explorer les signalements sans avoir à relire du code.

## 2. Lancer le tableau de bord

Depuis le dossier du projet, environnement virtuel activé :

```powershell
streamlit run src/app.py
```

Une page s'ouvre automatiquement dans le navigateur par défaut
(en général `http://localhost:8501`). Pour arrêter l'application, retourner
au terminal et faire `Ctrl+C`.

## 3. Architecture de l'application

`app.py` ne recalcule rien : il **importe** les fonctions déjà écrites et
validées au Jalon 2 depuis `kpi_dashboard.py` (chargement, nettoyage, calcul
des 5 KPI, génération des graphiques). Cela évite de dupliquer la logique
métier à deux endroits différents — si un calcul doit être corrigé un jour,
il ne l'est qu'une fois, dans `kpi_dashboard.py`.

```
src/
├── kpi_dashboard.py   ← logique métier (Jalon 2, inchangée)
└── app.py             ← interface Streamlit (Jalon 3, assemble le tout)
```

## 4. Filtres disponibles

| Filtre | Emplacement | Effet |
|---|---|---|
| Période (par mois) | Barre latérale gauche | Restreint les signalements à un intervalle de mois |
| Plateforme(s) | Barre latérale gauche | Ne garde que les signalements des plateformes cochées |

Les deux filtres se combinent. Tous les indicateurs et graphiques de la page
se recalculent automatiquement dès qu'un filtre change — aucune action
supplémentaire n'est nécessaire.

## 5. Organisation de la page

- **En-tête** : 4 indicateurs-clés résumant la sélection actuelle (nombre de
  signalements, taux d'accompagnement, mois le plus actif, nombre de
  plateformes sélectionnées).
- **4 onglets**, reprenant les 7 graphiques du Jalon 2 :
  1. *Volume & Types* → KPI 1 (courbe mensuelle) et KPI 2 (types de
     cyberharcèlement)
  2. *Plateformes* → KPI 3 (répartition par plateforme)
  3. *Accompagnement* → KPI 4 (jauge globale) et KPI 4 détail (types de
     demandes)
  4. *Profil des victimes* → KPI 5a (genre) et KPI 5b (âge)

Chaque graphique est accompagné d'une courte phrase (sous le graphique)
qui se met à jour selon les filtres actifs (ex. type de cyberharcèlement le
plus fréquent sur la période sélectionnée).

## 6. Cas particuliers gérés

- Si les filtres ne renvoient **aucun signalement**, un message d'avertissement
  s'affiche à la place du tableau de bord plutôt qu'une page vide ou une erreur.
- Si aucune demande d'accompagnement n'existe sur la période filtrée, le
  graphique de détail est remplacé par un message explicite plutôt que par
  un graphique vide.
- Idem pour le profil genre/âge si aucune donnée n'est renseignée sur la
  période filtrée.

## 7. Limites connues / pistes d'évolution

- Les filtres portent sur le mois et la plateforme ; un filtre par type de
  cyberharcèlement pourrait être ajouté si utile à l'usage.
- Les données sont chargées une seule fois au démarrage (mise en cache via
  `@st.cache_data`) : si le fichier Excel source est modifié pendant que
  l'application tourne, il faut recharger la page (touche `R`) pour que le
  changement soit pris en compte.
