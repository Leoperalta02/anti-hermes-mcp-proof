"""
Apex Luxury AI — Multi-Tenant Client Manager
Handles client provisioning, vertical configuration, asset tracking, and Vapi/Buzz mappings.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "tenants.json")

@dataclass
class Tenant:
    id: str
    name: str
    company_name: str
    vertical: str  # "FL_NO_FAULT_ACCIDENT", "LUXURY_REAL_ESTATE", "COMMERCIAL_FINANCE"
    phone_number: str
    subdomain_slug: str
    languages: List[str]  # ["es", "en"]
    tagline: str
    headshot_path: Optional[str] = None
    flyer_path: Optional[str] = None
    buzz_channel: Optional[str] = None
    vapi_assistant_id: Optional[str] = None
    google_drive_folder: Optional[str] = None
    custom_colors: Optional[Dict[str, str]] = None
    status: str = "ACTIVE"
    created_at: Optional[str] = None

class TenantManager:
    def __init__(self, data_path: str = DATA_PATH):
        self.data_path = data_path
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        self.tenants: Dict[str, Tenant] = {}
        self._load()
        if not self.tenants:
            self._init_default_tenants()

    def _load(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for t_data in data:
                        t = Tenant(**t_data)
                        self.tenants[t.id] = t
            except Exception as e:
                print(f"[TenantManager] Error loading tenants: {e}")

    def _save(self):
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump([asdict(t) for t in self.tenants.values()], f, indent=2)

    def _init_default_tenants(self):
        # 1. Sofia Lanz — Final Claim (Florida Accident / No-Fault)
        sofia = Tenant(
            id="tenant_sofia_lanz",
            name="Sofia Lanz",
            company_name="Final Claim",
            vertical="FL_NO_FAULT_ACCIDENT",
            phone_number="786-461-0049",
            subdomain_slug="sofia",
            languages=["es", "en"],
            tagline="Después de un Accidente, Estoy Aquí Para Ayudarte",
            headshot_path="assets/clients/sofia_headshot.png",
            flyer_path="assets/clients/sofia_flyer.png",
            buzz_channel="#client-sofia-lanz",
            custom_colors={"primary": "#d4af37", "secondary": "#0c1524"},
            status="ACTIVE",
            created_at="2026-08-28T11:00:00Z"
        )
        self.tenants[sofia.id] = sofia

        # 2. John "Toki" Grullon — The No Fault Group
        toki = Tenant(
            id="tenant_toki_grullon",
            name="John 'Toki' Grullon",
            company_name="The No Fault Group",
            vertical="FL_NO_FAULT_ACCIDENT",
            phone_number="786-683-4523",
            subdomain_slug="toki",
            languages=["en", "es"],
            tagline="After an Accident I Can Help You Get the Attention You Deserve",
            headshot_path="assets/clients/toki_headshot.png",
            flyer_path="assets/clients/toki_flyer.png",
            buzz_channel="#client-toki-grullon",
            custom_colors={"primary": "#06b6d4", "secondary": "#0a111e"},
            status="ACTIVE",
            created_at="2026-08-28T11:05:00Z"
        )
        self.tenants[toki.id] = toki

        # 3. Priscilla Vance — Vance Luxury Properties
        vance = Tenant(
            id="tenant_priscilla_vance",
            name="Priscilla Vance",
            company_name="Vance Luxury Properties",
            vertical="LUXURY_REAL_ESTATE",
            phone_number="305-555-0199",
            subdomain_slug="vance",
            languages=["en"],
            tagline="Curated Ultra-Luxury Real Estate & Private Estates",
            headshot_path="assets/hermes.png",
            buzz_channel="#client-vance-luxury",
            custom_colors={"primary": "#d4af37", "secondary": "#050608"},
            status="ACTIVE",
            created_at="2026-08-28T11:10:00Z"
        )
        self.tenants[vance.id] = vance

        # 4. Rosie Rivera — Rosie Rivera Luxury Real Estate
        rosie = Tenant(
            id="tenant_rosie_rivera",
            name="Rosie Rivera",
            company_name="Rosie Rivera Luxury Real Estate",
            vertical="LUXURY_REAL_ESTATE",
            phone_number="239-555-0144",
            subdomain_slug="rosie",
            languages=["en", "es"],
            tagline="Private Client Luxury Real Estate Advisor — Estero, Bonita Springs & Naples",
            headshot_path="assets/clients/rosie_headshot.png",
            buzz_channel="#client-rosie-rivera",
            custom_colors={"primary": "#d4af37", "secondary": "#080d1a"},
            status="ACTIVE",
            created_at="2026-09-04T00:00:00Z"
        )
        self.tenants[rosie.id] = rosie

        self._save()
        print("[TenantManager] Initialized default client tenants (Sofia Lanz, John Toki Grullon, Priscilla Vance, Rosie Rivera)")


    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        return self.tenants.get(tenant_id)

    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        for t in self.tenants.values():
            if t.subdomain_slug.lower() == slug.lower():
                return t
        return None

    def list_tenants(self) -> List[Tenant]:
        return list(self.tenants.values())

    def create_tenant(self, tenant: Tenant) -> Tenant:
        self.tenants[tenant.id] = tenant
        self._save()
        return tenant

tenant_manager = TenantManager()

if __name__ == "__main__":
    print(f"Loaded {len(tenant_manager.list_tenants())} tenants:")
    for t in tenant_manager.list_tenants():
        print(f" - {t.name} ({t.company_name}) -> Vertical: {t.vertical}, Phone: {t.phone_number}, Subdomain: {t.subdomain_slug}")
