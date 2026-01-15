#!/bin/bash

# 📋 SCRIPT DE DÉMARRAGE COMPLET - UniTicket Module Tickets
# Ce script vous guidera à travers tous les étapes de configuration

echo -e "\033[1;36m"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║          🎉 UniTicket Module Tickets - Démarrage              ║"
echo "║                                                                ║"
echo "║                   STATUS: ✅ PRÊT À FONCTIONNER               ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "\033[0m\n"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📍 ÉTAPE 0: Vérifications préalables${NC}\n"

# Vérifier Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python n'est pas installé${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python trouvé:${NC} $(python --version)"

# Vérifier pip
if ! command -v pip &> /dev/null; then
    echo -e "${RED}❌ pip n'est pas installé${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip trouvé${NC}"

# Vérifier MySQL
echo -e "\n${YELLOW}⚠️  IMPORTANT: MySQL doit être en cours d'exécution!${NC}"
echo "   Sur Windows: Services → Démarrer MySQL"
echo "   Ou: XAMPP → Cliquer Start pour MySQL"
echo "   Ou: Cmd → net start MySQL"
echo ""
read -p "Appuyez sur Entrée quand MySQL est lancé..."

echo -e "\n${BLUE}📍 ÉTAPE 1: Naviguer vers le dossier backend${NC}\n"

cd backend || exit 1
echo -e "${GREEN}✓ Dossier courant:${NC} $(pwd)"

echo -e "\n${BLUE}📍 ÉTAPE 2: Installer les dépendances${NC}\n"

echo "Installation en cours... (cela peut prendre quelques minutes)"
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dépendances installées${NC}"
else
    echo -e "${RED}❌ Erreur lors de l'installation${NC}"
    exit 1
fi

echo -e "\n${BLUE}📍 ÉTAPE 3: Exécuter le setup interactif${NC}\n"

python setup.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Setup terminé${NC}"
else
    echo -e "${RED}❌ Erreur lors du setup${NC}"
    exit 1
fi

echo -e "\n${BLUE}📍 ÉTAPE 4: Vérifier les migrations${NC}\n"

python manage.py showmigrations | grep tickets
echo -e "${GREEN}✓ Migrations vérifiées${NC}"

echo -e "\n${BLUE}📍 ÉTAPE 5: Informations utiles${NC}\n"

echo -e "${YELLOW}Fichiers de documentation:${NC}"
echo "  📄 GETTING_STARTED.md      - Guide de démarrage"
echo "  📄 API_GUIDE.md           - Guide complet d'utilisation"
echo "  📄 ARCHITECTURE.md        - Architecture du système"
echo "  📄 TROUBLESHOOTING.md     - Guide de dépannage"

echo -e "\n${YELLOW}Commandes utiles:${NC}"
echo "  python manage.py runserver        - Démarrer le serveur"
echo "  python manage.py test tickets     - Lancer les tests"
echo "  bash test_api.sh                  - Tester l'API"
echo "  python manage.py createsuperuser  - Créer un admin"

echo -e "\n${BLUE}📍 ÉTAPE 6: Options suivantes${NC}\n"

echo "Que voulez-vous faire maintenant?"
echo ""
echo "1) Démarrer le serveur Django"
echo "2) Lancer les tests de l'API"
echo "3) Accéder à l'interface admin"
echo "4) Lire la documentation"
echo "5) Quitter"
echo ""

read -p "Choisissez (1-5): " choice

case $choice in
    1)
        echo -e "\n${YELLOW}Démarrage du serveur Django...${NC}\n"
        python manage.py runserver
        ;;
    2)
        echo -e "\n${YELLOW}Lancement des tests...${NC}\n"
        bash test_api.sh
        ;;
    3)
        echo -e "\n${YELLOW}Démarrage du serveur pour l'admin...${NC}"
        echo "L'interface admin est à: http://localhost:8000/admin/"
        echo ""
        python manage.py runserver
        ;;
    4)
        echo -e "\n${YELLOW}Fichiers de documentation:${NC}\n"
        echo "Consultez les fichiers .md pour plus d'informations"
        ;;
    5)
        echo -e "\n${GREEN}À bientôt!${NC}\n"
        exit 0
        ;;
    *)
        echo -e "\n${RED}Choix invalide${NC}\n"
        exit 1
        ;;
esac

echo -e "\n${GREEN}✅ Configuration terminée avec succès!${NC}\n"
