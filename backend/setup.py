#!/usr/bin/env python
"""
Script de setup pour initialiser la base de données et l'application
"""

import os
import sys
import django

def setup_django():
    """Configure Django"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

def create_database():
    """Crée la base de données MySQL"""
    import mysql.connector
    from mysql.connector import Error
    
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        
        cursor = connection.cursor()
        
        # Créer la base de données
        cursor.execute("CREATE DATABASE IF NOT EXISTS uniticket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print("✓ Base de données créée/vérifiée")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"✗ Erreur lors de la création de la base de données: {e}")
        return False
    
    return True

def run_migrations():
    """Exécute les migrations"""
    from django.core.management import call_command
    
    try:
        call_command('migrate')
        print("✓ Migrations appliquées")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'exécution des migrations: {e}")
        return False

def create_superuser():
    """Crée un utilisateur administrateur"""
    from accounts.models import User
    
    email = input("Email du superadmin (admin@supnum.mr): ").strip() or "admin@supnum.mr"
    password = input("Mot de passe: ").strip()
    
    if not password:
        print("✗ Le mot de passe est requis")
        return False
    
    try:
        user = User.objects.create_superuser(
            email=email,
            password=password
        )
        print(f"✓ Superadmin créé: {email}")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la création du superadmin: {e}")
        return False

def create_test_users():
    """Crée des utilisateurs de test"""
    from accounts.models import User
    
    test_users = [
        {
            'email': 'student@supnum.mr',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'STUDENT'
        },
        {
            'email': 'agent@supnum.mr',
            'first_name': 'Alice',
            'last_name': 'Agent',
            'role': 'AGENT'
        }
    ]
    
    for user_data in test_users:
        try:
            User.objects.create_user(
                email=user_data['email'],
                password='testpass123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            print(f"✓ Utilisateur créé: {user_data['email']} ({user_data['role']})")
        except Exception as e:
            print(f"✗ Erreur lors de la création de {user_data['email']}: {e}")

def main():
    """Fonction principale"""
    setup_django()
    
    print("\n" + "="*50)
    print("  Configuration de UniTicket Backend")
    print("="*50 + "\n")
    
    # Étape 1: Créer la base de données
    print("[1/4] Création de la base de données...")
    if not create_database():
        print("Arrêt du setup")
        return
    
    # Étape 2: Exécuter les migrations
    print("\n[2/4] Application des migrations...")
    if not run_migrations():
        print("Arrêt du setup")
        return
    
    # Étape 3: Créer un superadmin
    print("\n[3/4] Création d'un superadmin...")
    response = input("Voulez-vous créer un superadmin? (o/n): ").strip().lower()
    if response == 'o':
        if not create_superuser():
            print("Erreur lors de la création du superadmin")
    
    # Étape 4: Créer des utilisateurs de test
    print("\n[4/4] Création d'utilisateurs de test...")
    response = input("Voulez-vous créer des utilisateurs de test? (o/n): ").strip().lower()
    if response == 'o':
        create_test_users()
    
    print("\n" + "="*50)
    print("  ✓ Configuration terminée!")
    print("="*50)
    print("\nProchaines étapes:")
    print("1. Démarrer le serveur: python manage.py runserver")
    print("2. Accéder à l'admin: http://127.0.0.1:8000/admin/")
    print("3. Consulter la documentation: tickets/README.md")
    print("\n")

if __name__ == '__main__':
    main()
