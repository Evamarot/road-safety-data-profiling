# 🚗 Road Safety Data Profiling & Quality Audit

Ce projet implémente un pipeline de Data Engineering basé sur l'**Architecture Medallion** et un tableau de bord interactif de **Data Profiling** pour analyser la qualité des données de la Sécurité Routière française (Base BAAC).

## 📋 Description du Projet

L'objectif de ce projet est de démontrer la maîtrise du cycle de vie de la donnée : de l'ingestion des données brutes à leur modélisation pour l'analyse décisionnelle (Business Intelligence), en passant par un audit rigoureux de la qualité.

Le projet se divise en deux parties majeures :
1. **Pipeline ETL (Notebook) :** Nettoyage, standardisation et modélisation spatiale en étoile (Star Schema).
2. **Dashboard de Profilage (Streamlit) :** Une application interactive permettant d'auditer les données brutes (Bronze) et de justifier les choix de nettoyage (Silver).

## 🏗️ Architecture Medallion

Le projet respecte les standards de l'industrie avec une séparation stricte des couches de données :

* **🥉 Couche Bronze (Raw) :** Données brutes issues de `data.gouv.fr` (Caractéristiques, Lieux, Véhicules, Usagers).
* **🥈 Couche Silver (Cleaned) :** Données nettoyées (gestion des valeurs manquantes, correction des types, filtrage du bruit géographique et des valeurs aberrantes).
* **🥇 Couche Gold (Business-Ready) :** Modèle en étoile (Star Schema) optimisé pour Power BI, isolant la dimension spatiale (`dim_lieux`) de la table de faits (`fact_accidents`).

## ✨ Fonctionnalités du Dashboard (Streamlit)

Le tableau de bord interactif répond aux 4 axes majeurs de l'audit de qualité des données :

* **A. Dataset Structure :** Inventaire des colonnes, types de données et signification métier des 4 tables relationnelles.
* **B. Missing Values & Completeness :** Détection des valeurs manquantes critiques (ex: coordonnées GPS `lat`/`long`) et stratégies d'imputation.
* **C. Consistency & Validity Checks :** Détection des anomalies via graphiques interactifs (bruit géographique, vitesses impossibles, âges aberrants).
* **D. Data Quality Summary :** Rapport global d'impact expliquant les risques pour l'analytique BI (bris d'intégrité référentielle, biais statistiques) si les données n'étaient pas traitées.

## 🛠️ Technologies Utilisées

* **Python 3.10+**
* **Pandas :** Manipulation et transformation des données (ETL).
* **Streamlit :** Création de l'interface utilisateur interactive.
* **Plotly :** Visualisations de données dynamiques.
* **YData-Profiling :** Génération de rapports automatisés d'exploration des données.

## 🚀 Installation et Déploiement Local

### 1. Cloner le dépôt
```bash
git clone [https://github.com/TonPseudo/road-safety-data-profiling.git](https://github.com/TonPseudo/road-safety-data-profiling.git)
cd road-safety-data-profiling
