"""
supabase_agent.py
Autonomous Supabase Database Provisioning Agent for Apex Luxury AI.
This agent uses the vaulted Supabase API keys to create tables and manage data.
"""

import os
import json
import psycopg2
from supabase import create_client, Client

class SupabaseAutonomousAgent:
    """
    Agent that autonomously verifies Supabase DB connectivity,
    and manages tables and data for newly onboarded Realtors and Accident Referral Agents.
    """

    def __init__(self):
        self.project_url = ""
        self.service_role_key = ""
        self.db_password = ""
        self.db_host = ""
        self._load_credentials()
        
        if self.project_url and self.service_role_key:
            self.supabase: Client = create_client(self.project_url, self.service_role_key)
        else:
            self.supabase = None

    def _load_credentials(self):
        vault_path = os.path.join(os.path.dirname(__file__), "..", "vault_backup", "vault_secrets.json")
        try:
            with open(vault_path, "r") as f:
                secrets = json.load(f)
                self.project_url = secrets.get("supabase_project_url", "")
                self.service_role_key = secrets.get("supabase_service_role_key", "")
                self.db_password = secrets.get("supabase_db_password", "")
                
                # Extract DB host from URL
                if self.project_url:
                    parts = self.project_url.split("//")[-1].split(".")
                    self.db_host = f"db.{parts[0]}.supabase.co"
        except Exception as e:
            print(f"[Supabase Agent] Error loading credentials: {e}")

    def test_connection(self) -> dict:
        """
        Tests connection to the Supabase database.
        """
        if not self.supabase:
            return {"status": "ERROR", "message": "Credentials not loaded."}
            
        try:
            # Simple query to test connection
            response = self.supabase.table('tenants').select("*").limit(1).execute()
            return {
                "status": "CONNECTED",
                "agent": "@Buzz-Database-Agent",
                "message": "Successfully authenticated with Supabase Database!"
            }
        except Exception as e:
            error_str = str(e)
            if "relation \"public.tenants\" does not exist" in error_str or "Could not find the table" in error_str:
                return {
                    "status": "CONNECTED_NO_TABLES",
                    "agent": "@Buzz-Database-Agent",
                    "message": "Connected successfully, but tables are not yet provisioned."
                }
            return {"status": "ERROR", "message": error_str}

    def provision_tables(self) -> dict:
        """
        Connects via psycopg2 to provision the required tables if they don't exist.
        """
        if not self.db_host or not self.db_password:
            return {"status": "ERROR", "message": "Database host or password missing."}
            
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=self.db_password,
                host=self.db_host,
                port="5432"
            )
            cur = conn.cursor()
            
            # Create tenants table (supporting Realtors & Accident/Claims agents)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    name VARCHAR(255) NOT NULL,
                    company_name VARCHAR(255),
                    vertical VARCHAR(100) NOT NULL, -- "FL_NO_FAULT_ACCIDENT" or "LUXURY_REAL_ESTATE"
                    phone VARCHAR(50),
                    subdomain VARCHAR(100) UNIQUE,
                    onboarded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Create generic leads table mapping to tenants
            cur.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    tenant_id UUID REFERENCES tenants(id),
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    location VARCHAR(255),
                    language VARCHAR(10) DEFAULT 'en',
                    details TEXT, -- Accident details or Real Estate preferences
                    status VARCHAR(50) DEFAULT 'NEW',
                    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            conn.commit()
            cur.close()
            conn.close()
            
            return {
                "status": "SUCCESS",
                "message": "Tables 'tenants' and 'leads' provisioned successfully in Supabase."
            }
        except Exception as e:
            return {"status": "ERROR", "message": f"Table provisioning failed: {str(e)}"}

    def provision_tenant_data(self, tenant_data: dict) -> dict:
        if not self.supabase:
            return {"status": "ERROR", "message": "Credentials not loaded."}
        try:
            response = self.supabase.table('tenants').insert(tenant_data).execute()
            return {
                "status": "SUCCESS",
                "data": response.data,
                "message": f"Successfully provisioned tenant: {tenant_data.get('name')}"
            }
        except Exception as e:
            return {"status": "ERROR", "message": str(e)}

if __name__ == "__main__":
    agent = SupabaseAutonomousAgent()
    print("=== SUPABASE AUTONOMOUS AGENT TEST ===")
    res = agent.test_connection()
    print(json.dumps(res, indent=2))
    
    print("\n=== PROVISIONING TABLES ===")
    prov_res = agent.provision_tables()
    print(json.dumps(prov_res, indent=2))
