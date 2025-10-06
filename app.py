import requests
import json
import time  # Importé pour ajouter un délai entre les messages
from supabase import create_client
from typing import List, Dict

# --- CONFIGURATION ---
# Il est recommandé d'utiliser des variables d'environnement pour les clés secrètes
# Pour ce script, nous les laissons en dur pour la simplicité.
SUPABASE_URL = 'https://godhvvxapbtghchfrcxz.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdvZGh2dnhhcGJ0Z2hjaGZyY3h6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkxMDEyMDgsImV4cCI6MjA3NDY3NzIwOH0.RK0-YEzLACd8BuCtmwfRNZEgNKlxD5pjQHCraqXANNs'
WHAPI_URL = "https://gate.whapi.cloud/messages/text"
WHAPI_TOKEN = "Bearer lvzUyiOL5gFebR9hf4qJipRCOHVkXSO9"

# Initialisation du client Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FONCTIONS ---

def get_users_data() -> List[Dict[str, str]]:
    """
    Récupère les noms complets et les numéros de téléphone de tous les utilisateurs
    depuis la table 'userData' de Supabase.
    Retourne une liste de dictionnaires, ex: [{'fullname': 'Jean', 'phone': '336...'}, ...]
    """
    try:
        # On sélectionne à la fois le nom et le téléphone
        response = supabase.table('userData').select('fullname, phone').execute()
        # On filtre pour ne garder que les utilisateurs qui ont un nom et un téléphone
        users = [
            {"fullname": user['fullname'], "phone": user['phone']} 
            for user in response.data 
            if user.get('fullname') and user.get('phone')
        ]
        print(f"✅ {len(users)} utilisateur(s) récupéré(s) depuis la base de données.")
        return users
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données utilisateur : {e}")
        return []

def generer_message_personnalise(fullname: str) -> str:
    """
    Génère le message WhatsApp en y insérant le nom de l'utilisateur.
    """
    message = f"""
Bonjour {fullname},

Bientôt disponible ! 

Ketoko est la nouvelle application mobile panafricaine qui révolutionne les achats et les ventes en ligne au Congo et partout en Afrique. Simplifiez votre expérience shopping et business avec une plateforme intuitive et sécurisée.

Téléchargez-la ici : https://ketoko.net

Merci pour votre confiance.
L'équipe Ketoko
    """
    # On nettoie les espaces en trop pour un affichage propre
    return message.strip()

def envoyer_message_whatsapp(phone_number: str, message_body: str):
    """
    Prépare et envoie un message via l'API Whapi.
    Gère les erreurs de connexion et les réponses de l'API.
    """
    headers = {
        "accept": "application/json",
        "authorization": WHAPI_TOKEN,
        "content-type": "application/json"
    }

    payload = {
        "to": phone_number,
        "body": message_body,
        "preview_url": True
    }

    try:
        response = requests.post(WHAPI_URL, headers=headers, json=payload)
        
        # Vérifier si la requête a été acceptée par l'API (codes 200 ou 201)
        if response.status_code in [200, 201]:
            print("   ✅ Message envoyé avec succès !")
        else:
            # Afficher l'erreur renvoyée par l'API si le code n'est pas un succès
            error_data = response.json()
            print(f"   ❌ Erreur API (Code: {response.status_code}): {error_data.get('error', {}).get('message', 'Erreur inconnue')}")

    except requests.exceptions.RequestException as e:
        print(f"   ❌ Erreur de connexion lors de l'envoi à {phone_number} : {e}")

def main():
    """
    Fonction principale qui orchestre l'automatisation.
    """
    print("--- Démarrage de l'automatisation d'envoi de messages WhatsApp ---")
    
    # 1. Récupérer la liste des utilisateurs
    utilisateurs = get_users_data()
    
    if not utilisateurs:
        print("Aucun utilisateur à contacter. Arrêt du script.")
        return

    # 2. Envoyer un message à chaque utilisateur
    for utilisateur in utilisateurs:
        fullname = utilisateur['fullname']
        phone = utilisateur['phone']
        
        print(f"\n-> Préparation de l'envoi pour {fullname} ({phone})...")
        
        # Nettoyer le numéro de téléphone (supprimer les espaces, +, etc.)
        # L'API Whapi n'accepte que les chiffres
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        if not clean_phone:
            print(f"   ⚠️ Numéro de téléphone invalide, passage au suivant.")
            continue

        # 3. Générer le message personnalisé
        message = generer_message_personnalise(fullname)
        
        # 4. Envoyer le message
        envoyer_message_whatsapp(clean_phone, message)
        
        # 5. Attendre 1 seconde avant d'envoyer le message suivant
        # C'est CRUCIAL pour ne pas être bloqué par l'API pour envoi excessif (rate limiting)
        time.sleep(1) 
        
    print("\n--- Automatisation terminée ---")


# --- POINT D'ENTRÉE DU SCRIPT ---
# Cette structure garantit que le code ne s'exécute que lorsque le script est lancé directement
if __name__ == "__main__":
    main()