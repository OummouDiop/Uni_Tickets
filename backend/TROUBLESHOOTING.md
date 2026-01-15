# Guide de Dépannage - Module Tickets

## 🔴 Erreurs Courantes et Solutions

### 1. Erreur: "Can't connect to server on 'localhost' (10061)"

**Cause:** MySQL n'est pas en cours d'exécution

**Solutions:**
```bash
# Sur Windows avec XAMPP
# 1. Ouvrir le panneau de contrôle XAMPP
# 2. Cliquer sur "Start" pour MySQL

# Sur Windows sans XAMPP (MySQL installé)
# Ouvrir Services Windows (services.msc)
# Chercher "MySQL" et cliquer sur "Démarrer"

# Sur Linux
sudo systemctl start mysql
sudo systemctl status mysql

# Sur macOS
brew services start mysql-community-server
```

### 2. Erreur: "ModuleNotFoundError: No module named 'qrcode'"

**Cause:** Les dépendances ne sont pas installées

**Solution:**
```bash
pip install -r requirements.txt
```

### 3. Erreur: "django.db.utils.OperationalError: (1049, "Unknown database")"

**Cause:** La base de données n'existe pas

**Solutions:**
```bash
# Option 1: Créer manuellement via MySQL
mysql -u root -p
CREATE DATABASE uniticket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Option 2: Utiliser le script setup
python setup.py
```

### 4. Erreur: "not null constraint failed"

**Cause:** Un champ requis n'a pas de valeur

**Solutions possibles:**
- Assurez-vous que `start_date` et `end_date` sont fournis
- Vérifiez que l'étudiant existe avant de créer une demande

```python
# Correct:
TicketRequest.objects.create(
    student=student,  # Doit être un objet User
    start_date='2026-01-20',  # Doit être fourni
    end_date='2026-01-25'      # Doit être fourni
)
```

### 5. Erreur: "UNIQUE constraint failed"

**Cause:** Une tentative de création d'enregistrement avec des valeurs dupliquées

**Solutions:**
- Vérifiez qu'il n'existe pas déjà un ticket pour cette date
- Pour QR codes, c'est automatique (UUID)

```python
# Vérifier avant de créer:
if not Ticket.objects.filter(request=request, date=date).exists():
    Ticket.objects.create(request=request, date=date)
```

### 6. Erreur 401: "Authentication credentials were not provided"

**Cause:** Pas de token JWT fourni

**Solutions:**
```bash
# 1. Obtenir un token:
curl -X POST http://localhost:8000/api/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "student@supnum.mr", "password": "testpass123"}'

# 2. Utiliser le token dans les requêtes:
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/tickets/requests/
```

### 7. Erreur 403: "You do not have permission to perform this action"

**Cause:** L'utilisateur n'a pas les permissions requises

**Solutions:**
- Vérifiez le rôle de l'utilisateur (STUDENT, ADMIN, AGENT)
- Consultez le tableau des permissions dans ARCHITECTURE.md

```python
# Vérifier le rôle:
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/accounts/profile/
# Regarder le champ "role"
```

### 8. Erreur: "The database is read-only"

**Cause:** Les permissions MySQL ne sont pas correctes

**Solutions:**
```bash
# Accorder les permissions:
mysql -u root -p
GRANT ALL PRIVILEGES ON uniticket_db.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## ⚠️ Avertissements Courants

### Migration Pending
```
# Vous avez créé de nouvelles migrations mais ne les avez pas appliquées
python manage.py migrate
```

### Changements non appliqués après modifications
```
# Redémarrer le serveur Django
# Ctrl+C pour arrêter
python manage.py runserver
```

### QR Code ne s'affiche pas
```
# Assurez-vous que Pillow est installé:
pip install Pillow --upgrade
```

## 🧪 Tests de Diagnostic

### Vérifier la connexion à la base de données
```bash
python manage.py dbshell
# Vous devriez voir le prompt MySQL
# Tapez EXIT; pour quitter
```

### Vérifier les migrations
```bash
python manage.py showmigrations
# Vous devriez voir un ✓ avant chaque migration appliquée
```

### Vérifier l'installation des paquets
```bash
pip list | grep -E "Django|djangorestframework|qrcode"
```

### Tester un endpoint
```bash
# D'abord, créer un utilisateur de test:
python manage.py shell
>>> from accounts.models import User
>>> u = User.objects.create_user(email='test@supnum.mr', password='test123', role='ADMIN')
>>> from rest_framework_simplejwt.tokens import RefreshToken
>>> refresh = RefreshToken.for_user(u)
>>> print(refresh.access_token)
# Copier le token

# Puis tester:
curl -H "Authorization: Bearer VOTRE_TOKEN" \
  http://localhost:8000/api/tickets/admin/dashboard/overview/
```

## 📋 Checklist de Dépannage

- [ ] MySQL est-il en cours d'exécution?
- [ ] La base de données `uniticket_db` existe-t-elle?
- [ ] Toutes les migrations ont-elles été appliquées? (`python manage.py showmigrations`)
- [ ] Les dépendances sont-elles installées? (`pip list`)
- [ ] Le token JWT est-il valide et pas expiré?
- [ ] L'utilisateur a-t-il le rôle approprié?
- [ ] La date du ticket est-elle valide?
- [ ] Les logs du serveur Django montrent-ils des erreurs?

## 🔍 Vérifier les Logs

### Logs du serveur Django
```
# Cherchez les erreurs en haut de la sortie du serveur
python manage.py runserver
```

### Logs de la base de données MySQL
```bash
# Sur Windows
type "C:\ProgramData\MySQL\MySQL Server 8.0\Data\*.err"

# Sur Linux
sudo tail -f /var/log/mysql/error.log
```

## 💡 Conseils Utiles

### Mode Debug Activé
```python
# Dans settings.py
DEBUG = True  # À passer à False en production
```

### Réinitialiser la base de données (⚠️ Attention)
```bash
# Cela SUPPRIME toutes les données
python manage.py flush

# Puis recharger les migrations
python manage.py migrate
```

### Créer de nouveaux modèles
```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### Créer un superadmin
```bash
python manage.py createsuperuser
# Suivre les instructions
```

## 🆘 Besoin d'Aide Supplémentaire?

1. Consultez les fichiers README.md et ARCHITECTURE.md
2. Vérifiez les tests dans tests.py pour voir des exemples d'utilisation
3. Consultez la documentation Django: https://docs.djangoproject.com/
4. Consultez la documentation Django REST Framework: https://www.django-rest-framework.org/

