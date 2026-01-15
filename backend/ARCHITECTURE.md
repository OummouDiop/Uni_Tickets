# Architecture Complète du Module Tickets

## 📋 Vue d'ensemble

```
Backend Django
├── Authentification (JWT)
├── Module Accounts (Utilisateurs)
└── Module Tickets (Gestion de tickets de restauration)
    ├── Étudiants
    ├── Administrateurs
    └── Agents de restauration
```

## 🔄 Flux de Travail

### 1️⃣ Étudiant demande des tickets
```
Étudiant remplit formulaire
    ↓
TicketRequest créée (PENDING)
    ↓
Admin vérifie le paiement
    ↓
Si vérifié : TicketRequest → PAID
    ↓
Admin approuve la demande
    ↓
TicketRequest → APPROVED
Tickets individuels créés avec QR codes
    ↓
Étudiant télécharge/affiche ses tickets
```

### 2️⃣ Agent scanne les tickets
```
Agent scanne le QR code
    ↓
API vérifie le ticket
    ↓
Si valide et date correcte :
    Ticket → USED
    Sauvegarder timestamp + agent
    ↓
Réponse : "Valide - Bienvenue!"
```

### 3️⃣ Dashboard Admin
```
Admin accède au dashboard
    ↓
Voit : Demandes en attente, Paiements à vérifier
    ↓
Valide paiements (PaymentLog)
    ↓
Approuve demandes (génère tickets)
    ↓
Consulte statistiques :
  - Revenu par jour/semaine/mois
  - Tickets utilisés
  - Étudiants actifs
```

## 📊 Modèles de Données

### TicketRequest (Demande de Ticket)
```
┌─────────────────────────┐
│   TicketRequest         │
├─────────────────────────┤
│ • id (PK)               │
│ • student (FK→User)     │
│ • start_date            │
│ • end_date              │
│ • number_of_days (auto) │
│ • total_amount (auto)   │
│ • status (PENDING...)   │
│ • payment_reference     │
│ • payment_screenshot    │
│ • created_at            │
│ • approved_at           │
│ • rejected_at           │
└─────────────────────────┘
         ↓ 1:M
    ┌─────────────┐
    │   Ticket    │
    ├─────────────┤
    │ • id (PK)   │
    │ • request   │
    │ • date      │
    │ • qr_token  │
    │ • status    │
    │ • used_at   │
    │ • scanned_by│
    └─────────────┘
```

### PaymentLog (Paiements)
```
┌─────────────────────────┐
│   PaymentLog            │
├─────────────────────────┤
│ • id (PK)               │
│ • ticket_request (1:1)  │
│ • reference             │
│ • screenshot            │
│ • status (VERIFIED...)  │
│ • verified_by           │
│ • verified_at           │
│ • created_at            │
│ • notes                 │
└─────────────────────────┘
```

## 🔗 Endpoints API

### Authentication
```
POST /api/accounts/token/          - Obtenir JWT token
POST /api/accounts/register/        - S'inscrire
POST /api/accounts/login/           - Se connecter
```

### Student Endpoints
```
GET    /api/tickets/requests/
POST   /api/tickets/requests/                    - Créer demande
GET    /api/tickets/requests/{id}/
PATCH  /api/tickets/requests/{id}/               - Mettre à jour
GET    /api/tickets/requests/my_requests/        - Mes demandes
GET    /api/tickets/requests/statistics/         - Mes stats
GET    /api/tickets/tickets/
GET    /api/tickets/tickets/my_tickets/          - Mes tickets
```

### Admin Endpoints
```
# Requests Management
GET    /api/tickets/admin/requests/
GET    /api/tickets/admin/requests/pending_requests/
GET    /api/tickets/admin/requests/paid_requests/
POST   /api/tickets/admin/requests/{id}/approve/
POST   /api/tickets/admin/requests/{id}/reject/
GET    /api/tickets/admin/requests/statistics/?period=day
GET    /api/tickets/admin/requests/student_statistics/
GET    /api/tickets/admin/requests/daily_revenue/?days=30

# Tickets Management
GET    /api/tickets/admin/tickets/
GET    /api/tickets/admin/tickets/today_tickets/
GET    /api/tickets/admin/tickets/used_today/
GET    /api/tickets/admin/tickets/by_date_range/?start_date=2026-01-15&end_date=2026-01-20
GET    /api/tickets/admin/tickets/by_student/?student_id=1

# Payment Management
GET    /api/tickets/admin/payments/
GET    /api/tickets/admin/payments/pending_payments/
POST   /api/tickets/admin/payments/{id}/verify/
POST   /api/tickets/admin/payments/{id}/reject/

# Dashboard
GET    /api/tickets/admin/dashboard/overview/
GET    /api/tickets/admin/dashboard/weekly_statistics/
GET    /api/tickets/admin/dashboard/monthly_statistics/
GET    /api/tickets/admin/dashboard/users_management/?role=STUDENT
POST   /api/tickets/admin/dashboard/deactivate_user/
POST   /api/tickets/admin/dashboard/activate_user/
```

