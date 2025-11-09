from flask import Flask, request
from config import VERIFY_TOKEN
from messenger_utils import send_message
from bot_logic import get_answer
from nlp_utils import detect_intent_ai, get_intent_response
from data_loader import load_data_from_file


app = Flask(__name__)

#---------------------------------------------
# Global Data Loads are Commented Out (We now load data per-page in webhook)
#---------------------------------------------

@app.route("/", methods=["GET"])
def home():
    return "Messenger bot is running!"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        token_sent = request.args.get("hub.verify_token")
        return request.args.get("hub.challenge") if token_sent == VERIFY_TOKEN else "Invalid token"
    
    # POST: incoming messages
    output = request.get_json(silent=True)
    if not output:
        return "No JSON payload", 400

    for entry in output.get("entry", []):
        #-------------------------------
        # Load Page-Specific Data
        page_id = entry.get("id")
        if not page_id:
            print("Error: Could not find Page ID in entry.")
            continue
            
        # All data files are loaded with the page_id context
        faq_english = load_data_from_file("faq_english.json", page_id)
        faq_embeddings_english = load_data_from_file("faq_english_embeddings.json", page_id)
        faq_georgian = load_data_from_file("faq_georgian.json", page_id)
        faq_embeddings_georgian = load_data_from_file("faq_georgian_embeddings.json", page_id)

        schedule_en = load_data_from_file("schedule_english.json", page_id)
        schedule_ge = load_data_from_file("schedule_georgian.json", page_id)
        location_en = load_data_from_file("location_contact_english.json", page_id)
        location_ge = load_data_from_file("location_contact_georgian.json", page_id)

        intents = load_data_from_file("intents.json", page_id)

        default_messages = load_data_from_file("default_messages.json", page_id)
        #-------------------------------
        for messaging_event in entry.get("messaging", []):
            sender = messaging_event.get("sender")
            message = messaging_event.get("message")
            
            # Use robust checks for critical fields
            if not isinstance(sender, dict) or not isinstance(message, dict):
                continue
            
            sender_id = sender.get("id")
            user_text = message.get("text")
            
            # Skip if no sender ID or non-text message
            if not sender_id or not isinstance(user_text, str):
                continue

            try:
                
                # 1. Intent Detection (FIXED: Passing intents)
                intent, lang = detect_intent_ai(user_text, intents) 
                print("AI-detected intent:", intent)
                response_text = None

                # Determine language-specific data sets
                is_georgian = (lang == "georgian")
                
                current_faq = faq_georgian if is_georgian else faq_english
                current_embeddings = faq_embeddings_georgian if is_georgian else faq_embeddings_english
                current_schedule = schedule_ge if is_georgian else schedule_en
                current_location = location_ge if is_georgian else location_en

                # 2. Intent-Based Response (DATA-DRIVEN)
                # Pass intents data to get the static response
                response_text = get_intent_response(intent, lang, intents) 

                # 3. Dynamic/FAQ Fallback (FIXED: Using 8-parameter signature)
                if not response_text:
                    response_text = get_answer(
                        user_text, 
                        intent, # intent name (needed for routing in bot_logic)
                        lang, # detected language
                        current_faq, # Language specific FAQ data
                        current_embeddings, # Language specific embeddings
                        current_schedule, # Language specific schedule
                        current_location, # Language specific location
                        default_messages # Default messages
                    )

                # 4. Final Fallback
                if not response_text:
                    # Uses the detected language key directly for fallback message
                    response_text = default_messages.get(lang, "Sorry, I didn't understand.")

            except Exception as e:
                print("Error processing message:", e)
                response_text = "Sorry, something went wrong."

            # Send response
            try:
                if response_text:
                    send_message(sender_id, response_text, page_id)
            except Exception as e:
                print("Error sending message:", e)

    return "ok", 200


# --- Run server ---
if __name__ == "__main__":
    app.run(port=5000, debug=True, use_reloader=False)
