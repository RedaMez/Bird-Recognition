#!/bin/bash

echo "Réinitialisation du projet"

# Crée le dossier 'resources/extracted_birds_to_validate/' s'il n'existe pas
mkdir -p resources/extracted_birds_to_validate

# Parcourt les sous-dossiers de resources/results/
for dir in resources/results/*/
do
    # Active le nullglob pour éviter l'erreur si aucun fichier .png n'est trouvé
    shopt -s nullglob
    
    # Parcourt les sous-sous-dossiers
    for sub_dir in "$dir"*/
    do
        # Déplace toutes les images présentes dans le sous-sous-dossier vers 'resources/extracted_birds_to_validate/'
        mv "$sub_dir"*.png resources/extracted_birds_to_validate/ 2>/dev/null
    done
    
    # Déplace toutes les images présentes dans le sous-dossier vers 'resources/extracted_birds_to_validate/'
    mv "$dir"*.png resources/extracted_birds_to_validate/ 2>/dev/null

    # Supprime le sous-dossier s'il est vide
    rm -r "$dir" 2>/dev/null
done

echo "Projet réinitialisé. Toutes les images ont été déplacées dans leur dossier initial, et les sous-dossiers dans 'results' ont été supprimés."
