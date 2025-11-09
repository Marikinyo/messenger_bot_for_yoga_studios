from config import SIMILARITY_THRESHOLD
from nlp_utils import match_faq
# Removed global data loads (load_data_from_file) as data is now passed in

# UPDATED-------------
def get_class_schedule(schedule_data, lang, class_type=None):
    """
    Constructs the class schedule response from the provided language-specific data.
    """
    results = []
    for cls in schedule_data.get("classes", []):
        if class_type is None or cls["type"].lower() == class_type.lower():
            results.append(f"{cls['type']} with {cls['trainer']} on {', '.join(cls['days'])} at {cls['hours']}")
    
    if not results:
        # Use language key for fallback message
        if lang == "georgian":
            return "მაპატიეთ, შესაბამისი კლასი ვერ მოიძებნა."
        return "Sorry, no matching class found."
    return "\n".join(results)


# UPDATED-------------
def get_location_info(location_data):
    """
    Constructs the location and contact information response from the provided data.
    """
    loc = location_data
    hours = "\n".join([f"{day}: {time}" for day, time in loc.get("opening_hours", {}).items()])
    return (
        f"{loc['studio_name']}\n"
        f"Address: {loc['address']}\n"
        f"Phone: {loc['phone']}\n"
        f"Email: {loc['email']}\n"
        f"Opening hours:\n{hours}"
    )


# UPDATED------------- (New signature to accept all data)
def get_answer(query, intent_name, lang, faq_data, faq_embeddings, schedule_data, location_data, default_messages):
    """
    Handles complex intent routing (schedule, location, faq) using the data provided.
    
    The data (faq_data, schedule_data, location_data) is assumed to be already 
    language-specific based on the detection done in app.py.
    """
    query_lower = query.lower()
    
    # 1. Schedule Request Logic
    if intent_name == "schedule_request":
        # Check if the user specified a class type within the query
        for cls in schedule_data.get("classes", []):
            if cls["type"].lower() in query_lower:
                # Return schedule for specific class
                return get_class_schedule(schedule_data, lang, cls["type"])
        
        # If no specific class is found, return the full schedule
        return get_class_schedule(schedule_data, lang)

    # 2. Location Request Logic
    elif intent_name == "location_request":
        return get_location_info(location_data)

    # 3. FAQ Logic (Catch-all for 'faq' intent)
    elif intent_name == "faq":
        faq_response = match_faq(
            query, 
            faq_embeddings, 
            faq_data, 
            threshold=SIMILARITY_THRESHOLD 
        )

        if faq_response:
            return faq_response
    
    # 4. Fallback (for generic questions or unhandled intents)
    # Use the static response from default_messages based on the detected language
    return default_messages.get(lang, default_messages.get('english', "Sorry, I didn't understand."))
