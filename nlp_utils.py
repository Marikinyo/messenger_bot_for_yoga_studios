import math
from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL, SIMILARITY_THRESHOLD
from data_loader import load_data_from_file
import json

client = OpenAI(api_key=OPENAI_API_KEY)

# intents = load_data_from_file("intents.json")


def cosine_similarity(vec1, vec2):
    if len(vec1) != len(vec2):
        return 0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))
    if norm1 == 0 or norm2 == 0:
        return 0
    return dot_product / (norm1 * norm2)

def match_faq(query, faq_embeddings, faq_data, threshold=SIMILARITY_THRESHOLD):
    # Generate embedding for user query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    user_vector = response.data[0].embedding

    # Find best match
    best_question = None
    best_score = 0
    for question, vector in faq_embeddings.items():
        score = cosine_similarity(user_vector, vector)
        if score > best_score:
            best_score = score
            best_question = question

    if best_score >= threshold:
        return faq_data[best_question]
    return None



def preprocess_intents(intents_data):
    """
    Creates a global dictionary for O(1) lookup of examples.
    """
    processed_intents = {}
    for intent in intents_data.get('intents', []): 
        name = intent["name"]
        processed_intents[name] = {
            "english": [ex.lower().strip() for ex in intent.get("examples", {}).get("english", [])],
            "georgian": [ex.lower().strip() for ex in intent.get("examples", {}).get("georgian", [])]
        }
    return processed_intents


def detect_intent_ai(query, intents_data):
    is_ge = any(ord(c) > 127 for c in query)
    lang = "georgian" if is_ge else "english"
    
    # Get intent names from the passed data
    intent_names = list(preprocess_intents(intents_data).keys())
    
    system_prompt = f"""
    You are a Natural Language Understanding (NLU) model for a yoga studio chatbot.
    Your task is to classify the user's query into one of the following intents: {', '.join(list(preprocess_intents(intents_data).keys()))}.
    If the query clearly asks about a class schedule or location, use 'schedule_request' or 'location_request'.
    If it's a simple salutation, use 'greeting'. If it's thanks, use 'thanks'.
    For any other complex question (pricing, booking, descriptions, etc.), use the general intent 'faq'.

    You MUST only respond with a single JSON object. Do not include any other text or explanation.
    JSON Format: {{"intent": "CLASSIFIED_INTENT_NAME"}}
    """
    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},
            temperature=0.0 
        )
        
        json_string = response.choices[0].message.content
        intent_data = json.loads(json_string)
        
        intent_name = intent_data.get("intent", "faq")
        if intent_name not in list(preprocess_intents(intents_data).keys()):
             intent_name = "faq"

        return intent_name, lang

    except Exception as e:
        print(f"Error detecting intent with OpenAI: {e}")
        return "faq", lang 


def get_intent_response(intent_name, lang="english", intents_data=None):
    """
    Retrieves a static response message for a matched intent from the JSON data.
    """
    if not intents_data:
        # Fallback if no intent data is provided
        return None 
    
    for intent in intents_data.get('intents', []): 
        if intent["name"] == intent_name:
            responses = intent.get("responses", {}).get(lang, [])
            
            if not responses and lang == "georgian":
                 responses = intent.get("responses", {}).get("english", [])

            if responses:
                return responses[0] 
                
    return None

