# kogi_webapp.py (ΤΕΛΙΚΗ ΕΚΔΟΣΗ - HYBRID CHAT v3.0 - ΣΥΓΧΡΟΝΙΣΜΕΝΟ)
import os
import uuid
import base64
from io import BytesIO
from PIL import Image 

from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

# --- ΡΥΘΜΙΣΕΙΣ AI & MODES ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=90.0) 

FINE_TUNED_MODEL_NAME = "ft:gpt-3.5-turbo-0125:personal::CYB1QaaS"
VISION_MODEL_NAME = "gpt-4o" 

SYSTEM_PROMPT = (
   "Είσαι ο **TankerMind**, ένας **πολύ έμπειρος Master Mariner** και **εξειδικευμένος σύμβουλος** σε ναυτιλιακά θέματα. "
   "Ο τόνος σου είναι **επαγγελματικός και διοικητικός**. "
   "Βασίζεις πάντα τις συμβουλές σου σε ναυτιλιακούς **κανονισμούς** (MARPOL, SOLAS, ISM Code κλπ.). "
   "Απάντησε σύντομα, δίνοντας λύση. Αν λάβεις εικόνα, η απάντησή σου πρέπει να εστιάζει στην ανάλυση της ασφάλειας και της πρακτικής."
)

# --- ΡΥΘΜΙΣΕΙΣ FLASK & DB ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', str(uuid.uuid4())) 
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db') 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
global_chat_history = [{"role": "system", "content": SYSTEM_PROMPT}] 

# -------------------------------------------------------------------------
# DB MODEL & HELPER FUNCTIONS
# -------------------------------------------------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    is_subscribed = db.Column(db.Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"User('{self.email}', 'Verified: {self.is_verified}', 'Subscribed: {self.is_subscribed}')"

with app.app_context():
    db.create_all()


def encode_image_to_base64(image_file):
    try:
        img = Image.open(image_file)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=70)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

# -------------------------------------------------------------------------
# HYBRID CHAT LOGIC
# -------------------------------------------------------------------------
def get_hybrid_response(user_message, image_base64=None):
    global global_chat_history
    
    if image_base64:
        model_to_use = VISION_MODEL_NAME
        content_for_api = [
            {"type": "text", "text": user_message or "Ανάλυσέ μου αυτή τη ναυτιλιακή εικόνα."},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
        ]
    else:
        model_to_use = FINE_TUNED_MODEL_NAME
        content_for_api = user_message

    if image_base64:
        messages_to_send = [{"role": "system", "content": SYSTEM_PROMPT}, 
                            {"role": "user", "content": content_for_api}]
    else:
        messages_to_send = global_chat_history + [{"role": "user", "content": content_for_api}]
    
    try:
        response = client.chat.completions.create(
            model=model_to_use,
            messages=messages_to_send,
            temperature=0.0
        )
        ai_response = response.choices[0].message.content
        
        global_chat_history.append({"role": "user", "content": user_message})
        global_chat_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except Exception as e:
        return f"[Σφάλμα: Η σύνδεση με το AI απέτυχε. Δοκιμάστε αργότερα. ({model_to_use} Error: {str(e)})]"

# -------------------------------------------------------------------------
# WEB ROUTES
# -------------------------------------------------------------------------

@app.route('/')
def home():
    return render_template('index.html', model_name=FINE_TUNED_MODEL_NAME)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

# [Εδώ εισάγετε τις routes για Login/Signup/Verify]

# *** ΔΙΟΡΘΩΣΗ ENDPOINT ***
# Αυτό είναι το ΜΟΝΑΔΙΚΟ endpoint για το chat
@app.route('/api/chat', methods=['POST'])
def handle_hybrid_chat():
    
    # [Εδώ θα μπει η λογική ελέγχου Login/Subscription]
    
    user_message = request.form.get('message', '')
    # *** ΔΙΟΡΘΩΣΗ ΟΝΟΜΑΤΟΣ ΑΡΧΕΙΟΥ ***
    image_file = request.files.get('image_file') 

    image_base64 = None
    
    if image_file and image_file.filename != '':
        if image_file.mimetype.startswith('image/'):
            image_base64 = encode_image_to_base64(image_file)
        else:
            return jsonify({'response': 'Μόνο αρχεία εικόνας επιτρέπονται.'})

    if not user_message and not image_base64:
        return jsonify({'response': 'Δεν δόθηκε μήνυμα ή εικόνα.'})
        
    ai_response = get_hybrid_response(user_message, image_base64)
    
    return jsonify({'response': ai_response})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)