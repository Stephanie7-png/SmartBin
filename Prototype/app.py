from flask import Flask, jsonify, request, render_template, session, redirect, url_for
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'smartbin_super_secret_key_sysops' # Clé pour sécuriser les sessions utilisateur
CORS(app)

# Base de données en mémoire des utilisateurs
USERS = {
    "admin": {"password": "admin123", "role": "admin", "zone": "all"},
    "agent_ville": {"password": "pass123", "role": "agent", "zone": "ville"},
    "agent_entreprise": {"password": "pass123", "role": "agent", "zone": "entreprise"}
}

smart_bins = [
    {"id": 1, "name": "Hall d'Accueil — Mairie", "level": 25, "type": "Tout venant", "zone": "ville", "mail_sent": False},
    {"id": 2, "name": "Poubelle Publique — Parc", "level": 37, "type": "Plastique/Verre", "zone": "ville", "mail_sent": False},
    {"id": 5, "name": "Conteneur — Place Centrale", "level": 15, "type": "Papier/Carton", "zone": "ville", "mail_sent": False},
    {"id": 3, "name": "Bac Bleu — Bureau 102", "level": 64, "type": "Papier", "zone": "entreprise", "mail_sent": False},
    {"id": 4, "name": "Bac Jaune — Couloir Sud", "level": 13, "type": "Plastique", "zone": "entreprise", "mail_sent": False},
    {"id": 6, "name": "Poubelle Verte — Cafét", "level": 45, "type": "Organique", "zone": "entreprise", "mail_sent": False}
]

def envoyer_alerte_mail(bin_name, level):
    """Fonction SysOps pour envoyer un mail automatique d'alerte"""
    print(f" [MAIL] Tentative d'envoi d'alerte pour {bin_name} ({level}%)")
    
    
    sender = "alertes@smartbin.local"
    receiver = "stephaniemakeu7@gmail.com"
    
    msg = MIMEText(f"ALERTE LOGISTIQUE SMARTBIN \n\nLe bac '{bin_name}' a atteint un niveau critique de {level}%.\nIl est l'heure de planifier le ramassage.")
    msg['Subject'] = f" SmartBin Pleine : {bin_name}"
    msg['From'] = sender
    msg['To'] = receiver

    # Simulation d'envoi dans les logs pour ne pas bloquer si le serveur n'a pas internet
    print(f"--- CONTENU DU MAIL ENVOYÉ ---\n{msg.as_string()}\n------------------------------")

@app.route('/')
def home():
    if 'username' not in session:
        return render_template('login.html')
    return render_template('index.html', user=session['username'], role=session['role'], zone=session['zone'])

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    
    user = USERS.get(username)
    if user and user['password'] == password:
        session['username'] = username
        session['role'] = user['role']
        session['zone'] = user['zone']
        return redirect(url_for('home'))
    
    return render_template('login.html', error="Identifiants invalides")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/bins', methods=['GET'])
def get_bins():
    return jsonify(smart_bins)

@app.route('/api/bins/<int:bin_id>', methods=['POST'])
def update_bin_level(bin_id):
    data = request.get_json()
    for p in smart_bins:
        if p["id"] == bin_id:
            p["level"] = max(0, min(100, int(data["level"])))
            
            # Déclenchement du mail automatique à 80% si pas encore envoyé
            if p["level"] >= 80 and not p["mail_sent"]:
                envoyer_alerte_mail(p["name"], p["level"])
                p["mail_sent"] = True
            elif p["level"] < 80:
                p["mail_sent"] = False # Réinitialise l'alerte si vidée
                
            return jsonify({"status": "success", "bin": p})
    return jsonify({"error": "Non trouvé"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
