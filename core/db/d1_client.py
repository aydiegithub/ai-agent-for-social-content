import os
import subprocess
import json
from typing import List, Dict, Any, Optional

# This is a conceptual representation of the environment object
# that CloudFlare Workers provide. In a real worker, this would
# be available globally. We'll simulate it for local testing.
class SimulatedEnv:
    def __init__(self):
        # In a real CF Worker, this would be bound in wrangler.toml
        # and provided by the environment.
        self.DB = D1Database()

class D1Database:
    def prepare(self, query: str):
        return D1PreparedStatement(query)

class D1PreparedStatement:
    def __init__(self, query: str):
        self._query = query
        self._bindings = []

    def bind(self, *args):
        # D1 bindings are 1-indexed, so we map them.
        self._bindings = list(args)
        return self

    def run(self):
        # This is where the actual local execution happens via wrangler
        db_name = os.getenv('D1_DATABASE_NAME', 'ai-content-generator-db')
        command = [
            'wrangler', 'd1', 'execute', db_name,
            '--local',
            '--json',
            '--command', f'"{self._query}"' # Wrap query in quotes
        ]
        
        # Add bindings to the command
        for binding in self._bindings:
            # Properly quote string bindings for the shell command
            param = f'"{binding}"' if isinstance(binding, str) else str(binding)
            command.append(f'--param={param}')

        try:
            # Use shell=True because wrangler commands can be complex
            result_json = subprocess.check_output(' '.join(command), shell=True, text=True, stderr=subprocess.PIPE)
            return json.loads(result_json)[0] # Wrangler wraps result in a list
        except subprocess.CalledProcessError as e:
            print(f"Error executing D1 command: {e}")
            print(f"Stderr: {e.stderr}")
            print(f"Command run: {' '.join(command)}")
            raise
        except (json.JSONDecodeError, IndexError) as e:
            print(f"Error parsing D1 response: {e}")
            print(f"Response JSON: {result_json}")
            raise

    def all(self):
        return self.run()

    def first(self, col: Optional[str] = None):
        response = self.run()
        results = response.get('results', [])
        if not results:
            return None
        if col:
            return results[0].get(col)
        return results[0]

# --- D1 Client ---
class D1Client:
    """
    A client for interacting with a CloudFlare D1 database.
    It abstracts away the differences between local development (using wrangler)
    and production (using the Fetch API provided by the CF Worker env).
    """
    def __init__(self):
        # In a real CloudFlare Worker, 'env' would be a global object
        # We check for its existance to determine the environment.
        # For now, we simulate it for local developement.
        self.env = globals().get('env', SimulatedEnv())
        self.db = self.env.DB
        print("D1Client initialized.")

    def _execute(self, query: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
        params = params or []
        stmt = self.db.prepare(query).bind(*params)
        return stmt.run()

    def fetch_one(self, query: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        params = params or []
        stmt = self.db.prepare(query).bind(*params)
        return stmt.first()

    def fetch_all(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        response = self._execute(query, params)
        return response.get('results', [])

    # --- High-Level Repository Methods ---

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = ?1;"
        return self.fetch_one(query, [user_id])
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = ?1;"
        return self.fetch_one(query, [email])

    def create_user(self, username, email, password_hash, otp) -> Dict[str, Any]:
        query = "INSERT INTO users (username, email, password, email_otp, is_active) VALUES (?1, ?2, ?3, ?4, 0) RETURNING *;"
        return self.fetch_one(query, [username, email, password_hash, otp])

    def activate_user(self, user_id: int):
        query = "UPDATE users SET is_active = 1, is_verified = 1, email_otp = NULL WHERE id = ?1;"
        return self._execute(query, [user_id])
        
    def get_or_create_user_credits(self, user_id: int) -> Dict[str, Any]:
        query_get = "SELECT * FROM credits WHERE user_id = ?1;"
        credits = self.fetch_one(query_get, [user_id])
        if credits:
            return credits
        query_create = "INSERT INTO credits (user_id, balance) VALUES (?1, 10) RETURNING *;"
        return self.fetch_one(query_create, [user_id])

    def get_content_history(self, user_id: int) -> List[Dict[str, Any]]:
        query = "SELECT * FROM content_history WHERE user_id = ?1 ORDER BY created_at DESC;"
        return self.fetch_all(query, [user_id])

    def create_content_history(self, user_id: int, title: str, input_params: Dict, generated_text: str, generated_image_url: Optional[str]) -> Dict[str, Any]:
        query = "INSERT INTO content_history (user_id, title, input_params, generated_text, generated_image_url) VALUES (?1, ?2, ?3, ?4, ?5) RETURNING *;"
        params_json = json.dumps(input_params)
        return self.fetch_one(query, [user_id, title, params_json, generated_text, generated_image_url])

    def update_user_credits(self, user_id: int, new_balance: int):
        query = "UPDATE credits SET balance = ?1 WHERE user_id = ?2;"
        return self._execute(query, [new_balance, user_id])

d1_client = D1Client()