# Guide Complet d'Utilisation de l'API Tickets

## 🔐 Authentification

### Obtenir un Token JWT

```bash
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@supnum.mr",
    "password": "testpass123"
  }'
```

**Réponse:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

Utiliser le token `access` dans toutes les requêtes:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" http://localhost:8000/api/tickets/
```

## 📌 Points Clés

- **Tous les timestamps** sont en UTC (format ISO 8601)
- **Montant** en MRU: 5 MRU par jour
- **QR Code** fourni en base64 pour l'affichage immédiat
- **Dates** au format YYYY-MM-DD
- **Pagination** avec limit=10 par défaut

## 👨‍🎓 API Étudiants

### 1. Créer une Demande de Tickets

```bash
curl -X POST http://localhost:8000/api/tickets/requests/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2026-01-20",
    "end_date": "2026-01-25"
  }'
```

**Réponse (201 Created):**
```json
{
  "id": 1,
  "student": 1,
  "student_name": "John Doe",
  "start_date": "2026-01-20",
  "end_date": "2026-01-25",
  "number_of_days": 6,
  "total_amount": "30.00",
  "status": "PENDING",
  "payment_reference": "",
  "payment_screenshot": null,
  "created_at": "2026-01-15T10:30:00Z",
  "approved_at": null,
  "rejected_at": null
}
```

**Erreurs possibles:**
- 400: Dates invalides (fin < début)
- 400: Demandes qui se chevauchent
- 401: Non authentifié
- 403: Pas étudiant

### 2. Consulter Mes Demandes

```bash
curl -X GET http://localhost:8000/api/tickets/requests/my_requests/ \
  -H "Authorization: Bearer TOKEN"
```

**Réponse:**
```json
[
  {
    "id": 1,
    "student_name": "John Doe",
    "start_date": "2026-01-20",
    "end_date": "2026-01-25",
    "number_of_days": 6,
    "total_amount": "30.00",
    "status": "PENDING",
    "created_at": "2026-01-15T10:30:00Z"
  }
]
```

### 3. Consulter Mes Statistiques

```bash
curl -X GET http://localhost:8000/api/tickets/requests/statistics/ \
  -H "Authorization: Bearer TOKEN"
```

**Réponse:**
```json
{
  "total_requests": 5,
  "approved_requests": 3,
  "rejected_requests": 0,
  "valid_tickets": 8,
  "used_tickets": 5,
  "expired_tickets": 0,
  "total_spent": 40.00
}
```

### 4. Lister Mes Tickets

```bash
curl -X GET http://localhost:8000/api/tickets/tickets/my_tickets/ \
  -H "Authorization: Bearer TOKEN"
```

**Réponse:**
```json
[
  {
    "id": 1,
    "request": 1,
    "date": "2026-01-20",
    "qr_token": "550e8400-e29b-41d4-a716-446655440000",
    "status": "VALID",
    "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUg...",
    "student_name": "John Doe",
    "used_at": null,
    "created_at": "2026-01-15T11:00:00Z"
  }
]
```

### 5. Télécharger/Afficher le QR Code

```bash
# Le QR code est fourni en base64 dans le champ "qr_code"
# Vous pouvez:
# 1. L'afficher directement dans une image HTML
# 2. Le sauvegarder comme fichier PNG
# 3. L'envoyer à une imprimante
```

## 👨‍💼 API Admin

### 1. Consulter Les Demandes en Attente

```bash
curl -X GET http://localhost:8000/api/tickets/admin/requests/pending_requests/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 2. Approuver Une Demande

```bash
curl -X POST http://localhost:8000/api/tickets/admin/requests/1/approve/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Réponse:**
```json
{
  "status": "approved",
  "message": "Request approved and 6 tickets created"
}
```

**Effet:**
- Statut change à APPROVED
- 6 tickets sont créés automatiquement
- Étudiants reçoivent les tickets

### 3. Rejeter Une Demande

```bash
curl -X POST http://localhost:8000/api/tickets/admin/requests/1/reject/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 4. Statistiques Globales

```bash
# Par jour
curl -X GET "http://localhost:8000/api/tickets/admin/requests/statistics/?period=day" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Par semaine
curl -X GET "http://localhost:8000/api/tickets/admin/requests/statistics/?period=week" \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Par mois
curl -X GET "http://localhost:8000/api/tickets/admin/requests/statistics/?period=month" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Réponse:**
```json
{
  "total_requests": 15,
  "approved_requests": 12,
  "rejected_requests": 2,
  "total_revenue": 120.00,
  "tickets_used": 45,
  "tickets_valid": 20,
  "tickets_expired": 5,
  "period": "day",
  "start_date": "2026-01-15"
}
```

### 5. Statistiques par Étudiant

```bash
curl -X GET http://localhost:8000/api/tickets/admin/requests/student_statistics/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Réponse:**
```json
[
  {
    "student": 1,
    "total_requests": 5,
    "total_amount": 50.00,
    "approved": 4,
    "rejected": 1
  },
  {
    "student": 2,
    "total_requests": 3,
    "total_amount": 30.00,
    "approved": 3,
    "rejected": 0
  }
]
```

### 6. Revenu Journalier

