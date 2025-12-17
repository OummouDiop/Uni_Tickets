from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.conf import settings
import json
from .models import User, PasswordResetCode

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')

        if not email or not password:
            return JsonResponse({'error': 'Email et mot de passe requis'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email existe déjà'}, status=400)

        # Le rôle est toujours STUDENT par défaut, seul l'admin peut le modifier
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='STUDENT'
        )

        return JsonResponse({
            'message': 'Compte créé avec succès',
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        })


@csrf_exempt
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            return JsonResponse({'error': 'Identifiants incorrects'}, status=400)

        return JsonResponse({
            'message': 'Connexion réussie',
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role
            }
        })


@csrf_exempt
def profile(request):
    """Obtenir le profil d'un utilisateur"""
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'user_id requis'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
            return JsonResponse({
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.isoformat()
                }
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)


@csrf_exempt
def update_profile(request):
    """Mettre à jour le profil d'un utilisateur"""
    if request.method == 'PUT':
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({'error': 'user_id requis'}, status=400)
        
        try:
            user = User.objects.get(id=user_id)
            
            # Mise à jour des champs autorisés
            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'password' in data and data['password']:
                user.set_password(data['password'])
            
            user.save()
            
            return JsonResponse({
                'message': 'Profil mis à jour avec succès',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)


@csrf_exempt
def list_users(request):
    """Liste tous les utilisateurs (ADMIN uniquement)"""
    if request.method == 'GET':
        admin_id = request.GET.get('admin_id')
        
        if not admin_id:
            return JsonResponse({'error': 'admin_id requis'}, status=400)
        
        try:
            admin = User.objects.get(id=admin_id)
            
            # Vérifier si l'utilisateur est ADMIN
            if admin.role != 'ADMIN':
                return JsonResponse({'error': 'Accès refusé. Admin uniquement.'}, status=403)
            
            users = User.objects.all().order_by('-date_joined')
            users_list = [{
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat()
            } for user in users]
            
            return JsonResponse({
                'users': users_list,
                'total': len(users_list)
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'Admin introuvable'}, status=404)


@csrf_exempt
def change_role(request):
    """Changer le rôle d'un utilisateur (ADMIN uniquement)"""
    if request.method == 'PUT':
        data = json.loads(request.body)
        admin_id = data.get('admin_id')
        user_id = data.get('user_id')
        new_role = data.get('role')
        
        if not admin_id or not user_id or not new_role:
            return JsonResponse({'error': 'admin_id, user_id et role requis'}, status=400)
        
        # Vérifier que le rôle est valide
        valid_roles = ['STUDENT', 'ADMIN', 'AGENT']
        if new_role not in valid_roles:
            return JsonResponse({'error': f'Rôle invalide. Valeurs possibles: {", ".join(valid_roles)}'}, status=400)
        
        try:
            admin = User.objects.get(id=admin_id)
            
            # Vérifier si l'utilisateur est ADMIN
            if admin.role != 'ADMIN':
                return JsonResponse({'error': 'Accès refusé. Admin uniquement.'}, status=403)
            
            user = User.objects.get(id=user_id)
            old_role = user.role
            user.role = new_role
            user.save()
            
            return JsonResponse({
                'message': f'Rôle changé de {old_role} à {new_role}',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                }
            })
        except User.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)


@csrf_exempt
def request_password_reset(request):
    """Étape 1: Demander un code de réinitialisation"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'error': 'Email requis'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            
            # Invalider les anciens codes non utilisés
            PasswordResetCode.objects.filter(user=user, is_used=False).update(is_used=True)
            
            # Créer un nouveau code
            reset_code = PasswordResetCode.objects.create(user=user)
            
            # Envoyer le code par email (pour l'instant, on le retourne dans la réponse)
            # TODO: Configurer l'envoi d'email
            try:
                send_mail(
                    'Code de réinitialisation - Uni Tickets',
                    f'Votre code de réinitialisation est: {reset_code.code}\n\nCe code expire dans 15 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                message = 'Code envoyé par email'
            except Exception as e:
                # Si l'email échoue, retourner le code dans la réponse (pour le développement)
                message = f'Email non configuré. Code: {reset_code.code}'
            
            return JsonResponse({
                'message': message,
                'email': user.email
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'Email introuvable'}, status=404)


@csrf_exempt
def verify_reset_code(request):
    """Étape 2: Vérifier le code de réinitialisation"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        
        if not email or not code:
            return JsonResponse({'error': 'Email et code requis'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).order_by('-created_at').first()
            
            if not reset_code:
                return JsonResponse({'error': 'Code invalide'}, status=400)
            
            if not reset_code.is_valid():
                return JsonResponse({'error': 'Code expiré'}, status=400)
            
            return JsonResponse({
                'message': 'Code valide',
                'email': user.email
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'Email introuvable'}, status=404)


@csrf_exempt
def reset_password(request):
    """Étape 3: Réinitialiser le mot de passe avec le code"""
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        code = data.get('code')
        new_password = data.get('new_password')
        
        if not email or not code or not new_password:
            return JsonResponse({'error': 'Email, code et nouveau mot de passe requis'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            reset_code = PasswordResetCode.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).order_by('-created_at').first()
            
            if not reset_code:
                return JsonResponse({'error': 'Code invalide'}, status=400)
            
            if not reset_code.is_valid():
                return JsonResponse({'error': 'Code expiré'}, status=400)
            
            # Changer le mot de passe
            user.set_password(new_password)
            user.save()
            
            # Marquer le code comme utilisé
            reset_code.is_used = True
            reset_code.save()
            
            return JsonResponse({
                'message': 'Mot de passe réinitialisé avec succès'
            })
            
        except User.DoesNotExist:
            return JsonResponse({'error': 'Email introuvable'}, status=404)

