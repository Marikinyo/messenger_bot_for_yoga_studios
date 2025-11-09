import requests
from config import PAGE_CONFIGS

# PAGE_ACCESS_TOKEN = ""
# for page_id in PAGE_CONFIGS.keys():
#     PAGE_ACCESS_TOKEN = PAGE_CONFIGS[page_id]['token']


# def send_message(recipient_id, text):
#     """Send message back to a Facebook Messenger user."""
#     url = "https://graph.facebook.com/v21.0/me/messages"
#     params = {"access_token": PAGE_ACCESS_TOKEN}
#     headers = {"Content-Type": "application/json"}
#     data = {"recipient": {"id": recipient_id}, "message": {"text": text}}
#     r = requests.post(url, params=params, headers=headers, json=data)
#     if r.status_code != 200:
#         print(f"Error sending message: {r.text}")
#         print(f"Facebook API Response: {r.text}")
        
       

def send_message(recipient_id: str, text: str, page_id: str):
    """
    Send message back to a Facebook Messenger user, fetching the access token
    based on the provided page_id.
    """
    
    # 1. Get the configuration for the specific page
    page_config = PAGE_CONFIGS.get(page_id)
    
    if not page_config:
        print(f"Error: Page ID '{page_id}' not found in PAGE_CONFIGS.")
        return

    # 2. Extract the Page Access Token
    page_access_token = page_config.get("token")
    if not page_access_token:
        print(f"Error: Access token not found for Page ID '{page_id}'.")
        return

    # 3. Construct and send the request
    url = "https://graph.facebook.com/v21.0/me/messages"
    
    # Use the specific token for the page
    params = {"access_token": page_access_token}
    
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": recipient_id}, "message": {"text": text}}
    
    r = requests.post(url, params=params, headers=headers, json=data)
    
    if r.status_code != 200:
        print(f"Error sending message to {page_id} ({page_config.get('page_name')}): {r.text}")
        print(f"Facebook API Response: {r.text}")
    else:
        print(f"Message sent successfully for Page ID {page_id}.")