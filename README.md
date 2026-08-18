# Tableau de bord décisionnel — EMC Helpline

Projet PFA 2026 · CMRPI · Fiche N°10
Stagiaire : NAFID IKRAM

## Architecture du projet

```
tableau_bord_emc_helpline/
├── data/
│   └── signalements-_1_.xlsx
├── src/
│   ├── kpi_dashboard.py       (Jalon 2 — logique métier : nettoyage, KPI, graphiques)
│   └── app.py                 (Jalon 3 — application Streamlit interactive)
├── requirements.txt
├── DOCUMENTATION_DASHBOARD.md (Jalon 3 — comment utiliser le tableau de bord)
└── README.md
```

## Installation sur ta machine (Windows, VS Code)

### 1. Créer le dossier du projet
Crée un dossier `tableau_bord_emc_helpline` là où tu veux ranger tes projets
(ex. `C:\Users\<toi>\Documents\PFA\`), puis à l'intérieur crée les
sous-dossiers `data` et `src` (clic droit → Nouveau dossier, ou dans le
terminal VS Code) :

```powershell
mkdir tableau_bord_emc_helpline
cd tableau_bord_emc_helpline
mkdir data
mkdir src
```

### 2. Placer les fichiers
- Télécharge `kpi_dashboard.py` depuis la conversation → mets-le dans `src/`
- Télécharge `requirements.txt` → mets-le à la racine du projet
- Copie ton fichier `signalements-_1_.xlsx` → mets-le dans `data/`

### 3. Ouvrir le dossier dans VS Code
`Fichier > Ouvrir un dossier...` → sélectionne `tableau_bord_emc_helpline`

### 4. Créer l'environnement virtuel (venv)
Dans le terminal intégré de VS Code (Terminal > Nouveau terminal) :

```powershell
python -m venv venv
```

Active-le :
```powershell
venv\Scripts\activate
```
(tu dois voir `(venv)` apparaître au début de la ligne du terminal)

Si VS Code te propose "Sélectionner cet environnement pour l'espace de
travail", clique **Oui**.

### 5. Installer les librairies
```powershell
pip install -r requirements.txt
```

### 6. Lancer le script (Jalon 2)
```powershell
python src/kpi_dashboard.py
```
Chaque graphique doit s'ouvrir automatiquement dans ton navigateur, et les
KPI s'afficher dans le terminal.

### 7. Lancer le tableau de bord interactif (Jalon 3)
```powershell
streamlit run src/app.py
```
Une page s'ouvre automatiquement dans le navigateur, avec les 7 graphiques
organisés en onglets et 2 filtres (période, plateforme). Voir
`DOCUMENTATION_DASHBOARD.md` pour le détail de son fonctionnement.
Pour arrêter l'application : `Ctrl+C` dans le terminal.

## Notes
- Le dossier `venv/` ne doit jamais être envoyé par email/USB ni mis sur
  GitHub — il est propre à chaque machine (ajoute-le à un `.gitignore` si
  tu utilises Git).
- Si tu changes de fichier de données, remplace simplement
  `data/signalements-_1_.xlsx` en gardant le même nom, ou modifie la
  variable `FICHIER_SOURCE` en haut de `kpi_dashboard.py`.
