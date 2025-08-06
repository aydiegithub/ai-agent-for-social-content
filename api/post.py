import os
import json
from http.server import BaseHTTPRequestHandler

import firebase_admin
from firebase_admin import credentials, auth, firestore

# --- INITIALIZATION ---
# This setup is the same as our generate.py function
cred_json = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT_KEY'))
cred = credentials.Certificate(cred_json)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# --- MAIN HANDLER ---
class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            # 1. Authenticate the user
            auth_header = self.headers.get('Authorization')
            id_token = auth_header.split('Bearer ')[1]
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token['uid']

            # 2. Get the request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            content_id = data.get('contentId')
            platform = data.get('platform')

            if not content_id or not platform:
                self.send_response(400); self.end_headers(); self.wfile.write(b'Missing contentId or platform'); return

            # 3. Check user's credits (cost is 1 per post)
            credits_doc_ref = db.collection('credits').document(user_id)
            credits_doc = credits_doc_ref.get()
            if not credits_doc.exists or credits_doc.to_dict().get('balance', 0) < 1:
                self.send_response(402); self.end_headers(); self.wfile.write(b'Insufficient credits for posting'); return

            # 4. Fetch the content and user's social tokens from Firestore
            content_doc_ref = db.collection('users').document(user_id).collection('history').document(content_id)
            content_doc = content_doc_ref.get()
            user_doc_ref = db.collection('users').document(user_id)
            user_doc = user_doc_ref.get()

            if not content_doc.exists or not user_doc.exists:
                self.send_response(404); self.end_headers(); self.wfile.write(b'Content or user not found'); return

            # 5. SIMULATION: Call the social media API
            # In a real app, you would use the stored tokens from user_doc to make a real API call.
            print(f"--- SIMULATING POST TO {platform.upper()} ---")
            print(f"User: {user_id}")
            print(f"Content: {content_doc.to_dict().get('generatedText')[:100]}...")
            # Here you would use a library like 'tweepy' for X or 'requests' for LinkedIn
            # Example: client = tweepy.Client(bearer_token=user_doc.to_dict().get('x_access_token'))
            # client.create_tweet(text=content_doc.to_dict().get('generatedText'))
            print("--- SIMULATION SUCCESSFUL ---")

            # 6. Deduct credit
            new_balance = credits_doc.to_dict()['balance'] - 1
            credits_doc_ref.update({'balance': new_balance})
            
            # 7. Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": f"Successfully posted to {platform}"}).encode('utf-8'))

        except Exception as e:
            print(f"An unexpected error occurred in post API: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f'Internal Server Error: {e}'.encode('utf-8'))