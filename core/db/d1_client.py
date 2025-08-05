import os
import subprocess
import json
from typing import List, Dict, Any, Optional

# This is a conceptual representation of the environment object
# that CloudFlare Workers provide. In a real worker, this would
# be available globally. We'll simulate it for local testing.
class SimulatedEnv:
    def __init__(self):
        self.DB = D1Database()
        
class D1Database:
    def prepare(self, query: str):
        return D1PreparedStatement(query)
    
class D1PreparedStatement:
    def __init__(self, query: str):
        self._query = query
        self._bindings = []
        
    def bind(self, *args):
        self._bindings = args
        return self
    
    def run(self):
        # This is where the actual local execution happens
        db_name = os.getenv('D1_DATABASE_NAME', 'ai-content-generator-db')
        command = [
            'wrangler', 'd1', 'execute', db_name,
            '--local',
            '--json',
            '--command', self._query
        ]
        
        # Add bindings to the command
        for binding in self._bindings:
            command.append(f'--param="{binding}"')
            
        try:
            result_json = subprocess.check_output(' '.join(command), shell=True)
            return json.loads(result_json)[0] # Wrangler wraps result in a list
        except subprocess.CalledProcessError as e:
            print(f"Error executing D1 command: {e}")
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
        """
        Prepares and executes a query, returning the full D1 response.
        """
        params = params or []
        stmt = self.db.prepare(query).bind(*params)
        return stmt.run()
    
    def fetch_one(self, query: str, params: Optional[List[Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Executes a query and returns the first result row as a dictionary, or None.
        """
        params = params or []
        stmt = self.db.prepare(query).bind(*params)
        return stmt.first()
    
    
    def fetch_all(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a query and returns all result rows as a list of dictionaries.
        """  
        response = self._execute(query, params)      
        return response.get('result', [])
    
    # --- High-Level Repository Methods ---
    # These methods provide a clean, ORM-like interface for our views.add()
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = ?1;"
        return self.fetch_one(query, [user_id])
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = ?1;"
        return self.fetch_one(query, [email])
    
    def create_user(self, username, email, password_hash, otp) -> Dict[str, Any]:
        query = """
                INSERT INTO users (username, email, password, email_otp, is_active)
                VALUES (?1, ?2, ?3, ?4, 0)
                RETURNING *;
        """
        return self.fetch_one(query, [username, email, password_hash, otp])
    
    def activate_user(self, user_id: int):
        query = "UPDATE users SET is_active = 1, is_verified = 1, email_otp = NULL WHERE id = ?1;"
        return self._execute(query, [user_id])
    

# A single instance to be used throughout the application
d1_client = D1Client()