### Agent Endpoints
```
POST   /api/tickets/tickets/{id}/scan/   - Scanner un ticket
```

## 🔐 Permissions

```
┌─────────────┬──────────┬──────────┬────────────┐
│ Endpoint    │ Student  │ Admin    │ Agent      │
├─────────────┼──────────┼──────────┼────────────┤
│ /requests   │ ✅ Own   │ ✅ All   │ ❌         │
│ /tickets    │ ✅ Own   │ ✅ All   │ ✅ Read    │
│ /admin/*    │ ❌       │ ✅       │ ❌         │
│ /scan       │ ❌       │ ❌       │ ✅         │
└─────────────┴──────────┴──────────┴────────────┘
```

## 📈 Calculs Automatiques

### Nombre de jours
```
number_of_days = (end_date - start_date).days + 1
```

### Montant total
```
total_amount = number_of_days * 5 MRU
Exemple: 6 jours = 30 MRU
```

### QR Code
```
Généré automatiquement : UUID4
Exemple: 550e8400-e29b-41d4-a716-446655440000
Encodé en image PNG en base64 pour l'API
```

## ⏰ Statuts des Tickets

```
VALID → Ticket peut être utilisé aujourd'hui
USED  → Ticket a été utilisé
EXPIRED → Date passée, pas utilisé
```

## 💰 Statuts des Demandes

```
PENDING  → En attente de paiement
PAID     → Paiement vérifié
APPROVED → Tickets générés et disponibles
REJECTED → Demande refusée
```

## 📸 Statuts des Paiements

```
PENDING  → En attente de vérification admin
VERIFIED → Paiement accepté
FAILED   → Paiement rejeté
```

## 🗄️ Base de Données

### Moteur
- MySQL 5.7+ ou MariaDB 10.3+

### Tables
```
accounts_user
├── id (PK)
├── email (UNIQUE)
├── first_name
├── last_name
├── password
├── role (STUDENT, ADMIN, AGENT)
├── is_active
└── date_joined

tickets_ticketrequest
├── id (PK)
├── student_id (FK→accounts_user)
├── start_date
├── end_date
├── number_of_days
├── total_amount
├── status
├── payment_reference
├── payment_screenshot
└── created_at

tickets_ticket
├── id (PK)
├── request_id (FK→tickets_ticketrequest)
├── date
├── qr_token (UNIQUE, INDEX)
├── status
├── used_at
├── scanned_by_id (FK→accounts_user)
└── created_at

tickets_paymentlog
├── id (PK)
├── ticket_request_id (1:1 FK→tickets_ticketrequest)
├── reference (UNIQUE)
├── screenshot
├── status
├── verified_by_id (FK→accounts_user)
├── verified_at
└── created_at
```

## 🧪 Exemple d'Utilisation

### 1. Étudiant crée une demande
```bash
curl -X POST http://localhost:8000/api/tickets/requests/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-01-20",
    "end_date": "2026-01-25"
  }'

# Réponse:
{
  "id": 1,
  "student": 1,
  "start_date": "2026-01-20",
  "end_date": "2026-01-25",
  "number_of_days": 6,
  "total_amount": 30.00,
  "status": "PENDING",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### 2. Admin approuve la demande
```bash
curl -X POST http://localhost:8000/api/tickets/admin/requests/1/approve/ \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Réponse:
{
  "status": "approved",
  "message": "Request approved and 6 tickets created"
}
```

### 3. Agent scanne un ticket
```bash
curl -X POST http://localhost:8000/api/tickets/tickets/1/scan/ \
  -H "Authorization: Bearer $AGENT_TOKEN"

# Réponse:
{
  "valid": true,
  "message": "Valid",
  "status": "USED",
  "student": "John Doe",
  "used_at": "2026-01-20T12:00:00Z"
}
```

### 4. Admin consulte les statistiques du jour
```bash
curl -X GET "http://localhost:8000/api/tickets/admin/requests/statistics/?period=day" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Réponse:
{
  "total_requests": 5,
  "approved_requests": 3,
  "rejected_requests": 0,
  "total_revenue": 90.00,
  "tickets_used": 12,
  "tickets_valid": 8,
  "tickets_expired": 0,
  "period": "day",
  "start_date": "2026-01-15"
}
```

## 📦 Dépendances Principales

```
Django==5.1
djangorestframework==3.15.1
djangorestframework-simplejwt==5.3.0
qrcode[pil]==7.4.2
Pillow==10.3.0
django-cors-headers==4.3.1
mysqlclient==2.2.4
```

