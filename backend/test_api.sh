#!/bin/bash
# Script d'exemples de requêtes cURL pour tester l'API UniTicket

BASE_URL="http://127.0.0.1:8000"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Tests API UniTicket ===${NC}\n"

# ============================================
# 1. AUTHENTICATION
# ============================================

echo -e "${YELLOW}[1] Authentification${NC}\n"

echo "Connexion d'un étudiant..."
STUDENT_TOKEN=$(curl -s -X POST $BASE_URL/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "student@supnum.mr", "password": "testpass123"}' \
  | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$STUDENT_TOKEN" ]; then
  echo -e "${RED}✗ Erreur: Token étudiant non obtenu${NC}"
else
  echo -e "${GREEN}✓ Token étudiant: ${STUDENT_TOKEN:0:20}...${NC}\n"
fi

echo "Connexion d'un admin..."
ADMIN_TOKEN=$(curl -s -X POST $BASE_URL/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@supnum.mr", "password": "adminpass123"}' \
  | grep -o '"access":"[^"]*' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
  echo -e "${RED}✗ Erreur: Token admin non obtenu${NC}"
else
  echo -e "${GREEN}✓ Token admin: ${ADMIN_TOKEN:0:20}...${NC}\n"
fi

# ============================================
# 2. CRÉER UNE DEMANDE (ÉTUDIANT)
# ============================================

echo -e "${YELLOW}[2] Créer une demande de tickets (Étudiant)${NC}\n"

START_DATE=$(date -d "+1 day" +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d)
END_DATE=$(date -d "+5 day" +%Y-%m-%d 2>/dev/null || date -v+5d +%Y-%m-%d)

echo "Dates: $START_DATE à $END_DATE"
REQUEST_RESPONSE=$(curl -s -X POST $BASE_URL/api/tickets/requests/ \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"start_date\": \"$START_DATE\", \"end_date\": \"$END_DATE\"}")

REQUEST_ID=$(echo $REQUEST_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$REQUEST_ID" ]; then
  echo -e "${RED}✗ Erreur lors de la création de la demande${NC}"
  echo "Réponse: $REQUEST_RESPONSE"
else
  echo -e "${GREEN}✓ Demande créée avec ID: $REQUEST_ID${NC}"
  echo "Réponse complète:"
  echo $REQUEST_RESPONSE | python -m json.tool 2>/dev/null || echo $REQUEST_RESPONSE
  echo ""
fi

# ============================================
# 3. LISTER LES DEMANDES (ÉTUDIANT)
# ============================================

echo -e "${YELLOW}[3] Lister mes demandes (Étudiant)${NC}\n"

curl -s -X GET $BASE_URL/api/tickets/requests/my_requests/ \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python -m json.tool 2>/dev/null

echo ""

# ============================================
# 4. CONSULTER LES DEMANDES EN ATTENTE (ADMIN)
# ============================================

echo -e "${YELLOW}[4] Consulter les demandes en attente (Admin)${NC}\n"

curl -s -X GET $BASE_URL/api/tickets/admin/requests/pending_requests/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool 2>/dev/null

echo ""

# ============================================
# 5. APPROUVER UNE DEMANDE (ADMIN)
# ============================================

if [ ! -z "$REQUEST_ID" ]; then
  echo -e "${YELLOW}[5] Approuver une demande (Admin)${NC}\n"
  
  curl -s -X POST $BASE_URL/api/tickets/admin/requests/$REQUEST_ID/approve/ \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" | python -m json.tool 2>/dev/null
  
  echo ""
fi

# ============================================
# 6. CONSULTER LES STATISTIQUES (ADMIN)
# ============================================

echo -e "${YELLOW}[6] Consulter les statistiques (Admin)${NC}\n"

curl -s -X GET "$BASE_URL/api/tickets/admin/requests/statistics/?period=day" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool 2>/dev/null

echo ""

# ============================================
# 7. DASHBOARD OVERVIEW (ADMIN)
# ============================================

echo -e "${YELLOW}[7] Vue d'ensemble du dashboard (Admin)${NC}\n"

curl -s -X GET $BASE_URL/api/tickets/admin/dashboard/overview/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool 2>/dev/null

echo ""

# ============================================
# 8. LISTER LES TICKETS DE L'ÉTUDIANT
# ============================================

echo -e "${YELLOW}[8] Lister mes tickets (Étudiant)${NC}\n"

curl -s -X GET $BASE_URL/api/tickets/tickets/my_tickets/ \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python -m json.tool 2>/dev/null

echo ""

# ============================================
# 9. CONSULTER TOUS LES UTILISATEURS (ADMIN)
# ============================================

echo -e "${YELLOW}[9] Consulter la gestion des utilisateurs (Admin)${NC}\n"

curl -s -X GET $BASE_URL/api/tickets/admin/dashboard/users_management/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" | python -m json.tool 2>/dev/null

echo ""

echo -e "${YELLOW}=== Fin des tests ===${NC}"
