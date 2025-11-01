# Qui utilise mon appli? - Challenge Kaggle

Ce projet vise à prédire l'utilisateur d'un logiciel à partir de traces d'utilisation. Il s'agit d'une compétition de machine learning où l'objectif est de classifier les sessions utilisateurs en fonction de leurs comportements.

## 📋 Table des matières

- [Description du projet](#description-du-projet)
- [Prérequis](#prérequis)
- [Installation](#installation)

## 🎯 Description du projet

Le but de la compétition est de prédire l'utilisateur d'un logiciel à partir d'un jeu de traces d'utilisation. Les données contiennent des sessions avec :
- Identifiant utilisateur
- Navigateur utilisé
- Séquence d'actions effectuées
- Timestamps des actions
- Metadata (documents consultés, services utilisés, configurations)

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/antara-walid/Qui-utilise-mon-appli-Challenge.git
cd Qui-utilise-mon-appli-Challenge
```

### 2. Créer un environnement virtuel

#### Avec venv

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Lancer Jupyter Notebook

```bash
jupyter notebook
```



