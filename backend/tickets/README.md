# Configuration du Système de Tickets UniTicket - Module Tickets

## 🎯 Résumé des Modifications

### 1. **Modèles de Données** (`models.py`)
- **TicketRequest** : Demandes de tickets avec gestion des statuts (PENDING, PAID, APPROVED, REJECTED)
- **Ticket** : Tickets individuels avec QR code unique et suivi d'utilisation
- **PaymentLog** : Suivi des paiements avec vérification par l'admin

### 2. **API REST**

#### Routes Étudiants :
```
GET    /api/tickets/requests/              - Lister mes demandes
POST   /api/tickets/requests/              - Créer une demande
GET    /api/tickets/requests/my_requests/  - Mes demandes
GET    /api/tickets/requests/statistics/   - Mes statistiques
GET    /api/tickets/tickets/               - Lister mes tickets
GET    /api/tickets/tickets/my_tickets/    - Mes tickets
POST   /api/tickets/tickets/{id}/scan/     - Scanner un ticket (agent)
```

#### Routes Admin :
```
# Demandes de Tickets
GET    /api/tickets/admin/requests/                    - Toutes les demandes
GET    /api/tickets/admin/requests/pending_requests/   - Demandes en attente
GET    /api/tickets/admin/requests/paid_requests/      - Demandes payées
POST   /api/tickets/admin/requests/{id}/approve/       - Approuver une demande
POST   /api/tickets/admin/requests/{id}/reject/        - Rejeter une demande
GET    /api/tickets/admin/requests/statistics/         - Statistiques globales
GET    /api/tickets/admin/requests/student_statistics/ - Statistiques par étudiant
GET    /api/tickets/admin/requests/daily_revenue/      - Revenu journalier

# Tickets
GET    /api/tickets/admin/tickets/              - Tous les tickets
GET    /api/tickets/admin/tickets/today_tickets/  - Tickets du jour
GET    /api/tickets/admin/tickets/used_today/     - Tickets utilisés aujourd'hui
GET    /api/tickets/admin/tickets/by_date_range/  - Tickets par plage de dates
GET    /api/tickets/admin/tickets/by_student/     - Tickets d'un étudiant

# Paiements
GET    /api/tickets/admin/payments/              - Tous les paiements
GET    /api/tickets/admin/payments/pending_payments/ - Paiements en attente
POST   /api/tickets/admin/payments/{id}/verify/  - Vérifier un paiement
POST   /api/tickets/admin/payments/{id}/reject/  - Rejeter un paiement

# Dashboard
GET    /api/tickets/admin/dashboard/overview/             - Aperçu général
GET    /api/tickets/admin/dashboard/weekly_statistics/    - Stats hebdomadaires
GET    /api/tickets/admin/dashboard/monthly_statistics/   - Stats mensuelles
GET    /api/tickets/admin/dashboard/users_management/     - Gestion des utilisateurs
POST   /api/tickets/admin/dashboard/deactivate_user/      - Désactiver un utilisateur
POST   /api/tickets/admin/dashboard/activate_user/        - Activer un utilisateur
```

### 3. **Interface Admin Django**
- Gestion complète des demandes de tickets
- Validation/Rejet des demandes
- Gestion des paiements avec vérification
- Actions groupées pour traiter plusieurs demandes

### 4. **Permissions par Rôle**
- `IsStudent` : Création de demandes, consultation de ses tickets
- `IsAdmin` : Gestion complète, statistiques, validation paiements
- `IsAgent` : Scanner les tickets, marquer comme utilisés

## 🚀 Installation et Démarrage

### Étape 1 : Installer les dépendances
```bash
cd backend
pip install -r requirements.txt
```

### Étape 2 : Démarrer MySQL
Assurez-vous que MySQL est en cours d'exécution:
- Sur Windows: Démarrer les services MySQL via Services ou XAMPP/WAMP
- Sur Linux: `sudo systemctl start mysql`

### Étape 3 : Créer la base de données (optionnel si elle existe)
```bash
mysql -u root -p
CREATE DATABASE uniticket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Étape 4 : Appliquer les migrations
```bash
python manage.py migrate
```

### Étape 5 : Créer un superadmin
```bash
python manage.py createsuperuser
```

### Étape 6 : Démarrer le serveur
```bash
python manage.py runserver
```

## 📊 Statistiques Disponibles

### Pour les Étudiants
- Nombre total de demandes
- Demandes approuvées/rejetées
- Tickets valides, utilisés, expirés
- Total dépensé

### Pour les Admins
- Nombre total d'étudiants
- Demandes en attente/approuvées
- Paiements vérifiés
- Revenu par jour/semaine/mois
- Tickets utilisés par jour
- Statistiques par étudiant

## 💾 Structure des Données

### TicketRequest
```json
{
  "id": 1,
  "student": 1,
  "start_date": "2026-01-20",
  "end_date": "2026-01-25",
  "number_of_days": 6,
  "total_amount": 30.00,
  "status": "APPROVED",
  "payment_reference": "PAY123456",
  "created_at": "2026-01-15T10:30:00Z"
}
```

### Ticket
```json
{
  "id": 1,
  "request": 1,
  "date": "2026-01-20",
  "qr_token": "550e8400-e29b-41d4-a716-446655440000",
  "status": "VALID",
  "qr_code": "data:image/png;base64,..."
}
```

### PaymentLog
```json
{
  "id": 1,
  "ticket_request": 1,
  "reference": "PAY123456",
  "status": "VERIFIED",
  "verified_by": 2,
  "verified_at": "2026-01-15T11:00:00Z"
}
```

## 🔐 Authentification

Les routes admin nécessitent:
1. Un utilisateur avec `role='ADMIN'`
2. Un token JWT valide

Exemple de requête:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/api/tickets/admin/requests/
```

## 📝 Fichiers Créés/Modifiés

```
tickets/
├── models.py              # Modèles TicketRequest, Ticket, PaymentLog
├── views.py               # Vues pour étudiants et agents
├── admin_views.py         # Vues pour admins (demandes, tickets)
├── admin_dashboard.py     # Dashboard et statistiques
├── serializers.py         # Sérializers pour API
├── permissions.py         # Classes de permissions personnalisées
├── admin.py               # Interface Django Admin
├── urls.py                # Routage des URLs
├── migrations/
│   ├── 0001_initial.py
│   └── 0002_*.py          # Migration PaymentLog
└── tests.py
```

## ⚙️ Configuration Settings

Ajouté à `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'tickets',
    ...
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'uniticket_db',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
```

## 🎯 Prochaines Étapes

1. **Développement Mobile** : Implémenter l'app mobile React/Expo
2. **Intégration Paiement** : Ajouter passerelle de paiement
3. **Email Notifications** : Envoyer notifications de validation
4. **Tests** : Créer test unitaires pour les modèles et API
5. **Déploiement** : Déployer sur serveur production

