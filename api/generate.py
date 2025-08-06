import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import firebase_admin
from firebase_admin import credentials, auth, firestore

import google.generativeai as genai

# --- INITIALIZATION ---
cred_json = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
cred = credentials.Certificate(cred_json)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
text_model = genai.GenerativeModel('gemini-pro')


# --- HELPER FUNCTIONS (UPDATED) ---

def build_prompt(data):
    """Constructs a detailed prompt for the AI from request data."""
    prompt = f"Generate content with the following specifications:\n"
    prompt += f"- Title: {data.get('title', 'N/A')}\n"
    prompt += f"- Niche/Industry: {data.get('niche', 'N/A')}\n"
    if data.get('context'):
        prompt += f"- Context/Details: {data.get('context')}\n"
    # NEW: Include tags in the prompt
    if data.get('tags'):
        prompt += f"- Important Keywords/Tags to include: {data.get('tags')}\n"
    prompt += "\nPlease provide a comprehensive and well-structured piece of content."
    return prompt

def generate_text_from_ai(prompt):
    """Calls the Gemini API to generate text."""
    try:
        response = text_model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Gemini Text Gen Error: {e}")
        raise ValueError("Failed to generate text from AI.")

def generate_image_url_from_ai(prompt):
    """Simulates generating an image."""
    print(f"Simulating image generation for prompt: {prompt}")
    return "https://placehold.co/1024x1024/4f46e5/ffffff?text=AI+Generated+Image"


# --- MAIN HANDLER (UPDATED) ---
class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            auth_header = self.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                self.send_response(401); self.end_headers(); self.wfile.write(b'Unauthorized'); return

            id_token = auth_header.split('Bearer ')[1]
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token['uid']

            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            cost = 1 + (3 if data.get('generate_image') else 0)
            credits_doc_ref = db.collection('credits').document(user_id)
            credits_doc = credits_doc_ref.get()

            if not credits_doc.exists or credits_doc.to_dict().get('balance', 0) < cost:
                self.send_response(402); self.end_headers(); self.wfile.write(b'Insufficient credits'); return

            prompt = build_prompt(data)
            generated_text = generate_text_from_ai(prompt)
            image_url = None
            if data.get('generate_image'):
                image_prompt = f"An image for: {data.get('title')} in the {data.get('niche')} niche."
                image_url = generate_image_url_from_ai(image_prompt)

            @firestore.transactional
            def update_in_transaction(transaction, credits_ref, history_collection_ref):
                snapshot = credits_ref.get(transaction=transaction)
                new_balance = snapshot.to_dict()['balance'] - cost
                transaction.update(credits_ref, {'balance': new_balance})

                history_ref = history_collection_ref.document()
                # NEW: Save tags to the history document
                transaction.set(history_ref, {
                    'title': data.get('title'),
                    'niche': data.get('niche'),
                    'context': data.get('context'),
                    'tags': data.get('tags'), # Added tags
                    'generatedText': generated_text,
                    'imageUrl': image_url,
                    'createdAt': firestore.SERVER_TIMESTAMP
                })

            history_collection = db.collection('users').document(user_id).collection('history')
            update_in_transaction(db.transaction(), credits_doc_ref, history_collection)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_body = {"message": "Content generated successfully!"}
            self.wfile.write(json.dumps(response_body).encode('utf-8'))

        except auth.InvalidIdTokenError:
            self.send_response(401); self.end_headers(); self.wfile.write(b'Unauthorized: Invalid token')
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.send_response(500); self.end_headers(); self.wfile.write(f'Internal Server Error: {e}'.encode('utf-8'))