```bash
# Dernier 30 jours (par défaut)
curl -X GET http://localhost:8000/api/tickets/admin/requests/daily_revenue/ \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Dernier 7 jours
curl -X GET "http://localhost:8000/api/tickets/admin/requests/daily_revenue/?days=7" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Réponse:**
```json
[
  {
    "created_at__date": "2026-01-10",
    "revenue": 50.00,
    "count": 2
  },
  {
    "created_at__date": "2026-01-11",
    "revenue": 75.00,
    "count": 3
  }
]
```

### 7. Tickets du Jour

```bash
curl -X GET http://localhost:8000/api/tickets/admin/tickets/today_tickets/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 8. Tickets Utilisés Aujourd'hui

```bash
curl -X GET http://localhost:8000/api/tickets/admin/tickets/used_today/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 9. Tickets par Plage de Dates

```bash
curl -X GET "http://localhost:8000/api/tickets/admin/tickets/by_date_range/?start_date=2026-01-10&end_date=2026-01-15" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 10. Tickets d'un Étudiant

```bash
curl -X GET "http://localhost:8000/api/tickets/admin/tickets/by_student/?student_id=1" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 11. Gestion des Paiements

#### Lister les paiements en attente
```bash
curl -X GET http://localhost:8000/api/tickets/admin/payments/pending_payments/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### Vérifier un paiement
```bash
curl -X POST http://localhost:8000/api/tickets/admin/payments/1/verify/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Effet:**
- Statut du paiement → VERIFIED
- Demande de tickets → PAID

#### Rejeter un paiement
```bash
curl -X POST http://localhost:8000/api/tickets/admin/payments/1/reject/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 12. Dashboard Overview

```bash
curl -X GET http://localhost:8000/api/tickets/admin/dashboard/overview/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Réponse:**
```json
{
  "total_students": 45,
  "pending_requests": 5,
  "approved_requests": 120,
  "today_requests": 3,
  "pending_payments": 2,
  "verified_payments": 118,
  "today_revenue": 30.00,
  "today_tickets_used": 8,
  "today_tickets_valid": 12
}
```

### 13. Statistiques Hebdomadaires

```bash
curl -X GET http://localhost:8000/api/tickets/admin/dashboard/weekly_statistics/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 14. Statistiques Mensuelles

```bash
curl -X GET http://localhost:8000/api/tickets/admin/dashboard/monthly_statistics/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### 15. Gestion des Utilisateurs

#### Lister tous les utilisateurs
```bash
curl -X GET http://localhost:8000/api/tickets/admin/dashboard/users_management/ \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### Lister par rôle
```bash
curl -X GET "http://localhost:8000/api/tickets/admin/dashboard/users_management/?role=STUDENT" \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

#### Désactiver un utilisateur
```bash
curl -X POST http://localhost:8000/api/tickets/admin/dashboard/deactivate_user/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 5}'
```

#### Activer un utilisateur
```bash
curl -X POST http://localhost:8000/api/tickets/admin/dashboard/activate_user/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 5}'
```

## 👨‍🍳 API Agent de Restauration

### 1. Scanner Un Ticket

```bash
curl -X POST http://localhost:8000/api/tickets/tickets/1/scan/ \
  -H "Authorization: Bearer AGENT_TOKEN"
```

**Réponse (ticket valide):**
```json
{
  "valid": true,
  "message": "Valid",
  "status": "USED",
  "student": "John Doe",
  "used_at": "2026-01-20T12:30:00Z"
}
```

**Réponse (ticket déjà utilisé):**
```json
{
  "valid": false,
  "message": "Already used",
  "status": "USED"
}
```

**Réponse (ticket expiré):**
```json
{
  "valid": false,
  "message": "Expired",
  "status": "EXPIRED"
}
```

## 📋 Codes de Statut HTTP

| Code | Signification |
|------|---------------|
| 200 | OK - Succès |
| 201 | Created - Ressource créée |
| 400 | Bad Request - Requête invalide |
| 401 | Unauthorized - Non authentifié |
| 403 | Forbidden - Permission refusée |
| 404 | Not Found - Ressource non trouvée |
| 500 | Server Error - Erreur serveur |

## 🔍 Filtrage et Pagination

### Pagination
```bash
curl -X GET "http://localhost:8000/api/tickets/requests/?limit=5&offset=10" \
  -H "Authorization: Bearer TOKEN"
```

### Tri
```bash
curl -X GET "http://localhost:8000/api/tickets/requests/?ordering=-created_at" \
  -H "Authorization: Bearer TOKEN"
```

## ⚠️ Erreurs Courantes et Corrections

### 401 Unauthorized
```bash
# Vérifier que vous utilisez le bon token
# Vérifier que le token n'a pas expiré
```

### 403 Forbidden  
```bash
# Vérifier votre rôle (STUDENT, ADMIN, AGENT)
# Vérifier que vous accédez au bon endpoint
```

### 400 Bad Request
```bash
# Vérifier le format des données JSON
# Vérifier les formats de dates (YYYY-MM-DD)
# Vérifier que tous les champs requis sont fournis
```

## 💡 Bonnes Pratiques

1. **Toujours utiliser HTTPS** en production
2. **Stocker les tokens** de manière sécurisée
3. **Utiliser des timeouts** sur les requêtes
4. **Implémenter la pagination** pour les listes
5. **Logger les erreurs** pour le débogage
6. **Valider les données** côté client
7. **Gérer les tokens expirés** avec refresh

## 📚 Ressources Additionnelles

- Documentation OAuth2/JWT: https://tools.ietf.org/html/rfc6749
- Django REST Framework: https://www.django-rest-framework.org/
- Format ISO 8601 dates: https://www.iso.org/iso-8601-date-and-time-format.html

