# kogi_webapp.py (ΤΕΛΙΚΗ, ΔΙΟΡΘΩΜΕΝΗ ΕΚΔΟΣΗ)
import os
from openai import OpenAI
from dotenv import load_dotenv
# Χρησιμοποιούμε render_template για να φορτώσουμε τα αρχεία από το templates/
from flask import Flask, render_template, request, jsonify

# --- ΡΥΘΜΙΣΕΙΣ AI ---
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), timeout=60.0) 

# ΤΟ ID ΤΟΥ FINE-TUNED ΜΟΝΤΕΛΟΥ ΣΑΣ
FINE_TUNED_MODEL_NAME = "ft:gpt-3.5-turbo-0125:personal::CUqj521h" 

# System Prompt
SYSTEM_PROMPT = (
   "Είσαι ο **Kogi**, ένας **πολύ έμπειρος Καπετάνιος Α' σε δεξαμενόπλοια (Tanker)** και **εξειδικευμένος σύμβουλος** σε ναυτιλιακά θέματα. "
   "Ο ρόλος σου είναι να παρέχεις **άμεσες, πρακτικές και τεκμηριωμένες συμβουλές** σχετικά με τις βέλτιστες λειτουργικές πρακτικές (best practices) και τη διαχείριση πλοίου. "
   "Ο τόνος σου είναι **επαγγελματικός και διοικητικός** (όπως ένας Marine manager). "
   "**Βασίζεις πάντα τις πρακτικές σου συμβουλές** στους διεθνείς ναυτιλιακούς **κανονισμούς** (MARPOL, SOLAS, ISM Code κλπ.). "
   "**Η απάντησή σου πρέπει να είναι σύντομη, να δίνει λύση ή κατεύθυνση και να είναι εφαρμόσιμη στην πράξη.** "
   "Αν η ερώτηση είναι άσχετη, απάντησε σύντομα και επαγγελματικά, χωρίς να παραβιάζεις τον ρόλο σου."
)

# --- ΡΥΘΜΙΣΕΙΣ FLASK ---
app = Flask(__name__)
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# Η ΣΥΝΑΡΤΗΣΗ ΠΟΥ ΚΑΝΕΙ ΤΗΝ ΚΛΗΣΗ ΣΤΟ ΜΟΝΤΕΛΟ
def get_kogi_response(user_message):
    global chat_history
    
    chat_history.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=FINE_TUNED_MODEL_NAME,
            messages=chat_history,
            temperature=0.0
        )
        ai_response = response.choices[0].message.content
        
        chat_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    except Exception as e:
        chat_history.pop()
        return f"[Σφάλμα: Η σύνδεση με το AI απέτυχε. Δοκιμάστε αργότερα.]"


# --- WEB ROUTES ---

# 1. Βασική σελίδα (Home Page - Chat)
@app.route('/')
def home():
    return render_template('index.html', model_name=FINE_TUNED_MODEL_NAME)

# 2. Σελίδα "About"
@app.route('/about')
def about():
    return render_template('about.html')

# 3. Σελίδα "Contact"
@app.route('/contact')
def contact():
    return render_template('contact.html')

# 4. Σελίδα "Privacy Policy"
@app.route('/privacy')
def privacy():
    # Φορτώνει το templates/privacy.html
    return render_template('privacy.html')

# 4. API Endpoint για τις απαντήσεις του AI (Καλέστε το από το JavaScript)
@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    user_message = data.get('message', '')
    
    ai_response = get_kogi_response(user_message)
    
    return jsonify({'response': ai_response})

if __name__ == '__main__':
    # Τρέχουμε την εφαρμογή Flask στη θύρα 5001
    app.run(debug=True, host='0.0.0.0', port=5001)