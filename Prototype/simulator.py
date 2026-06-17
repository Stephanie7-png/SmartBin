import time
import random
import requests

API_URL = "http://127.0.0.1:5000/api/bins"

print(" Simulateur de flux de déchets SmartBin démarré...")

while True:
    try:
        # 1. Récupérer l'état actuel des poubelles
        response = requests.get(API_URL)
        if response.status_code == 200:
            bins = response.json()
            
            for b in bins:
                # Si la poubelle est pleine (>=95%), on ne la remplit plus automatiquement
                if b["level"] >= 95:
                    continue
                    
                # Simulation réaliste selon le lieu
                if "Cafét" in b["name"]:
                    # La cafét se remplit vite (gros flux de déchets organiques)
                    increment = random.randint(3, 8)
                elif "Hall" in b["name"]:
                    increment = random.randint(1, 5)
                else:
                    increment = random.randint(0, 3)
                
                new_level = min(100, b["level"] + increment)
                
                # Mettre à jour la poubelle via l'API locale
                requests.post(f"{API_URL}/{b['id']}", json={"level": new_level})
                
            print(f"[Simulation] Mise à jour des niveaux effectuée. Prochain flux dans 10 secondes.")
            
    except Exception as e:
        print(f"⚠️rreur de connexion avec l'API : {e}")
        
    # Attend 10 secondes avant le prochain jet de déchets
    time.sleep(10)
