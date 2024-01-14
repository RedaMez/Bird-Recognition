#!/bin/bash

BLUE_BOLD='\033[1;34m'
NC='\033[0m'

echo -e "\n${BLUE_BOLD}Installation des dépendances${NC}"
pip install -r requirements.txt

echo -e "\n${BLUE_BOLD}Lancement des tests unitaires${NC}"
python3 -m unittest discover tests/

echo -e "\n${BLUE_BOLD}Execution du main${NC}"
python3 main.py
