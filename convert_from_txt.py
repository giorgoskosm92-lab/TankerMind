# convert_from_txt.py
import os
import json
from dotenv import load_dotenv

# Φορτώνουμε το System Prompt από τον kogi_webapp.py για συνέπεια
# ΠΡΟΣΟΧΗ: Αντικαταστήστε με το δικό σας πλήρες System Prompt!
SYSTEM_PROMPT = (
    "Είσαι ο **TankerMind**, ένας **πολύ έμπειρος Master Mariner** και **εξειδικευμένος σύμβουλος** σε ναυτιλιακά θέματα. "
    "Ο ρόλος σου είναι να παρέχεις **άμεσες, πρακτικές και τεκμηριωμένες συμβουλές** σχετικά με τις βέλτιστες λειτουργικές πρακτικές (best practices) και τη διαχείριση πλοίου. "
    "Ο τόνος σου είναι **επαγγελματικός και διοικητικός**."
)

# --- ΟΡΙΣΜΟΙ ΑΡΧΕΙΩΝ ---
INPUT_TXT_FILE = 'new_qa_fixes.txt'
OUTPUT_JSONL_FILE = 'new_training_data.jsonl'


def convert_txt_to_jsonl(input_file, output_file, system_prompt):
    
    # 1. Διάβασμα του TXT αρχείου
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"❌ ΣΦΑΛΜΑ: Το αρχείο εισόδου '{input_file}' δεν βρέθηκε.")
        return

    training_data = []
    current_user_message = None
    
    print("-> Εκκίνηση μετατροπής...")

    # 2. Επεξεργασία κάθε γραμμής
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('USER:'):
            # Αρχή νέου ζεύγους (Ερώτηση)
            if current_user_message:
                print(f"⚠️ Προσοχή: Παραλείφθηκε απάντηση για το: {current_user_message[:30]}...")
            current_user_message = line[len('USER:'):].strip()
            
        elif line.startswith('ASSISTANT:'):
            # Βρέθηκε απάντηση
            assistant_message = line[len('ASSISTANT:'):].strip()
            
            if current_user_message:
                # 3. Δημιουργία δομής JSONL
                entry = {
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": current_user_message},
                        {"role": "assistant", "content": assistant_message}
                    ]
                }
                training_data.append(entry)
                current_user_message = None # Μηδενισμός για το επόμενο ζεύγος
            
    # 4. Εγγραφή στο JSONL αρχείο
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for entry in training_data:
            json_line = json.dumps(entry, ensure_ascii=False)
            outfile.write(json_line + '\n')

    print("\n✅ Ολοκλήρωση!")
    print(f"Επιτυχής μετατροπή: {len(training_data)} ζεύγη.")
    print(f"Το αρχείο {output_file} είναι έτοιμο για ανέβασμα.")


if __name__ == "__main__":
    convert_txt_to_jsonl(INPUT_TXT_FILE, OUTPUT_JSONL_FILE, SYSTEM_PROMPT)