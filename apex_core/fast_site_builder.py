"""
Apex Luxury AI — Autonomous Fast Site Builder (Fizz Engine)
Generates high-converting live landing pages for real estate, Florida No-Fault, and PIP clients.
Trained on Apple Design Principles (apple.com, apple.com/business).
"""

import os
import sys
import json
from typing import Dict, Any, Optional

# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apex_core.tenant_manager import tenant_manager, Tenant

PUBLIC_SITES_DIR = os.path.join(os.path.dirname(__file__), "..", "public_sites")

class FastSiteBuilder:
    def __init__(self, output_dir: str = PUBLIC_SITES_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    @staticmethod
    def load_playbook() -> Dict[str, Any]:
        playbook_path = os.path.join(os.path.dirname(__file__), "office_playbook.json")
        if os.path.exists(playbook_path):
            try:
                with open(playbook_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and data:
                        return data
            except Exception as e:
                print(f"[FastSiteBuilder] Warning reading {playbook_path}: {e}")
        return {}

    @staticmethod
    def load_listings() -> list:
        listings_path = os.path.join(os.path.dirname(__file__), "office_listings.json")
        if os.path.exists(listings_path):
            try:
                with open(listings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and data:
                        return data
            except Exception as e:
                print(f"[FastSiteBuilder] Warning reading {listings_path}: {e}")
        return []

    @staticmethod
    def load_intake_queue(tenant_slug: Optional[str] = None) -> list:
        """Load pending listing intake queue entries for portal embedding."""
        queue_path = os.path.join(os.path.dirname(__file__), "listing_intake_queue.json")
        if not os.path.exists(queue_path):
            return []
        try:
            with open(queue_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            pending = [e for e in data if e.get("queue_status") == "PENDING_APPROVAL"]
            if tenant_slug:
                slug = tenant_slug.strip().lower()
                pending = [
                    e for e in pending
                    if str(e.get("listing", {}).get("tenant_slug", "rosie")).lower() == slug
                ]
            return pending
        except Exception as e:
            print(f"[FastSiteBuilder] Warning reading {queue_path}: {e}")
            return []

    def build_site(self, tenant: Tenant) -> str:
        site_folder = os.path.join(self.output_dir, tenant.subdomain_slug)
        os.makedirs(site_folder, exist_ok=True)
        os.makedirs(os.path.join(site_folder, "assets"), exist_ok=True)

        # Copy client assets to site folder if they exist
        if tenant.headshot_path and os.path.exists(tenant.headshot_path):
            import shutil
            shutil.copyfile(tenant.headshot_path, os.path.join(site_folder, "assets", "headshot.png"))
        if tenant.flyer_path and os.path.exists(tenant.flyer_path):
            import shutil
            shutil.copyfile(tenant.flyer_path, os.path.join(site_folder, "assets", "flyer.png"))

        # Generate HTML based on vertical
        if tenant.vertical == "FL_NO_FAULT_ACCIDENT":
            html = self._generate_accident_pip_html(tenant)
        else:
            html = self._generate_luxury_realty_html(tenant)

        index_file = os.path.join(site_folder, "index.html")
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html)

        portal_file = self.build_portal(tenant)
        print(f"[FastSiteBuilder] Deployed landing page for {tenant.name} -> {index_file}")
        print(f"[FastSiteBuilder] Deployed private portal for {tenant.name} -> {portal_file}")
        return index_file

    def _generate_accident_pip_html(self, t: Tenant) -> str:
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t.company_name} | {t.name} — Asistencia de Accidentes 24/7</title>
  <meta name="description" content="{t.tagline}. Te conectamos con los mejores médicos y abogados de accidentes en Florida.">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Outfit:wght@600;700;800;900&display=swap" rel="stylesheet">
  
  <style>
    :root {{
      --bg-dark: #080d1a;
      --bg-card: rgba(16, 24, 40, 0.85);
      --gold-primary: #d4af37;
      --gold-gradient: linear-gradient(135deg, #fae596 0%, #d4af37 50%, #aa820a 100%);
      --cyan-accent: #06b6d4;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --danger: #ef4444;
      --success: #10b981;
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
    body {{ background: var(--bg-dark); color: var(--text-main); min-height: 100vh; overflow-x: hidden; }}
    
    .container {{ max-width: 1100px; margin: 0 auto; padding: 0 1.5rem; }}
    
    /* Nav */
    .navbar {{ display: flex; justify-content: space-between; align-items: center; padding: 1.5rem 0; border-bottom: 1px solid rgba(212,175,55,0.15); }}
    .brand {{ font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: #fff; text-transform: uppercase; }}
    .brand span {{ color: var(--gold-primary); }}
    
    /* Emergency Bar */
    .pip-alert-bar {{
      background: rgba(239, 68, 68, 0.12);
      border: 1px solid rgba(239, 68, 68, 0.35);
      padding: 0.85rem 1.25rem;
      border-radius: 8px;
      margin: 1.5rem 0 2.5rem 0;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      font-size: 0.95rem;
      color: #fca5a5;
    }}
    
    /* Hero */
    .hero-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; margin-bottom: 4rem; }}
    .hero-title {{ font-family: 'Outfit', sans-serif; font-size: 3.25rem; line-height: 1.1; margin-bottom: 1rem; font-weight: 900; }}
    .gold-text {{ background: var(--gold-gradient); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero-desc {{ font-size: 1.15rem; color: var(--text-muted); margin-bottom: 2rem; line-height: 1.6; }}
    
    /* Profile Image Box */
    .profile-card {{
      background: var(--bg-card);
      border: 1px solid rgba(212,175,55,0.3);
      border-radius: 20px;
      overflow: hidden;
      box-shadow: 0 20px 40px rgba(0,0,0,0.8), 0 0 30px rgba(212,175,55,0.2);
      text-align: center;
    }}
    .profile-img {{ width: 100%; height: 380px; object-fit: cover; }}
    .profile-body {{ padding: 1.5rem; }}
    
    /* Buttons */
    .btn-call {{
      background: var(--gold-gradient);
      color: #080d1a;
      font-size: 1.25rem;
      font-weight: 800;
      font-family: 'Outfit', sans-serif;
      padding: 1.15rem 2rem;
      border-radius: 12px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.75rem;
      box-shadow: 0 8px 25px rgba(212,175,55,0.4);
      transition: transform 0.2s;
    }}
    .btn-call:hover {{ transform: translateY(-3px); }}
    
    /* Intake Form Card */
    .intake-card {{
      background: var(--bg-card);
      border: 1px solid rgba(212,175,55,0.2);
      border-radius: 16px;
      padding: 2.5rem;
      margin-bottom: 4rem;
    }}
    .form-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.25rem; margin-bottom: 1.25rem; }}
    .form-input {{
      width: 100%;
      background: rgba(8, 13, 26, 0.9);
      border: 1px solid rgba(212,175,55,0.2);
      border-radius: 8px;
      padding: 0.9rem 1rem;
      color: #fff;
      font-size: 1rem;
      outline: none;
    }}
    .form-input:focus {{ border-color: var(--gold-primary); }}
    
    /* Features Grid */
    .features-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-bottom: 4rem; }}
    .feature-box {{
      background: var(--bg-card);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 12px;
      padding: 1.75rem;
      text-align: center;
    }}
    .feature-icon {{ font-size: 2rem; margin-bottom: 0.75rem; }}
    .feature-title {{ font-family: 'Outfit', sans-serif; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--gold-primary); }}
    
    /* Footer */
    .footer {{ text-align: center; padding: 3rem 0; border-top: 1px solid rgba(255,255,255,0.08); color: var(--text-muted); font-size: 0.85rem; }}
    
    @media (max-width: 800px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .form-row {{ grid-template-columns: 1fr; }}
      .features-grid {{ grid-template-columns: 1fr; }}
      .hero-title {{ font-size: 2.5rem; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Navbar -->
    <header class="navbar">
      <div class="brand">{t.company_name} <span>24/7</span></div>
      <a href="tel:{t.phone_number.replace('-', '')}" class="btn-call" style="font-size: 1rem; padding: 0.65rem 1.25rem;">
        <span>📞 {t.phone_number}</span>
      </a>
    </header>

    <!-- Florida PIP 14-Day Countdown Bar -->
    <div class="pip-alert-bar">
      <span>⚠️</span>
      <div>
        <strong>¡Ley de Florida (Regla de los 14 Días)!</strong> Debe recibir evaluación médica dentro de los 14 días posteriores al accidente para activar sus <strong>$10,000 en beneficios médicos (PIP)</strong>.
      </div>
    </div>

    <!-- Hero Section -->
    <section class="hero-grid">
      <div>
        <h1 class="hero-title">DESPUÉS DE UN <br><span class="gold-text">ACCIDENTE</span><br>Estoy Aquí Para Ayudarte</h1>
        <p class="hero-desc">
          Te conecto de inmediato con los <strong>mejores médicos especialistas y abogados de accidentes</strong> en Florida para que recibas la atención médica y compensación que mereces.
        </p>
        
        <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
          <a href="tel:{t.phone_number.replace('-', '')}" class="btn-call">
            <span>🚨 Llamar Ahora 24/7 ({t.phone_number})</span>
          </a>
          <div style="font-size: 0.85rem; color: var(--success); display: flex; align-items: center; gap: 0.4rem;">
            <span>● Asistente de Voz IA Activa en Español</span>
          </div>
        </div>
      </div>

      <!-- Profile Card -->
      <div class="profile-card">
        <img src="assets/headshot.png" alt="{t.name}" class="profile-img" onerror="this.src='../../assets/clients/sofia_headshot.png'">
        <div class="profile-body">
          <h3 style="font-family: 'Outfit', sans-serif; font-size: 1.5rem; font-weight: 800; color: #fff;">{t.name}</h3>
          <div style="font-size: 0.9rem; color: var(--gold-primary); text-transform: uppercase; font-weight: 700; margin-top: 0.25rem;">
            Tu Enlace de Confianza en Florida
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">
            Confidencialidad Garantizada &bull; Atención en Todo Florida
          </div>
        </div>
      </div>
    </section>

    <!-- 3 Core Advantages -->
    <section class="features-grid">
      <div class="feature-box">
        <div class="feature-icon">🏥</div>
        <div class="feature-title">Evaluación Médica Inmediata</div>
        <p style="font-size: 0.9rem; color: var(--text-muted);">
          Coordinamos tu cita con clínicas y quiroprácticos certificados antes de que venza el plazo de los 14 días.
        </p>
      </div>
      <div class="feature-box">
        <div class="feature-icon">⚖️</div>
        <div class="feature-title">Abogados de Confianza</div>
        <p style="font-size: 0.9rem; color: var(--text-muted);">
          Te referimos con firmas legales de primera línea para proteger tus derechos sin costos de tu bolsillo.
        </p>
      </div>
      <div class="feature-box">
        <div class="feature-icon">🚗</div>
        <div class="feature-title">Gestión de Grúa y Transporte</div>
        <p style="font-size: 0.9rem; color: var(--text-muted);">
          Te orientamos en la gestión de transporte y reclamos de daños a tu vehículo.
        </p>
      </div>
    </section>

    <!-- Emergency Intake Form -->
    <section class="intake-card">
      <h2 style="font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; margin-bottom: 0.5rem; text-align: center;">
        Registro Rápido de <span class="gold-text">Accidente en 60 Segundos</span>
      </h2>
      <p style="text-align: center; color: var(--text-muted); margin-bottom: 2rem;">
        Completa los datos y nuestro equipo te contactará en menos de 2 minutos.
      </p>

      <form id="pip-form">
        <div class="form-row">
          <input type="text" class="form-input" placeholder="Nombre y Apellido" required>
          <input type="tel" class="form-input" placeholder="Teléfono de Contacto" required>
        </div>
        <div class="form-row">
          <input type="text" class="form-input" placeholder="Ciudad del Accidente (Ej: Miami, Orlando)" required>
          <input type="date" class="form-input" placeholder="Fecha del Accidente" required>
        </div>
        <button type="submit" class="btn-call" style="width: 100%; justify-content: center; border: none; cursor: pointer;">
          <span>📋 Enviar Reclamo y Recibir Ayuda Inmediata</span>
        </button>
      </form>
    </section>

    <!-- Footer & Disclaimer -->
    <footer class="footer">
      <p style="margin-bottom: 0.75rem;">
        <strong>Aviso Legal Importante:</strong> {t.name} y {t.company_name} no son firmas de abogados y no ofrecen asesoría legal directa. Nuestro servicio es conectar a víctimas de accidentes con profesionales médicos y legales independientes y autorizados en el Estado de Florida.
      </p>
      <p>&copy; 2026 {t.company_name} — Powered by Apex Luxury AI Autonomous Workforce.</p>
    </footer>

  </div>
</body>
</html>"""

    def _generate_luxury_realty_html(self, t: Tenant) -> str:
        listings = self.load_listings()
        estate_cards_html = ""
        for item in listings:
            status_cls = item.get("status_pill_class", "status-for-sale")
            sqft_fmt = f"{item['sqft']:,}"
            waterfront_txt = item.get("waterfront", "Prime Location")
            estate_cards_html += f"""
        <div class="estate-card" data-category="{item['status']}" data-id="{item['id']}" onclick="openEstateModal('{item['id']}')">
          <div class="estate-media-wrap">
            <img src="{item['primary_image']}" alt="{item['title']}" class="estate-card-img" loading="lazy">
            <div class="estate-status-badge {status_cls}">{item['status_label']}</div>
            <div class="estate-price-pill">{item['price']}</div>
          </div>
          <div class="estate-card-body">
            <h3 class="estate-title">{item['title']}</h3>
            <div class="estate-submarket">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
              {item['neighborhood']}
            </div>
            <div class="estate-specs-grid">
              <span class="spec-pill">{item['beds']} Beds</span>
              <span class="spec-pill">{item['baths']} Baths</span>
              <span class="spec-pill">{sqft_fmt} SqFt</span>
              <span class="spec-pill">{waterfront_txt}</span>
            </div>
            <p class="estate-brief">{item['tagline']}</p>
            <div class="estate-action-row">
              <span class="estate-explore-link">Explore Dossier <span>›</span></span>
              <button class="estate-card-btn" onclick="event.stopPropagation(); openEstateModal('{item['id']}')">View Estate</button>
            </div>
          </div>
        </div>"""

        listings_json_str = json.dumps(listings)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t.name} | {t.company_name} — Private Client Luxury Real Estate</title>
  <meta name="description" content="{t.tagline}. High-end real estate advisory across Estero, Bonita Springs, and Naples, Florida.">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {{
      --bg-canvas: #000000;
      --bg-surface: #0a0a0c;
      --bg-card: rgba(22, 22, 26, 0.72);
      --bg-card-hover: rgba(30, 30, 36, 0.85);
      --text-primary: #f5f5f7;
      --text-secondary: #86868b;
      --gold-accent: #e5c890;
      --gold-gradient: linear-gradient(135deg, #f7e7c4 0%, #e5c890 50%, #b89547 100%);
      --hairline: rgba(255, 255, 255, 0.09);
      --hairline-hover: rgba(229, 200, 144, 0.35);
      --apple-blue: #2997ff;
      --apple-radius: 28px;
      --pill-radius: 980px;
    }}
    
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", sans-serif;
      background-color: var(--bg-canvas);
      color: var(--text-primary);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
      overflow-x: hidden;
    }}

    .container {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 2rem;
    }}

    /* Global Apple Frosted Glass Header with Slide-Down Flyout */
    .apple-nav {{
      position: sticky;
      top: 0;
      z-index: 1000;
      background: rgba(0, 0, 0, 0.85);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border-bottom: 1px solid var(--hairline);
      transition: background 0.3s ease;
    }}
    .nav-inner {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0.85rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: relative;
    }}
    .brand-mark {{
      font-size: 1.05rem;
      font-weight: 600;
      letter-spacing: -0.01em;
      color: var(--text-primary);
      display: flex;
      align-items: center;
      gap: 0.6rem;
      text-decoration: none;
    }}
    .brand-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--gold-accent);
      box-shadow: 0 0 10px rgba(229, 200, 144, 0.6);
    }}
    .nav-actions {{
      display: flex;
      align-items: center;
      gap: 2rem;
    }}
    
    /* Apple Dropdown Trigger */
    .nav-item-dropdown {{
      position: static;
    }}
    .nav-link {{
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.88rem;
      font-weight: 400;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      padding: 0.85rem 0.5rem;
      margin-bottom: -0.85rem;
      cursor: pointer;
      transition: color 0.2s ease;
      position: relative;
    }}
    .nav-link:hover, .nav-item-dropdown:hover .nav-link {{
      color: var(--text-primary);
    }}
    .nav-link svg {{
      transition: transform 0.25s ease;
    }}
    .nav-item-dropdown:hover .nav-link svg {{
      transform: rotate(180deg);
    }}

    /* Apple Full-Width Liquid Glass Slide-Down Flyout Menu */
    .apple-flyout {{
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: rgba(10, 10, 14, 0.97);
      backdrop-filter: blur(35px);
      -webkit-backdrop-filter: blur(35px);
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 40px 80px rgba(0, 0, 0, 0.9);
      max-height: 0;
      opacity: 0;
      visibility: hidden;
      transform: translateY(-8px);
      pointer-events: none;
      transition: max-height 0.35s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease, transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.35s ease;
      z-index: 999;
    }}
    /* Hover buffer bridge - uninterrupted invisible hit-catcher between nav and flyout */
    .apple-flyout::before {{
      content: '';
      position: absolute;
      top: -35px;
      left: 0;
      right: 0;
      height: 40px;
      background: transparent;
      z-index: 1001;
      pointer-events: auto;
    }}
    .nav-item-dropdown:hover .apple-flyout,
    .nav-item-dropdown:focus-within .apple-flyout,
    .apple-flyout:hover,
    .apple-flyout.is-open {{
      max-height: 520px;
      opacity: 1;
      visibility: visible;
      transform: translateY(0);
      pointer-events: auto;
    }}
    
    .flyout-container {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 2.8rem 2rem 3.2rem 2rem;
      display: grid;
      grid-template-columns: 1.2fr 1fr 1fr;
      gap: 3rem;
      text-align: left;
    }}
    .flyout-col-title {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-secondary);
      margin-bottom: 1.25rem;
      font-weight: 600;
    }}
    .flyout-link-stack {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}
    .flyout-big-link {{
      color: var(--text-primary);
      text-decoration: none;
      font-size: 1.25rem;
      font-weight: 600;
      letter-spacing: -0.015em;
      transition: all 0.2s ease;
      display: block;
    }}
    .flyout-big-link:hover {{
      color: var(--gold-accent);
      transform: translateX(4px);
    }}
    .flyout-sub-link {{
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.88rem;
      transition: color 0.2s ease;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.35rem 0;
    }}
    .flyout-sub-link:hover {{
      color: var(--text-primary);
    }}
    .flyout-sub-link span {{
      font-size: 0.75rem;
      color: var(--gold-accent);
    }}

    /* Dim Background Overlay on Menu Open */
    .apple-page-scrim {{
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.35s ease;
      z-index: 900;
    }}

    .pill-btn-small {{
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-primary);
      padding: 0.45rem 1.15rem;
      border-radius: var(--pill-radius);
      font-size: 0.82rem;
      font-weight: 500;
      text-decoration: none;
      border: 1px solid var(--hairline);
      transition: all 0.25s ease;
    }}
    .pill-btn-small:hover {{
      background: var(--text-primary);
      color: #000;
      transform: scale(1.02);
    }}

    /* Cinematic Apple Hero Section */
    .hero {{
      padding: 6.5rem 0 5rem 0;
      text-align: center;
    }}
    .hero-eyebrow {{
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-weight: 600;
      color: var(--gold-accent);
      margin-bottom: 1.25rem;
      display: inline-block;
    }}
    .hero-title {{
      font-size: clamp(2.8rem, 5.8vw, 4.6rem);
      font-weight: 600;
      letter-spacing: -0.025em;
      line-height: 1.06;
      max-width: 900px;
      margin: 0 auto;
      color: var(--text-primary);
    }}
    .hero-subtitle {{
      font-size: clamp(1.15rem, 2vw, 1.35rem);
      font-weight: 400;
      line-height: 1.45;
      color: var(--text-secondary);
      max-width: 680px;
      margin: 1.5rem auto 2.5rem auto;
    }}
    .hero-cta-group {{
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 1.5rem;
      margin-bottom: 4rem;
    }}
    .pill-btn-primary {{
      background: var(--text-primary);
      color: #000000;
      font-weight: 500;
      font-size: 1rem;
      padding: 0.85rem 2rem;
      border-radius: var(--pill-radius);
      text-decoration: none;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .pill-btn-primary:hover {{
      transform: scale(1.03);
      box-shadow: 0 10px 30px rgba(255, 255, 255, 0.2);
    }}
    .apple-link-cta {{
      color: var(--gold-accent);
      font-size: 1rem;
      font-weight: 400;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      transition: gap 0.2s ease, opacity 0.2s ease;
    }}
    .apple-link-cta:hover {{
      opacity: 0.85;
      gap: 0.55rem;
    }}

    /* Hero Visual Showcase Card */
    .hero-display-stage {{
      position: relative;
      border-radius: var(--apple-radius);
      overflow: hidden;
      border: 1px solid var(--hairline);
      background: var(--bg-surface);
      box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8);
      max-width: 1060px;
      margin: 0 auto;
    }}
    .stage-image {{
      width: 100%;
      height: 480px;
      object-fit: cover;
      display: block;
      filter: brightness(0.92) contrast(1.05);
    }}
    .stage-overlay {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 2.5rem;
      background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.92) 100%);
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      text-align: left;
    }}
    .stage-advisor {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }}
    .stage-avatar {{
      width: 68px;
      height: 68px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid var(--gold-accent);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6);
    }}
    .stage-name {{
      font-size: 1.3rem;
      font-weight: 600;
      letter-spacing: -0.01em;
      color: #ffffff;
    }}
    .stage-desc {{
      font-size: 0.85rem;
      color: var(--text-secondary);
    }}
    .stage-badge {{
      background: rgba(255, 255, 255, 0.08);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--hairline);
      padding: 0.6rem 1.2rem;
      border-radius: var(--pill-radius);
      font-size: 0.8rem;
      color: var(--gold-accent);
      font-weight: 500;
    }}

    /* Apple Bento Chapter Grid */
    .section-chapter {{
      padding: 7rem 0;
    }}
    .chapter-eyebrow {{
      text-align: center;
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--gold-accent);
      font-weight: 600;
      margin-bottom: 0.75rem;
    }}
    .chapter-title {{
      text-align: center;
      font-size: clamp(2.2rem, 4vw, 3.2rem);
      font-weight: 600;
      letter-spacing: -0.02em;
      line-height: 1.12;
      margin-bottom: 3.5rem;
      color: var(--text-primary);
    }}
    .bento-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.5rem;
    }}
    .bento-card {{
      background: var(--bg-card);
      border: 1px solid var(--hairline);
      border-radius: var(--apple-radius);
      padding: 2.8rem 2.2rem;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .bento-card:hover {{
      background: var(--bg-card-hover);
      border-color: var(--hairline-hover);
      transform: translateY(-4px);
    }}
    .bento-card.span-2 {{
      grid-column: span 2;
    }}
    .bento-tag {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--gold-accent);
      font-weight: 600;
      margin-bottom: 1rem;
    }}
    .bento-headline {{
      font-size: 1.45rem;
      font-weight: 600;
      letter-spacing: -0.015em;
      line-height: 1.25;
      color: var(--text-primary);
      margin-bottom: 0.85rem;
    }}
    .bento-text {{
      font-size: 0.95rem;
      color: var(--text-secondary);
      line-height: 1.5;
    }}

    /* Apple-Style Interactive Valuation Engine */
    .cma-section {{
      padding: 6rem 0;
      border-top: 1px solid var(--hairline);
      border-bottom: 1px solid var(--hairline);
      background: var(--bg-surface);
    }}
    .cma-box {{
      background: var(--bg-card);
      border: 1px solid var(--hairline);
      border-radius: var(--apple-radius);
      padding: 3.5rem 3rem;
      max-width: 960px;
      margin: 0 auto;
    }}
    .cma-display {{
      text-align: center;
      margin-bottom: 3rem;
    }}
    .cma-val-title {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--gold-accent);
      margin-bottom: 0.5rem;
    }}
    .cma-price-hero {{
      font-size: clamp(3rem, 6vw, 4.8rem);
      font-weight: 600;
      letter-spacing: -0.03em;
      color: var(--text-primary);
      font-variant-numeric: tabular-nums;
      margin-bottom: 0.5rem;
    }}
    .cma-price-sub {{
      font-size: 0.95rem;
      color: var(--text-secondary);
    }}

    .cma-controls {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      align-items: center;
      margin-bottom: 2.5rem;
      padding: 1.5rem 0;
      border-top: 1px solid var(--hairline);
      border-bottom: 1px solid var(--hairline);
    }}
    .control-label {{
      font-size: 0.85rem;
      font-weight: 500;
      color: var(--text-primary);
      margin-bottom: 0.6rem;
      display: flex;
      justify-content: space-between;
    }}
    .slider-val {{
      color: var(--gold-accent);
      font-weight: 600;
    }}
    .apple-slider {{
      -webkit-appearance: none;
      width: 100%;
      height: 5px;
      border-radius: 5px;
      background: rgba(255, 255, 255, 0.15);
      outline: none;
      transition: background 0.2s;
    }}
    .apple-slider::-webkit-slider-thumb {{
      -webkit-appearance: none;
      appearance: none;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: #ffffff;
      cursor: pointer;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
      transition: transform 0.15s ease;
    }}
    .apple-slider::-webkit-slider-thumb:hover {{
      transform: scale(1.15);
    }}
    .apple-select {{
      width: 100%;
      padding: 0.75rem 1rem;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--hairline);
      color: var(--text-primary);
      font-size: 0.95rem;
      outline: none;
      font-family: inherit;
    }}

    /* Confidential Direct Intake */
    .intake-section {{
      padding: 7rem 0 9rem 0;
      text-align: center;
    }}
    .intake-card {{
      background: var(--bg-card);
      border: 1px solid var(--hairline);
      border-radius: var(--apple-radius);
      padding: 3.5rem 3rem;
      max-width: 680px;
      margin: 0 auto;
      text-align: left;
    }}
    .form-group {{
      margin-bottom: 1.5rem;
    }}
    .form-label {{
      display: block;
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text-secondary);
      margin-bottom: 0.5rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .apple-input {{
      width: 100%;
      padding: 0.85rem 1.2rem;
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--hairline);
      color: #ffffff;
      font-size: 0.95rem;
      outline: none;
      font-family: inherit;
      transition: border-color 0.2s;
    }}
    .apple-input:focus {{
      border-color: var(--gold-accent);
      background: rgba(255, 255, 255, 0.07);
    }}

    /* Apple Minimalist Footer & Disclaimers */
    .apple-footer {{
      padding: 4rem 0 3rem 0;
      border-top: 1px solid var(--hairline);
      color: var(--text-secondary);
      font-size: 0.75rem;
      line-height: 1.6;
    }}
    .footer-disclaimer {{
      margin-bottom: 1.5rem;
    }}
    .footer-line {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 1.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }}

    @media (max-width: 900px) {{
      .bento-grid {{ grid-template-columns: 1fr; }}
      .bento-card.span-2 {{ grid-column: span 1; }}
      .cma-controls {{ grid-template-columns: 1fr; }}
      .hero-cta-group {{ flex-direction: column; }}
      .stage-overlay {{ flex-direction: column; align-items: flex-start; gap: 1rem; }}
    }}
    /* =========================================================
       Apple-Style Kinetic Estates Showcase
       ========================================================= */
    .estates-section {{
      padding: 6rem 0 7rem 0;
      position: relative;
      overflow: hidden;
      background: linear-gradient(180deg, #000000 0%, #08080a 50%, #000000 100%);
      border-top: 1px solid var(--hairline);
      border-bottom: 1px solid var(--hairline);
    }}
    .estates-header-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 2rem;
      gap: 2rem;
    }}
    .estates-eyebrow {{
      font-size: 0.85rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--gold-accent);
      margin-bottom: 0.65rem;
    }}
    .estates-headline {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      font-size: 2.8rem;
      font-weight: 700;
      line-height: 1.1;
      letter-spacing: -0.025em;
      color: var(--text-primary);
    }}
    .carousel-nav-controls {{
      display: flex;
      align-items: center;
      gap: 0.85rem;
      flex-shrink: 0;
    }}
    .carousel-nav-btn {{
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: rgba(30, 30, 36, 0.75);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--hairline);
      color: var(--text-primary);
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      outline: none;
    }}
    .carousel-nav-btn:hover {{
      background: rgba(229, 200, 144, 0.2);
      border-color: var(--gold-accent);
      color: #ffffff;
      transform: scale(1.06);
    }}
    .carousel-nav-btn:active {{
      transform: scale(0.96);
    }}

    .estate-filter-bar {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 2.5rem;
      overflow-x: auto;
      padding-bottom: 0.5rem;
      scrollbar-width: none;
    }}
    .estate-filter-bar::-webkit-scrollbar {{ display: none; }}
    .filter-pill {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--hairline);
      color: var(--text-secondary);
      font-size: 0.88rem;
      font-weight: 500;
      padding: 0.55rem 1.25rem;
      border-radius: var(--pill-radius);
      cursor: pointer;
      transition: all 0.25s ease;
      white-space: nowrap;
      outline: none;
    }}
    .filter-pill:hover {{
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-primary);
      border-color: rgba(255, 255, 255, 0.2);
    }}
    .filter-pill.active {{
      background: var(--gold-gradient);
      color: #0b0c10;
      font-weight: 700;
      border-color: transparent;
      box-shadow: 0 4px 18px rgba(229, 200, 144, 0.35);
    }}

    .estates-carousel-wrapper {{
      position: relative;
      width: 100vw;
      margin-left: calc(-50vw + 50%);
      margin-right: calc(-50vw + 50%);
      overflow: hidden;
    }}
    .carousel-scrim-left, .carousel-scrim-right {{
      position: absolute;
      top: 0;
      bottom: 0;
      width: 6vw;
      z-index: 10;
      pointer-events: none;
    }}
    .carousel-scrim-left {{
      left: 0;
      background: linear-gradient(90deg, #000000 0%, rgba(0, 0, 0, 0) 100%);
    }}
    .carousel-scrim-right {{
      right: 0;
      background: linear-gradient(270deg, #000000 0%, rgba(0, 0, 0, 0) 100%);
    }}
    .estates-track {{
      display: flex;
      gap: 1.75rem;
      padding: 1rem max(2rem, calc((100vw - 1180px) / 2)) 2.5rem max(2rem, calc((100vw - 1180px) / 2));
      overflow-x: auto;
      scroll-snap-type: x mandatory;
      scroll-behavior: smooth;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
      user-select: none;
      cursor: grab;
    }}
    .estates-track.is-dragging {{
      cursor: grabbing;
      scroll-snap-type: none;
      scroll-behavior: auto;
    }}
    .estates-track::-webkit-scrollbar {{ display: none; }}

    .estate-card {{
      flex: 0 0 420px;
      scroll-snap-align: start;
      background: var(--bg-card);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid var(--hairline);
      border-radius: var(--apple-radius);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      position: relative;
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.4s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.3s ease;
      cursor: pointer;
    }}
    .estate-card:hover {{
      transform: translateY(-8px) scale(1.015);
      border-color: var(--hairline-hover);
      box-shadow: 0 24px 60px rgba(0, 0, 0, 0.7), 0 0 30px rgba(229, 200, 144, 0.15);
    }}
    .estate-media-wrap {{
      position: relative;
      width: 100%;
      height: 270px;
      overflow: hidden;
      background: #141418;
    }}
    .estate-card-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .estate-card:hover .estate-card-img {{
      transform: scale(1.06);
    }}
    .estate-status-badge {{
      position: absolute;
      top: 1.15rem;
      left: 1.15rem;
      z-index: 2;
      padding: 0.4rem 0.9rem;
      border-radius: var(--pill-radius);
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
    }}
    .status-for-sale {{
      background: rgba(16, 185, 129, 0.22);
      color: #34d399;
      border: 1px solid rgba(52, 211, 153, 0.4);
    }}
    .status-pending {{
      background: rgba(245, 158, 11, 0.22);
      color: #fbbf24;
      border: 1px solid rgba(251, 191, 36, 0.4);
    }}
    .status-sold {{
      background: rgba(229, 200, 144, 0.22);
      color: #f7e7c4;
      border: 1px solid rgba(229, 200, 144, 0.5);
    }}
    .estate-price-pill {{
      position: absolute;
      top: 1.15rem;
      right: 1.15rem;
      z-index: 2;
      background: rgba(0, 0, 0, 0.78);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1px solid rgba(255, 255, 255, 0.15);
      color: #ffffff;
      font-size: 0.9rem;
      font-weight: 700;
      padding: 0.4rem 0.85rem;
      border-radius: var(--pill-radius);
    }}
    .estate-card-body {{
      padding: 1.65rem 1.75rem 1.85rem 1.75rem;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }}
    .estate-title {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--text-primary);
      margin-bottom: 0.35rem;
      line-height: 1.25;
    }}
    .estate-submarket {{
      font-size: 0.86rem;
      color: var(--text-secondary);
      margin-bottom: 1.15rem;
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}
    .estate-specs-grid {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.45rem;
      margin-bottom: 1.15rem;
    }}
    .spec-pill {{
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: #d1d1d6;
      font-size: 0.76rem;
      font-weight: 500;
      padding: 0.3rem 0.65rem;
      border-radius: var(--pill-radius);
    }}
    .estate-brief {{
      font-size: 0.88rem;
      color: var(--text-secondary);
      line-height: 1.45;
      margin-bottom: 1.4rem;
      flex-grow: 1;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .estate-action-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding-top: 1.1rem;
      border-top: 1px solid var(--hairline);
    }}
    .estate-explore-link {{
      font-size: 0.86rem;
      color: var(--gold-accent);
      font-weight: 600;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      cursor: pointer;
      transition: gap 0.2s ease;
    }}
    .estate-card:hover .estate-explore-link {{
      gap: 0.5rem;
    }}
    .estate-card-btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      color: #ffffff;
      font-size: 0.82rem;
      font-weight: 600;
      padding: 0.5rem 1.1rem;
      border-radius: var(--pill-radius);
      cursor: pointer;
      transition: all 0.25s ease;
    }}
    .estate-card-btn:hover {{
      background: var(--gold-gradient);
      color: #0b0c10;
      border-color: transparent;
      box-shadow: 0 4px 14px rgba(229, 200, 144, 0.35);
    }}

    /* Estate Modal Lightbox */
    .estate-modal-backdrop {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      z-index: 10050;
      background: rgba(0, 0, 0, 0.82);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      display: none;
      align-items: center;
      justify-content: center;
      padding: 1.5rem;
      opacity: 0;
      transition: opacity 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .estate-modal-backdrop.is-active {{
      display: flex;
      opacity: 1;
    }}
    .estate-modal-sheet {{
      width: 100%;
      max-width: 860px;
      max-height: 90vh;
      overflow-y: auto;
      background: #0e0e12;
      border: 1.5px solid rgba(229, 200, 144, 0.35);
      border-radius: 32px;
      box-shadow: 0 32px 80px rgba(0, 0, 0, 0.9), 0 0 40px rgba(229, 200, 144, 0.2);
      position: relative;
      scrollbar-width: thin;
      scrollbar-color: var(--gold-accent) rgba(255, 255, 255, 0.05);
      transform: translateY(28px) scale(0.96);
      transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .estate-modal-backdrop.is-active .estate-modal-sheet {{
      transform: translateY(0) scale(1);
    }}
    .estate-modal-close {{
      position: absolute;
      top: 1.5rem;
      right: 1.5rem;
      width: 40px;
      height: 40px;
      border-radius: 50%;
      background: rgba(20, 20, 26, 0.85);
      border: 1px solid var(--hairline);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      z-index: 20;
      transition: all 0.2s ease;
    }}
    .estate-modal-close:hover {{
      background: var(--gold-accent);
      color: #000000;
      transform: rotate(90deg);
    }}
    .modal-hero-img-wrap {{
      width: 100%;
      height: 360px;
      position: relative;
    }}
    .modal-hero-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .modal-hero-gradient {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0.1) 0%, rgba(14,14,18,0.95) 100%);
    }}
    .modal-body {{
      padding: 2rem 2.5rem 2.5rem 2.5rem;
    }}
    .modal-keystone-box {{
      background: rgba(229, 200, 144, 0.07);
      border: 1px solid rgba(229, 200, 144, 0.3);
      border-radius: 20px;
      padding: 1.35rem 1.75rem;
      margin: 1.5rem 0;
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1.25rem;
    }}
    .modal-keystone-col-label {{
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--gold-accent);
      margin-bottom: 0.25rem;
    }}
    .modal-keystone-col-val {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #ffffff;
    }}
    .modal-cta-bar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
      margin-top: 2rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--hairline);
    }}

  </style>
</head>
<body>

  <!-- Apple Frosted Glass Navigation with Slide-Down Flyout -->
  <header class="apple-nav">
    <div class="nav-inner">
      <a href="#" class="brand-mark">
        <span class="brand-dot"></span>
        {t.name}
      </a>

      <div class="nav-actions">
        <a class="nav-link" href="#portfolio" style="padding: 0.85rem 0.5rem; margin-bottom: -0.85rem;">Estates</a>
        <!-- Dropdown 1: Intelligence -->
        <div class="nav-item-dropdown">
          <a class="nav-link" href="#valuation">
            Intelligence
            <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </a>
          <!-- Slide-Down Flyout -->
          <div class="apple-flyout">
            <div class="flyout-container">
              <div>
                <div class="flyout-col-title">Analytical Engines</div>
                <div class="flyout-link-stack">
                  <a href="#valuation" class="flyout-big-link">Interactive CMA Valuation ›</a>
                  <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4; margin-top: 0.3rem;">
                    Real-time algorithmic pricing across Estero, Bonita Springs, and Naples submarkets.
                  </p>
                </div>
              </div>
              <div>
                <div class="flyout-col-title">Micro-Neighborhoods</div>
                <div class="flyout-link-stack">
                  <a href="#valuation" class="flyout-sub-link">Estero & West Bay Club <span>$510/sq.ft</span></a>
                  <a href="#valuation" class="flyout-sub-link">Bonita Springs & Bay Colony <span>$610/sq.ft</span></a>
                  <a href="#valuation" class="flyout-sub-link">Naples & Port Royal <span>$780/sq.ft</span></a>
                  <a href="#valuation" class="flyout-sub-link">Gulf Harbour Yacht & CC <span>$465/sq.ft</span></a>
                </div>
              </div>
              <div>
                <div class="flyout-col-title">Direct Actions</div>
                <div class="flyout-link-stack">
                  <a href="#consultation" class="flyout-sub-link">Request Private CMA Dossier <span>PDF</span></a>
                  <a href="#advisory" class="flyout-sub-link">Flood & Roof Risk Mitigation <span>Audit</span></a>
                  <a href="tel:{t.phone_number.replace('-', '')}" class="flyout-sub-link">Direct Principal Line <span>24/7</span></a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Dropdown 2: Advisory -->
        <div class="nav-item-dropdown">
          <a class="nav-link" href="#advisory">
            Advisory
            <svg width="10" height="6" viewBox="0 0 10 6" fill="none"><path d="M1 1L5 5L9 1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
          </a>
          <!-- Slide-Down Flyout -->
          <div class="apple-flyout">
            <div class="flyout-container">
              <div>
                <div class="flyout-col-title">The Standard</div>
                <div class="flyout-link-stack">
                  <a href="#advisory" class="flyout-big-link">Discreet Principal Representation ›</a>
                  <p style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4; margin-top: 0.3rem;">
                    Bespoke off-market acquisition and disposition for family offices and luxury homeowners.
                  </p>
                </div>
              </div>
              <div>
                <div class="flyout-col-title">Specialist Disciplines</div>
                <div class="flyout-link-stack">
                  <a href="#advisory" class="flyout-sub-link">Off-Market Pocket Listings <span>Private</span></a>
                  <a href="#advisory" class="flyout-sub-link">Bilingual English / Español <span>Native</span></a>
                  <a href="#advisory" class="flyout-sub-link">HOA Reserve & Flood Audits <span>Certified</span></a>
                </div>
              </div>
              <div>
                <div class="flyout-col-title">Client Surface</div>
                <div class="flyout-link-stack">
                  <a href="portal.html" class="flyout-sub-link" target="_blank">Executive Client Portal ↗ <span>Back Door</span></a>
                  <a href="#consultation" class="flyout-sub-link">Book In-Person Appraisal <span>Confidential</span></a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <a href="#consultation" class="pill-btn-small">Request Private Brief</a>
      </div>
    </div>
  </header>
  <div class="apple-page-scrim"></div>

  <!-- Cinematic Hero -->
  <section class="hero container">
    <div class="hero-eyebrow">Southwest Florida • Private Client Advisory</div>
    <h1 class="hero-title">Real estate.<br>Perfected with discretion.</h1>
    <p class="hero-subtitle">{t.tagline}. High-conviction representation across Estero, Bonita Springs, and Naples.</p>
    
    <div class="hero-cta-group">
      <a href="#consultation" class="pill-btn-primary">
        Schedule Private Consultation
      </a>
      <a href="#valuation" class="apple-link-cta">
        Explore live valuation model <span>›</span>
      </a>
    </div>

    <!-- Hero Image Showcase Stage -->
    <div class="hero-display-stage">
      <img src="assets/mansion_hero.jpg" alt="Luxury Estate" class="stage-image" onerror="this.src='https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1200&q=80'">
      <div class="stage-overlay">
        <div class="stage-advisor">
          <img src="assets/headshot.png" alt="{t.name}" class="stage-avatar" onerror="this.src='assets/Rosie.png'">
          <div>
            <div class="stage-name">{t.name}</div>
            <div class="stage-desc">{t.company_name} • Florida Licensed Real Estate Advisor</div>
          </div>
        </div>
        <div class="stage-badge">
          Direct Principal Access
        </div>
      </div>
    </div>
  </section>

  <!-- Apple Kinetic Estates Showcase Section -->
  <section class="estates-section" id="portfolio">
    <div class="container">
      <div class="estates-header-row">
        <div>
          <div class="estates-eyebrow">Curated Portfolio • Southwest Florida Luxury</div>
          <h2 class="estates-headline">Explore the estates.<br>Active, pending, and trophy sales.</h2>
        </div>
        <div class="carousel-nav-controls">
          <button class="carousel-nav-btn prev-btn" id="estatePrevBtn" aria-label="Previous estate">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M15 19l-7-7 7-7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
          <button class="carousel-nav-btn next-btn" id="estateNextBtn" aria-label="Next estate">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M9 5l7 7-7 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>
        </div>
      </div>

      <!-- Category Filter Pills -->
      <div class="estate-filter-bar">
        <button class="filter-pill active" data-filter="all">All Estates (5)</button>
        <button class="filter-pill" data-filter="for_sale">✨ For Sale (2)</button>
        <button class="filter-pill" data-filter="under_contract">⚡ Under Contract (1)</button>
        <button class="filter-pill" data-filter="sold">🏆 Record Sold (2)</button>
      </div>
    </div>

    <!-- Kinetic Horizontal Carousel Track with Edge Scrims -->
    <div class="estates-carousel-wrapper">
      <div class="carousel-scrim-left"></div>
      <div class="carousel-scrim-right"></div>
      <div class="estates-track" id="estatesTrack">
        {estate_cards_html}
      </div>
    </div>
  </section>

  <!-- Apple Bento Chapter: The Advisory Standard -->
  <section class="section-chapter container" id="advisory">
    <div class="chapter-eyebrow">The Standard</div>
    <h2 class="chapter-title">Discreet. Analytical. Distinctive.</h2>

    <div class="bento-grid">
      <div class="bento-card span-2">
        <div>
          <div class="bento-tag">Proprietary Flow</div>
          <h3 class="bento-headline">Off-Market Inventory & Private Pocket Offerings</h3>
          <p class="bento-text">Access confidential pre-market estates across Pelican Bay, Barefoot Beach, and Estero prior to public MLS syndication. Complete discretion from letter of intent to settlement.</p>
        </div>
      </div>

      <div class="bento-card">
        <div>
          <div class="bento-tag">Bilingual Mastery</div>
          <h3 class="bento-headline">English & Spanish Principal Representation</h3>
          <p class="bento-text">Seamless contractual guidance in English and Spanish for domestic and international family offices.</p>
        </div>
      </div>

      <div class="bento-card">
        <div>
          <div class="bento-tag">Risk Modeling</div>
          <h3 class="bento-headline">Flood Zone & HOA Assessment</h3>
          <p class="bento-text">Detailed mitigation metrics covering 500-year flood lines, elevation certs, and condominium structural reserve audits.</p>
        </div>
      </div>

      <div class="bento-card span-2">
        <div>
          <div class="bento-tag">Execution Precision</div>
          <h3 class="bento-headline">Targeted Comparative Market Analysis (CMA)</h3>
          <p class="bento-text">Precision valuation built on micro-neighborhood hyper-comps, architectural adjustments, and real-time absorption speed across Lee & Collier Counties.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Apple-Style Interactive Valuation Engine -->
  <section class="cma-section" id="valuation">
    <div class="container">
      <div class="cma-box">
        <div class="cma-display">
          <div class="cma-val-title">Indicative Market Valuation</div>
          <div class="cma-price-hero" id="cma-hero-price">$1,850,000</div>
          <div class="cma-price-sub">Est. Range: <span id="cma-range-low">$1,775,000</span> – <span id="cma-range-high">$1,925,000</span> • <span id="cma-ppsf">$525</span>/sq.ft</div>
        </div>

        <div class="cma-controls">
          <div>
            <div class="control-label">
              <span>Interior Living Area</span>
              <span class="slider-val"><span id="sqft-val">3,500</span> sq.ft</span>
            </div>
            <input type="range" class="apple-slider" id="sqft-slider" min="1500" max="8500" step="50" value="3500" oninput="updateValuation()">
          </div>

          <div>
            <div class="control-label">
              <span>Submarket Location</span>
            </div>
            <select class="apple-select" id="market-select" onchange="updateValuation()">
              <option value="estero">Estero / West Bay Club ($480 - $550/sq.ft)</option>
              <option value="bonita">Bonita Springs / Bay Colony ($550 - $680/sq.ft)</option>
              <option value="naples" selected>Naples / Port Royal ($650 - $1,100/sq.ft)</option>
              <option value="gulf">Gulf Harbor Yacht & CC ($420 - $510/sq.ft)</option>
            </select>
          </div>
        </div>

        <div style="text-align: center;">
          <a href="#consultation" class="pill-btn-primary" style="font-size: 0.9rem; padding: 0.75rem 1.6rem;">
            Request Official Appraised CMA Dossier
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Confidential Direct Intake Section -->
  <section class="intake-section container" id="consultation">
    <div class="chapter-eyebrow">Direct Principal Contact</div>
    <h2 class="chapter-title" style="margin-bottom: 2.5rem;">Begin the conversation.</h2>

    <div class="intake-card">
      <form onsubmit="submitInquiry(event)">
        <div class="form-group">
          <label class="form-label">Full Name</label>
          <input type="text" class="apple-input" id="inquiry-name" placeholder="Leo Peralta" required>
        </div>
        <div class="form-group">
          <label class="form-label">Direct Phone or Email</label>
          <input type="text" class="apple-input" id="inquiry-contact" placeholder="client@private.domain" required>
        </div>
        <div class="form-group">
          <label class="form-label">Property Interest or Address</label>
          <input type="text" class="apple-input" id="inquiry-address" placeholder="e.g. Pelican Landing or 1646 Heritage" required>
        </div>
        <button type="submit" class="pill-btn-primary" id="inquiry-submit-btn" style="width: 100%; justify-content: center; cursor: pointer; border: none;">
          Transmit Confidential Brief
        </button>
      </form>
      <div id="inquiry-feedback" style="display: none; margin-top: 1.5rem; text-align: center; color: var(--gold-accent); font-size: 0.9rem;">
        ✓ Brief securely transmitted to {t.name}'s private intake desk.
      </div>
    </div>
  </section>

  <!-- Apple Minimalist Footer -->
  <footer class="apple-footer container">
    <div class="footer-disclaimer">
      1. Indicative valuations are heuristic market models for preliminary consultation only and do not constitute a certified real estate appraisal or lender-guaranteed value.<br>
      2. Off-market and pre-MLS access is subject to principal seller agreements and cooperative broker compliance. Not intended to solicit properties currently under exclusive listing agreement.<br>
      3. Equal Housing Opportunity. All information deemed reliable but not guaranteed.
    </div>
    <div class="footer-line">
      <div>&copy; 2026 {t.company_name} • {t.name}</div>
      <div>Designed with Apple Aesthetic Principles • Powered by Apex Luxury AI</div>
    </div>
  </footer>

  <script>
    const submarketRates = {{
      'estero': 510,
      'bonita': 610,
      'naples': 780,
      'gulf': 465
    }};

    function updateValuation() {{
      const sqft = parseInt(document.getElementById('sqft-slider').value);
      const market = document.getElementById('market-select').value;
      const rate = submarketRates[market] || 600;

      document.getElementById('sqft-val').innerText = sqft.toLocaleString();
      
      const total = sqft * rate;
      const low = Math.round(total * 0.95);
      const high = Math.round(total * 1.05);

      document.getElementById('cma-hero-price').innerText = '$' + total.toLocaleString();
      document.getElementById('cma-range-low').innerText = '$' + low.toLocaleString();
      document.getElementById('cma-range-high').innerText = '$' + high.toLocaleString();
      document.getElementById('cma-ppsf').innerText = '$' + rate;
    }}

    function submitInquiry(e) {{
      e.preventDefault();
      const btn = document.getElementById('inquiry-submit-btn');
      btn.disabled = true;
      btn.innerText = 'Encrypting & Transmitting...';

      const name = document.getElementById('inquiry-name').value.trim();
      const contact = document.getElementById('inquiry-contact').value.trim();
      const address = document.getElementById('inquiry-address').value.trim();
      const val = document.getElementById('cma-hero-price').innerText.trim();

      const newLead = {{
        id: 'lead_' + Date.now(),
        full_name: name,
        contact: contact,
        property_interest: address,
        valuation_target: val,
        tenant: '{t.subdomain_slug}',
        timestamp: new Date().toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}}),
        date: new Date().toISOString(),
        heat: 'HOT'
      }};

      // Persist to localStorage for immediate reactive display in Sovereign OS Portal
      try {{
        const storageKey = 'apex_leads_{t.subdomain_slug}';
        const existing = JSON.parse(localStorage.getItem(storageKey) || '[]');
        existing.unshift(newLead);
        localStorage.setItem(storageKey, JSON.stringify(existing));
      }} catch (err) {{
        console.warn('localStorage sync error:', err);
      }}

      // Transmit to Loopback server (:8787/brief)
      const payload = {{
        kind: 'apex_realtor_onboarding_brief',
        tenant: '{t.subdomain_slug}',
        lead: newLead
      }};

      fetch('http://127.0.0.1:8787/brief', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(payload)
      }}).catch(() => {{}}).finally(() => {{
        const feedback = document.getElementById('inquiry-feedback');
        feedback.innerHTML = `
          <div style="background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.3); padding: 1.1rem; border-radius: 14px; margin-top: 1.25rem; text-align: left;">
            <div style="color: #34d399; font-weight: 600; font-size: 0.95rem; display: flex; align-items: center; gap: 0.4rem;">
              <span>✓</span> Confidential Brief Transmitted
            </div>
            <p style="color: var(--text-secondary); font-size: 0.82rem; margin: 0.4rem 0 0.85rem 0; line-height: 1.45;">
              Your valuation target of <strong style="color:#fff;">${{val}}</strong> for <strong style="color:#fff;">${{address}}</strong> has been dispatched and staged directly into {t.name}'s Sovereign OS portal.
            </p>
            <a href="portal.html" target="_blank" style="display: inline-flex; align-items: center; gap: 0.4rem; font-size: 0.82rem; color: #ffd700; text-decoration: none; font-weight: 600; background: rgba(229,200,144,0.12); padding: 0.45rem 0.95rem; border-radius: 20px; border: 1px solid rgba(229,200,144,0.3); transition: all 0.2s ease;">
              View Staged Lead in Portal ↗
            </a>
          </div>
        `;
        feedback.style.display = 'block';
        btn.innerText = '✓ Brief Dispatched';
      }});
    }}

    // Apple Navigation Click & Hover Grace Buffer
    const dropdowns = document.querySelectorAll('.nav-item-dropdown');
    let closeTimer = null;

    dropdowns.forEach(dd => {{
      const link = dd.querySelector('.nav-link');
      const flyout = dd.querySelector('.apple-flyout');

      function openFlyout() {{
        if (closeTimer) {{
          clearTimeout(closeTimer);
          closeTimer = null;
        }}
        dropdowns.forEach(other => {{
          const f = other.querySelector('.apple-flyout');
          if (f && f !== flyout) f.classList.remove('is-open');
        }});
        if (flyout) flyout.classList.add('is-open');
        const scrim = document.querySelector('.apple-page-scrim');
        if (scrim) scrim.style.opacity = '1';
      }}

      function closeFlyoutWithDelay() {{
        if (closeTimer) clearTimeout(closeTimer);
        closeTimer = setTimeout(() => {{
          const anyDropdownHovered = Array.from(dropdowns).some(d => d.matches(':hover'));
          const anyFlyoutHovered = Array.from(document.querySelectorAll('.apple-flyout')).some(f => f.matches(':hover'));
          if (anyDropdownHovered || anyFlyoutHovered) return;

          document.querySelectorAll('.apple-flyout').forEach(f => f.classList.remove('is-open'));
          const scrim = document.querySelector('.apple-page-scrim');
          if (scrim) scrim.style.opacity = '0';
        }}, 700);
      }}

      dd.addEventListener('mouseenter', openFlyout);
      dd.addEventListener('mouseleave', closeFlyoutWithDelay);

      if (flyout) {{
        flyout.addEventListener('mouseenter', () => {{
          if (closeTimer) {{
            clearTimeout(closeTimer);
            closeTimer = null;
          }}
        }});
        flyout.addEventListener('mousemove', () => {{
          if (closeTimer) {{
            clearTimeout(closeTimer);
            closeTimer = null;
          }}
        }});
        flyout.addEventListener('mouseleave', closeFlyoutWithDelay);
      }}

      if (link) {{
        link.addEventListener('click', (e) => {{
          e.preventDefault();
          const isOpen = flyout && flyout.classList.contains('is-open');
          if (isOpen) {{
            if (flyout) flyout.classList.remove('is-open');
            const scrim = document.querySelector('.apple-page-scrim');
            if (scrim) scrim.style.opacity = '0';
          }} else {{
            openFlyout();
          }}
        }});
      }}
    }});

    // Smooth scroll and auto-close flyout on sub-link click
    document.querySelectorAll('.apple-flyout a').forEach(a => {{
      a.addEventListener('click', (e) => {{
        const href = a.getAttribute('href');
        if (href && href.startsWith('#')) {{
          e.preventDefault();
          document.querySelectorAll('.apple-flyout').forEach(f => f.classList.remove('is-open'));
          const scrim = document.querySelector('.apple-page-scrim');
          if (scrim) scrim.style.opacity = '0';
          const target = document.querySelector(href);
          if (target) target.scrollIntoView({{ behavior: 'smooth' }});
        }}
      }});
    }});

    // Close when clicking anywhere outside header
    document.addEventListener('click', (e) => {{
      if (!e.target.closest('.apple-nav')) {{
        document.querySelectorAll('.apple-flyout').forEach(f => f.classList.remove('is-open'));
        const scrim = document.querySelector('.apple-page-scrim');
        if (scrim) scrim.style.opacity = '0';
      }}
    }});

    updateValuation();

    // =========================================================
    // Apple-Style Kinetic Horizontal Carousel & Estate Modal
    // =========================================================
    const estatesData = {listings_json_str};
    const estatesTrack = document.getElementById('estatesTrack');
    const estatePrevBtn = document.getElementById('estatePrevBtn');
    const estateNextBtn = document.getElementById('estateNextBtn');
    const estateFilterBtns = document.querySelectorAll('.estate-filter-bar .filter-pill');

    // Arrow Navigation with smooth momentum
    if (estateNextBtn && estatesTrack) {{
      estateNextBtn.addEventListener('click', () => {{
        estatesTrack.scrollBy({{ left: 450, behavior: 'smooth' }});
      }});
    }}
    if (estatePrevBtn && estatesTrack) {{
      estatePrevBtn.addEventListener('click', () => {{
        estatesTrack.scrollBy({{ left: -450, behavior: 'smooth' }});
      }});
    }}

    // Drag-to-Scroll Kinetic Motion
    if (estatesTrack) {{
      let isDown = false;
      let startX;
      let scrollLeft;

      estatesTrack.addEventListener('mousedown', (e) => {{
        isDown = true;
        estatesTrack.classList.add('is-dragging');
        startX = e.pageX - estatesTrack.offsetLeft;
        scrollLeft = estatesTrack.scrollLeft;
      }});

      estatesTrack.addEventListener('mouseleave', () => {{
        if (!isDown) return;
        isDown = false;
        estatesTrack.classList.remove('is-dragging');
      }});

      estatesTrack.addEventListener('mouseup', () => {{
        if (!isDown) return;
        isDown = false;
        estatesTrack.classList.remove('is-dragging');
      }});

      estatesTrack.addEventListener('mousemove', (e) => {{
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - estatesTrack.offsetLeft;
        const walk = (x - startX) * 1.35;
        estatesTrack.scrollLeft = scrollLeft - walk;
      }});
    }}

    // Category Filter with Smooth Animation
    estateFilterBtns.forEach(btn => {{
      btn.addEventListener('click', () => {{
        estateFilterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const filter = btn.getAttribute('data-filter');
        const cards = document.querySelectorAll('.estate-card');
        
        cards.forEach(card => {{
          const cat = card.getAttribute('data-category');
          if (filter === 'all' || cat === filter) {{
            card.style.display = 'flex';
            setTimeout(() => {{
              card.style.opacity = '1';
              card.style.transform = 'scale(1)';
            }}, 20);
          }} else {{
            card.style.opacity = '0';
            card.style.transform = 'scale(0.94)';
            setTimeout(() => {{
              card.style.display = 'none';
            }}, 250);
          }}
        }});
      }});
    }});

    // Estate Modal Controller
    window.openEstateModal = function(estateId) {{
      const estate = estatesData.find(item => item.id === estateId);
      if (!estate) return;

      const modal = document.getElementById('estateModal');
      const heroImg = document.getElementById('modalHeroImg');
      const title = document.getElementById('modalTitle');
      const neighborhood = document.getElementById('modalNeighborhood');
      const price = document.getElementById('modalPrice');
      const statusBadge = document.getElementById('modalStatusBadge');
      const specs = document.getElementById('modalSpecs');
      const narrative = document.getElementById('modalNarrative');
      const ppsf = document.getElementById('modalPpsf');
      const benchmark = document.getElementById('modalBenchmark');
      const velocity = document.getElementById('modalVelocity');
      const showingBtn = document.getElementById('modalRequestShowingBtn');

      if (heroImg) heroImg.src = estate.primary_image;
      if (title) title.textContent = estate.title;
      if (neighborhood) neighborhood.textContent = estate.neighborhood + ' • ' + estate.submarket;
      if (price) price.textContent = estate.price;
      if (statusBadge) {{
        statusBadge.textContent = estate.status_label;
        statusBadge.className = 'estate-status-badge ' + (estate.status_pill_class || 'status-for-sale');
      }}
      if (specs) {{
        specs.innerHTML = `
          <span class="spec-pill" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">${{estate.beds}} Bedrooms</span>
          <span class="spec-pill" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">${{estate.baths}} Bathrooms</span>
          <span class="spec-pill" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">${{estate.sqft.toLocaleString()}} Sq.Ft.</span>
          <span class="spec-pill" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">${{estate.garage}}</span>
          <span class="spec-pill" style="font-size: 0.85rem; padding: 0.4rem 0.85rem;">${{estate.waterfront}}</span>
        `;
      }}
      if (narrative) narrative.textContent = estate.quill_narrative;
      if (ppsf) ppsf.textContent = estate.keystone_valuation ? estate.keystone_valuation.price_per_sqft : '—';
      if (benchmark) benchmark.textContent = estate.keystone_valuation ? estate.keystone_valuation.benchmark_spread : '—';
      if (velocity) velocity.textContent = estate.keystone_valuation ? estate.keystone_valuation.market_velocity : '—';

      if (showingBtn) {{
        showingBtn.onclick = () => {{
          closeEstateModal();
          const consultSection = document.getElementById('consultation');
          if (consultSection) {{
            consultSection.scrollIntoView({{ behavior: 'smooth' }});
            const addrInput = document.getElementById('intakePropertyAddress');
            if (addrInput) {{
              addrInput.value = estate.title + ' (' + estate.neighborhood + ')';
              addrInput.focus();
            }}
          }}
        }};
      }}

      if (modal) {{
        modal.classList.add('is-active');
        document.body.style.overflow = 'hidden';
      }}
    }};

    window.closeEstateModal = function() {{
      const modal = document.getElementById('estateModal');
      if (modal) {{
        modal.classList.remove('is-active');
        document.body.style.overflow = '';
      }}
    }};

    const closeBtn = document.getElementById('closeEstateModalBtn');
    if (closeBtn) closeBtn.addEventListener('click', closeEstateModal);

    const modalBackdrop = document.getElementById('estateModal');
    if (modalBackdrop) {{
      modalBackdrop.addEventListener('click', (e) => {{
        if (e.target === modalBackdrop) closeEstateModal();
      }});
    }}

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeEstateModal();
    }});
  </script>

  <!-- Apple Frosted Glass Estate Dossier Modal -->
  <div class="estate-modal-backdrop" id="estateModal">
    <div class="estate-modal-sheet" id="estateModalSheet">
      <button class="estate-modal-close" id="closeEstateModalBtn" aria-label="Close modal">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
      </button>
      <div class="modal-hero-img-wrap">
        <img src="" alt="" class="modal-hero-img" id="modalHeroImg">
        <div class="modal-hero-gradient"></div>
        <div style="position: absolute; bottom: 1.5rem; left: 2.5rem; right: 2.5rem; display: flex; justify-content: space-between; align-items: flex-end;">
          <div>
            <div class="estate-status-badge" id="modalStatusBadge" style="position: static; margin-bottom: 0.6rem; display: inline-block;"></div>
            <h2 id="modalTitle" style="font-size: 2rem; font-weight: 700; color: #ffffff; line-height: 1.15;"></h2>
            <div id="modalNeighborhood" style="color: var(--gold-accent); font-size: 0.95rem; margin-top: 0.3rem;"></div>
          </div>
          <div id="modalPrice" style="font-size: 2rem; font-weight: 800; color: #ffffff; text-shadow: 0 4px 18px rgba(0,0,0,0.8);"></div>
        </div>
      </div>
      <div class="modal-body">
        <div class="estate-specs-grid" id="modalSpecs" style="margin-bottom: 1.5rem; gap: 0.65rem;"></div>
        
        <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--gold-accent); margin-bottom: 0.5rem;">Architectural Narrative</h4>
        <p id="modalNarrative" style="color: #d1d1d6; font-size: 1rem; line-height: 1.6; margin-bottom: 1.5rem;"></p>

        <!-- Keystone Analytical Intel Box -->
        <h4 style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--gold-accent); margin-bottom: 0.5rem;">Keystone Market Intelligence</h4>
        <div class="modal-keystone-box">
          <div>
            <div class="modal-keystone-col-label">Price Per Sq.Ft</div>
            <div class="modal-keystone-col-val" id="modalPpsf">—</div>
          </div>
          <div>
            <div class="modal-keystone-col-label">Benchmark Valuation</div>
            <div class="modal-keystone-col-val" id="modalBenchmark">—</div>
          </div>
          <div>
            <div class="modal-keystone-col-label">Submarket Velocity</div>
            <div class="modal-keystone-col-val" id="modalVelocity" style="font-size: 0.95rem;">—</div>
          </div>
        </div>

        <!-- Showing Action Bar -->
        <div class="modal-cta-bar">
          <div>
            <div style="font-weight: 700; font-size: 1.05rem; color: #ffffff;">Experience this estate in person</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary);">Direct principal scheduling with {t.name}</div>
          </div>
          <button class="pill-btn-primary" id="modalRequestShowingBtn" style="padding: 0.75rem 1.85rem; font-size: 0.92rem;">
            Request Private Walkthrough
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Floating Glass AI Concierge Widget (Stripe x Apple) -->
  <style>
    .concierge-launcher {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      z-index: 9999;
      display: flex;
      align-items: center;
      gap: 0.85rem;
      background: rgba(18, 18, 24, 0.94);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1.5px solid rgba(229, 200, 144, 0.65);
      padding: 0.65rem 1.35rem 0.65rem 0.75rem;
      border-radius: var(--pill-radius);
      cursor: pointer;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8), 0 0 24px rgba(229, 200, 144, 0.35);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s ease, border-color 0.3s ease;
      animation: conciergeEntrance 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.5s both, conciergePulse 4s ease-in-out 1.5s infinite;
    }}
    .concierge-launcher:hover {{
      transform: translateY(-4px) scale(1.03);
      border-color: #ffd700;
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.9), 0 0 32px rgba(229, 200, 144, 0.6);
    }}
    @keyframes conciergeEntrance {{
      from {{
        opacity: 0;
        transform: translateY(24px) scale(0.92);
      }}
      to {{
        opacity: 1;
        transform: translateY(0) scale(1);
      }}
    }}
    @keyframes conciergePulse {{
      0%, 100% {{
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8), 0 0 20px rgba(229, 200, 144, 0.35);
      }}
      50% {{
        box-shadow: 0 20px 44px rgba(0, 0, 0, 0.85), 0 0 32px rgba(229, 200, 144, 0.6);
      }}
    }}
    .concierge-avatar-wrap {{
      position: relative;
      width: 42px;
      height: 42px;
      flex-shrink: 0;
    }}
    .concierge-launcher-img {{
      width: 42px;
      height: 42px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid var(--gold-accent);
    }}
    .concierge-online-dot {{
      position: absolute;
      bottom: 0;
      right: 0;
      width: 11px;
      height: 11px;
      background: #34d399;
      border-radius: 50%;
      border: 2px solid #111;
      animation: dotPulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}
    @keyframes dotPulse {{
      0%, 100% {{
        box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7);
      }}
      50% {{
        box-shadow: 0 0 0 6px rgba(52, 211, 153, 0);
      }}
    }}
    .concierge-launcher-title {{
      font-size: 0.88rem;
      font-weight: 600;
      color: #ffffff;
      line-height: 1.2;
    }}
    .concierge-launcher-sub {{
      font-size: 0.72rem;
      color: var(--gold-accent);
      letter-spacing: 0.02em;
      font-weight: 500;
      margin-top: 2px;
    }}

    /* Concierge Chat Window */
    .concierge-window {{
      position: fixed;
      bottom: 5.5rem;
      right: 2rem;
      width: 380px;
      max-width: calc(100vw - 2.5rem);
      height: 540px;
      max-height: calc(100vh - 7rem);
      background: rgba(12, 12, 16, 0.96);
      backdrop-filter: blur(32px);
      -webkit-backdrop-filter: blur(32px);
      border: 1px solid rgba(229, 200, 144, 0.3);
      border-radius: 20px;
      box-shadow: 0 32px 80px rgba(0, 0, 0, 0.95), 0 0 30px rgba(229, 200, 144, 0.15);
      z-index: 10000;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      transform: translateY(20px) scale(0.95);
      pointer-events: none;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .concierge-window.is-open {{
      opacity: 1;
      transform: translateY(0) scale(1);
      pointer-events: auto;
    }}
    .concierge-header {{
      padding: 1rem 1.25rem;
      border-bottom: 1px solid var(--hairline);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255, 255, 255, 0.02);
    }}
    .concierge-header-agent {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    .concierge-header-img {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      object-fit: cover;
      border: 1.5px solid var(--gold-accent);
    }}
    .concierge-header-name {{
      font-size: 0.9rem;
      font-weight: 600;
      color: #fff;
    }}
    .concierge-header-sub {{
      font-size: 0.72rem;
      color: var(--text-secondary);
    }}
    .concierge-close-btn {{
      background: transparent;
      border: none;
      color: var(--text-secondary);
      font-size: 1.1rem;
      cursor: pointer;
      padding: 0.25rem 0.5rem;
      border-radius: 6px;
      transition: color 0.2s ease;
    }}
    .concierge-close-btn:hover {{
      color: #fff;
    }}
    .concierge-body {{
      flex: 1;
      padding: 1.25rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
    }}
    .concierge-bubble {{
      max-width: 86%;
      padding: 0.85rem 1.05rem;
      border-radius: 16px;
      font-size: 0.85rem;
      line-height: 1.45;
    }}
    .concierge-agent-bubble {{
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid var(--hairline);
      color: var(--text-primary);
      align-self: flex-start;
    }}
    .concierge-user-bubble {{
      background: var(--gold-accent);
      color: #000;
      font-weight: 500;
      align-self: flex-end;
    }}
    .concierge-chips {{
      display: flex;
      gap: 0.4rem;
      padding: 0 1.25rem 0.65rem 1.25rem;
      overflow-x: auto;
      scrollbar-width: none;
    }}
    .concierge-chips::-webkit-scrollbar {{
      display: none;
    }}
    .concierge-chip {{
      white-space: nowrap;
      font-size: 0.72rem;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--hairline);
      color: var(--text-secondary);
      padding: 0.35rem 0.7rem;
      border-radius: var(--pill-radius);
      cursor: pointer;
      transition: all 0.2s ease;
    }}
    .concierge-chip:hover {{
      color: #fff;
      border-color: var(--gold-accent);
      background: rgba(229, 200, 144, 0.1);
    }}
    .concierge-footer {{
      padding: 0.85rem 1.25rem;
      border-top: 1px solid var(--hairline);
      display: flex;
      gap: 0.5rem;
      background: rgba(255, 255, 255, 0.01);
    }}
    .concierge-input {{
      flex: 1;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--hairline);
      border-radius: 12px;
      padding: 0.65rem 0.9rem;
      color: #fff;
      font-size: 0.85rem;
      outline: none;
      font-family: inherit;
    }}
    .concierge-input:focus {{
      border-color: var(--gold-accent);
    }}
    .concierge-send-btn {{
      background: var(--text-primary);
      color: #000;
      border: none;
      width: 36px;
      height: 36px;
      border-radius: 10px;
      font-weight: 700;
      font-size: 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.15s ease;
    }}
    .concierge-send-btn:hover {{
      transform: scale(1.05);
    }}
  </style>

  <!-- Floating Concierge Elements -->
  <div class="concierge-launcher" id="concierge-launcher" onclick="toggleConcierge()">
    <div class="concierge-avatar-wrap">
      <img src="assets/headshot.png" alt="{t.name}" class="concierge-launcher-img" onerror="this.src='../../assets/clients/sofia_headshot.png'">
      <span class="concierge-online-dot"></span>
    </div>
    <div class="concierge-launcher-info">
      <div class="concierge-launcher-title">✨ {t.name}'s Digital Desk</div>
      <div class="concierge-launcher-sub">Online • 24/7 Sovereign Concierge</div>
    </div>
  </div>

  <div class="concierge-window" id="concierge-window">
    <div class="concierge-header">
      <div class="concierge-header-agent">
        <img src="assets/headshot.png" alt="{t.name}" class="concierge-header-img" onerror="this.src='../../assets/clients/sofia_headshot.png'">
        <div>
          <div class="concierge-header-name">{t.name} Digital Desk</div>
          <div class="concierge-header-sub">Keystone MLS & Appraisal Engine</div>
        </div>
      </div>
      <button class="concierge-close-btn" onclick="toggleConcierge()">✕</button>
    </div>

    <div class="concierge-body" id="concierge-body">
      <div class="concierge-bubble concierge-agent-bubble">
        Hello! I am {t.name}'s Sovereign AI Concierge. I have live access to Southwest Florida MLS comps, Lee County tax records, and valuation models across Estero and Naples.<br><br>
        How may I assist your acquisition or listing strategy today?
      </div>
    </div>

    <div class="concierge-chips">
      <button class="concierge-chip" onclick="askConcierge('📐 Estero $/sqft Rates')">📐 Estero $/sqft Rates</button>
      <button class="concierge-chip" onclick="askConcierge('🏡 Bella Terra Valuation')">🏡 Bella Terra Valuation</button>
      <button class="concierge-chip" onclick="askConcierge('🌊 Flood Zone AE vs X')">🌊 Flood Zone AE vs X</button>
      <button class="concierge-chip" onclick="askConcierge('📅 Book Private Showing')">📅 Book Private Showing</button>
    </div>

    <form class="concierge-footer" onsubmit="sendConciergeMsg(event)">
      <input type="text" class="concierge-input" id="concierge-input" placeholder="Ask about comps, valuations, or private tours..." autocomplete="off">
      <button type="submit" class="concierge-send-btn">↑</button>
    </form>
  </div>

  <script>
    function toggleConcierge() {{
      const win = document.getElementById('concierge-window');
      win.classList.toggle('is-open');
      if (win.classList.contains('is-open')) {{
        document.getElementById('concierge-input').focus();
      }}
    }}

    function askConcierge(query) {{
      const body = document.getElementById('concierge-body');
      
      const userBubble = document.createElement('div');
      userBubble.className = 'concierge-bubble concierge-user-bubble';
      userBubble.innerText = query;
      body.appendChild(userBubble);
      body.scrollTop = body.scrollHeight;

      setTimeout(() => {{
        const agentBubble = document.createElement('div');
        agentBubble.className = 'concierge-bubble concierge-agent-bubble';

        const q = query.toLowerCase();
        if (q.includes('rate') || q.includes('sqft') || q.includes('estero')) {{
          agentBubble.innerHTML = '<strong>Keystone Micro-Comp Benchmark:</strong><br>• Estero Core Corridor: <strong>$310 – $340 / sq.ft</strong><br>• West Bay / Gated Luxury: <strong>$480 – $550 / sq.ft</strong><br>• Naples High-Luxury: <strong>$780 – $1,200+ / sq.ft</strong><br><br>Properties with post-Ian metal/tile roofs currently command an immediate 6–8% insurance underwriting discount.';
        }} else if (q.includes('bella terra') || q.includes('valuation')) {{
          agentBubble.innerHTML = '<strong>Keystone Property Quadrant:</strong><br>• Target: <strong>21450 Bella Terra Blvd</strong><br>• Keystone Appraisal: <strong>$848,800</strong><br>• Zillow Zestimate: $562,400<br>• Alpha Spread: <strong>+$286,400</strong><br><br>Zillow fails to factor in the permitted 2023 tile roof and custom heated pool. {t.name} can present this exact appraisal to your buyer.';
        }} else if (q.includes('flood') || q.includes('ae') || q.includes('zone')) {{
          agentBubble.innerHTML = '<strong>FEMA Flood Zone Advisory:</strong><br>• <strong>Zone X:</strong> Minimal flood hazard; 0 mandatory flood insurance required.<br>• <strong>Zone AE:</strong> Base flood elevation required. Can add $3,200–$5,500/yr in insurance if unmitigated.<br><br>{t.name} verifies all elevation certificates through Lee County GIS prior to contract execution.';
        }} else if (q.includes('showing') || q.includes('tour') || q.includes('book')) {{
          agentBubble.innerHTML = 'I would be delighted to arrange an exclusive private showing with {t.name}.<br><br>Please enter your cell number or email below, or submit our Direct Principal Brief on this page, and {t.name} will reach out to confirm your itinerary.';
        }} else {{
          agentBubble.innerHTML = 'Thank you for your inquiry regarding Southwest Florida luxury realty. I have forwarded this brief to {t.name}\\'s private workforce desk. Feel free to submit an official dossier request or call <strong>{t.phone_number}</strong> directly.';
        }}

        body.appendChild(agentBubble);
        body.scrollTop = body.scrollHeight;
      }}, 400);
    }}

    function sendConciergeMsg(e) {{
      e.preventDefault();
      const input = document.getElementById('concierge-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      askConcierge(text);
    }}
  </script>
</body>
</html>"""

    def build_portal(self, tenant: Tenant) -> str:
        site_folder = os.path.join(self.output_dir, tenant.subdomain_slug)
        os.makedirs(site_folder, exist_ok=True)
        portal_file = os.path.join(site_folder, "portal.html")
        html = self._generate_portal_html(tenant)
        with open(portal_file, "w", encoding="utf-8") as f:
            f.write(html)
        return portal_file

    def _generate_portal_html(self, t: Tenant) -> str:
        coaching_label = getattr(t, 'coaching_source', 'Office Coaching Playbook')
        market_label = getattr(t, 'market', 'Southwest Florida')
        playbook = self.load_playbook()
        buttons_html = []
        for i, (k, s) in enumerate(playbook.items()):
            active_cls = " active" if i == 0 else ""
            label = s.get("menu_title", s.get("title", k))
            buttons_html.append(f'          <button class="script-item{active_cls}" onclick="loadScript(\'{k}\', this)">{label}</button>')
        playbook_menu_markup = "\n".join(buttons_html)
        first_script_key = next(iter(playbook.keys()), "fsbo")
        playbook_json_str = json.dumps(playbook)
        intake_queue = self.load_intake_queue(t.subdomain_slug)
        intake_queue_json = json.dumps(intake_queue)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{t.name} • Sovereign Realtor OS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-canvas: #000000;
      --bg-surface: #0a0a0d;
      --bg-card: rgba(18, 18, 24, 0.75);
      --bg-card-elevated: rgba(26, 26, 33, 0.88);
      --text-primary: #f5f5f7;
      --text-secondary: #86868b;
      --gold-accent: #e5c890;
      --gold-dim: rgba(229,200,144,0.15);
      --hairline: rgba(255,255,255,0.08);
      --hairline-gold: rgba(229,200,144,0.3);
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #f87171;
      --blue: #60a5fa;
      --r: 20px;
      --pill: 980px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", sans-serif;
      background: #000;
      color: var(--text-primary);
      -webkit-font-smoothing: antialiased;
      overflow-x: hidden;
      background-image:
        radial-gradient(ellipse 90% 55% at 50% -15%, rgba(229,200,144,0.14) 0%, transparent 65%),
        radial-gradient(ellipse 50% 40% at 92% 45%, rgba(96,165,250,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 55% 50% at 8% 85%, rgba(229,200,144,0.04) 0%, transparent 60%);
      background-attachment: fixed;
    }}

    /* ── NAV ── */
    .portal-nav {{
      position: sticky; top: 0; z-index: 200;
      background: rgba(0,0,0,0.82);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border-bottom: 1px solid var(--hairline);
    }}
    .nav-inner {{
      max-width: 1400px; margin: 0 auto; padding: 0 2rem;
      display: flex; justify-content: space-between; align-items: center;
      height: 3.2rem;
    }}
    .brand {{ display: flex; align-items: center; gap: 0.65rem; }}
    .brand-dot {{
      width: 8px; height: 8px; border-radius: 50%;
      background: var(--gold-accent);
      box-shadow: 0 0 10px rgba(229,200,144,0.7);
    }}
    .brand-name {{ font-size: 0.95rem; font-weight: 600; }}
    .badge {{
      background: rgba(255,255,255,0.06); border: 1px solid var(--hairline);
      color: var(--text-secondary); font-size: 0.7rem;
      padding: 0.18rem 0.55rem; border-radius: var(--pill);
      font-family: 'JetBrains Mono', monospace;
    }}
    .nav-tabs {{
      display: flex; gap: 0.2rem; background: rgba(255,255,255,0.04);
      border: 1px solid var(--hairline); border-radius: var(--pill);
      padding: 0.22rem;
    }}
    .nav-tab {{
      font-size: 0.78rem; font-weight: 500; padding: 0.3rem 0.85rem;
      border-radius: var(--pill); cursor: pointer; border: none;
      background: transparent; color: var(--text-secondary);
      transition: all 0.2s ease;
    }}
    .nav-tab.active {{
      background: rgba(255,255,255,0.12); color: var(--text-primary);
    }}
    .nav-right {{ display: flex; align-items: center; gap: 1rem; }}
    .live-dot {{
      display: flex; align-items: center; gap: 0.4rem;
      font-size: 0.75rem; color: var(--success); font-weight: 500;
    }}
    .pulse-dot {{
      width: 6px; height: 6px; border-radius: 50%;
      background: var(--success); box-shadow: 0 0 8px var(--success);
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.4; }} }}
    .btn-sm {{
      font-size: 0.78rem; font-weight: 500; padding: 0.35rem 0.85rem;
      border-radius: var(--pill); border: 1px solid var(--hairline);
      background: rgba(255,255,255,0.06); color: var(--text-primary);
      cursor: pointer; transition: all 0.2s ease; text-decoration: none;
      display: inline-flex; align-items: center; gap: 0.3rem;
    }}
    .btn-sm:hover {{ background: var(--text-primary); color: #000; }}

    /* ── LAYOUT SHELL ── */
    .os-shell {{
      max-width: 1400px; margin: 0 auto;
      padding: 0 2rem 4rem 2rem;
    }}

    /* ── PANEL VISIBILITY ── */
    .os-panel {{ display: none; }}
    .os-panel.active {{ display: block; }}

    /* ── CARDS ── */
    .card {{
      background: var(--bg-card);
      border: 1px solid var(--hairline);
      border-radius: var(--r);
      padding: 1.5rem 1.75rem;
      transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .card:hover {{ border-color: var(--hairline-gold); box-shadow: 0 12px 28px rgba(0,0,0,0.5); }}
    .card-title {{
      font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--gold-accent); font-weight: 600; margin-bottom: 0.5rem;
    }}

    /* ── KPI BAR ── */
    .kpi-bar {{
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 1rem; margin: 1.75rem 0;
    }}
    .kpi {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: 14px; padding: 1.1rem 1.25rem;
      transition: all 0.2s ease; cursor: default;
    }}
    .kpi:hover {{ border-color: var(--hairline-gold); transform: translateY(-2px); }}
    .kpi-num {{
      font-size: 1.7rem; font-weight: 600; letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums;
    }}
    .kpi-num.gold {{ background: linear-gradient(135deg,#f7e7c4,#e5c890,#b89547); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .kpi-num.green {{ color: var(--success); }}
    .kpi-num.blue {{ color: var(--blue); }}
    .kpi-lbl {{
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em;
      color: var(--text-secondary); font-weight: 500; margin-top: 0.15rem;
    }}

    /* ── ACTION QUEUE ── */
    .section-header {{
      display: flex; justify-content: space-between; align-items: center;
      margin: 2rem 0 1rem 0;
    }}
    .section-title {{ font-size: 1.1rem; font-weight: 600; letter-spacing: -0.015em; }}
    .count-pill {{
      background: var(--gold-dim); border: 1px solid var(--hairline-gold);
      color: var(--gold-accent); font-size: 0.72rem; font-weight: 600;
      padding: 0.2rem 0.65rem; border-radius: var(--pill);
    }}
    .contact-row {{
      display: flex; align-items: center; gap: 1rem;
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: 14px; padding: 0.85rem 1.25rem;
      margin-bottom: 0.65rem; transition: all 0.2s ease;
    }}
    .contact-row:hover {{ border-color: var(--hairline-gold); background: var(--bg-card-elevated); }}
    .contact-avatar {{
      width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 0.85rem;
    }}
    .av-hot {{ background: rgba(248,113,113,0.2); color: var(--danger); }}
    .av-warm {{ background: rgba(251,191,36,0.2); color: var(--warning); }}
    .av-cold {{ background: rgba(96,165,250,0.15); color: var(--blue); }}
    .contact-info {{ flex: 1; }}
    .contact-name {{ font-size: 0.88rem; font-weight: 600; }}
    .contact-meta {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.1rem; }}
    .contact-actions {{ display: flex; gap: 0.4rem; }}
    .btn-action {{
      font-size: 0.72rem; font-weight: 500; padding: 0.3rem 0.7rem;
      border-radius: var(--pill); border: 1px solid var(--hairline);
      background: transparent; color: var(--text-secondary);
      cursor: pointer; transition: all 0.2s ease;
    }}
    .btn-action.primary {{ background: var(--text-primary); color: #000; border-color: var(--text-primary); }}
    .btn-action:hover:not(.primary) {{ border-color: var(--gold-accent); color: var(--gold-accent); }}
    .heat-badge {{
      font-size: 0.65rem; font-weight: 700; padding: 0.18rem 0.5rem;
      border-radius: var(--pill); text-transform: uppercase; letter-spacing: 0.06em;
    }}
    .heat-hot {{ background: rgba(248,113,113,0.15); color: var(--danger); border: 1px solid rgba(248,113,113,0.3); }}
    .heat-warm {{ background: rgba(251,191,36,0.15); color: var(--warning); border: 1px solid rgba(251,191,36,0.3); }}
    .heat-cold {{ background: rgba(96,165,250,0.1); color: var(--blue); border: 1px solid rgba(96,165,250,0.25); }}

    /* ── PIPELINES ── */
    .pipeline-tabs {{
      display: flex; gap: 0.3rem; margin-bottom: 1.25rem;
    }}
    .pipe-tab {{
      font-size: 0.82rem; font-weight: 500; padding: 0.5rem 1.1rem;
      border-radius: var(--pill); border: 1px solid var(--hairline);
      background: transparent; color: var(--text-secondary); cursor: pointer;
      transition: all 0.2s ease;
    }}
    .pipe-tab.active {{ background: var(--text-primary); color: #000; border-color: var(--text-primary); }}
    .kanban-track {{
      overflow-x: auto; padding-bottom: 0.5rem;
      scrollbar-width: thin; scrollbar-color: rgba(255,255,255,0.1) transparent;
    }}
    .kanban {{
      display: flex; gap: 0.85rem; min-width: max-content;
    }}
    .kanban-col {{
      width: 185px; flex-shrink: 0;
    }}
    .kanban-stage {{
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em;
      color: var(--text-secondary); font-weight: 600;
      padding: 0.5rem 0.75rem; margin-bottom: 0.5rem;
      background: rgba(255,255,255,0.04); border-radius: 8px;
    }}
    .deal-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 0.5rem;
      cursor: grab; transition: all 0.2s ease;
    }}
    .deal-card:hover {{ border-color: var(--hairline-gold); transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.5); }}
    .deal-name {{ font-size: 0.82rem; font-weight: 600; }}
    .deal-addr {{ font-size: 0.72rem; color: var(--text-secondary); margin: 0.2rem 0; }}
    .deal-val {{ font-size: 0.8rem; font-weight: 600; color: var(--gold-accent); }}
    .deal-days {{ font-size: 0.68rem; color: var(--text-secondary); margin-top: 0.25rem; }}
    .kanban-add {{
      font-size: 0.75rem; color: var(--text-secondary); cursor: pointer;
      padding: 0.5rem 0.75rem; text-align: center;
      border: 1px dashed var(--hairline); border-radius: 10px;
      transition: all 0.2s ease;
    }}
    .kanban-add:hover {{ border-color: var(--gold-accent); color: var(--gold-accent); }}

    /* ── NET SHEETS ── */
    .net-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1.5rem 0; }}
    .net-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: var(--r); padding: 1.5rem 1.75rem;
    }}
    .net-title {{
      font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.09em;
      color: var(--gold-accent); font-weight: 600; margin-bottom: 1rem;
    }}
    .net-field {{ margin-bottom: 0.85rem; }}
    .net-label {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.3rem; }}
    .net-input {{
      width: 100%; background: rgba(255,255,255,0.05);
      border: 1px solid var(--hairline); border-radius: 10px;
      padding: 0.6rem 0.85rem; color: #fff; font-size: 0.88rem;
      outline: none; font-family: inherit;
    }}
    .net-input:focus {{ border-color: var(--gold-accent); }}
    .net-result-row {{
      display: flex; justify-content: space-between; align-items: center;
      padding: 0.5rem 0; border-bottom: 1px solid var(--hairline);
      font-size: 0.82rem;
    }}
    .net-result-row.total {{
      border-bottom: none; padding-top: 0.75rem; margin-top: 0.25rem;
      font-weight: 700; font-size: 1rem;
    }}
    .net-result-val {{ font-family: 'JetBrains Mono', monospace; }}
    .net-result-val.positive {{ color: var(--success); }}
    .net-result-val.negative {{ color: var(--danger); }}
    .btn-calc {{
      width: 100%; margin-top: 1rem; padding: 0.7rem 1rem;
      background: var(--text-primary); color: #000; border: none;
      border-radius: var(--pill); font-size: 0.85rem; font-weight: 600;
      cursor: pointer; transition: all 0.2s ease;
    }}
    .btn-calc:hover {{ transform: scale(1.02); box-shadow: 0 6px 18px rgba(255,255,255,0.15); }}

    /* ── CMA PANEL ── */
    .cma-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin: 1.5rem 0; }}
    .cma-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: var(--r); padding: 1.5rem 1.75rem;
    }}
    .cma-board-badge {{
      display: inline-flex; align-items: center; gap: 0.4rem;
      background: var(--gold-dim); border: 1px solid var(--hairline-gold);
      color: var(--gold-accent); font-size: 0.72rem; font-weight: 600;
      padding: 0.22rem 0.65rem; border-radius: var(--pill);
      margin-bottom: 0.85rem; text-transform: uppercase; letter-spacing: 0.07em;
    }}
    .comp-row {{
      display: flex; justify-content: space-between; align-items: center;
      padding: 0.6rem 0; border-bottom: 1px solid var(--hairline);
      font-size: 0.82rem;
    }}
    .comp-row:last-child {{ border-bottom: none; }}
    .comp-addr {{ color: var(--text-secondary); font-size: 0.78rem; }}
    .comp-price {{ font-weight: 600; font-family: 'JetBrains Mono', monospace; }}
    .comp-status {{
      font-size: 0.65rem; padding: 0.18rem 0.5rem; border-radius: var(--pill);
      font-weight: 600; text-transform: uppercase;
    }}
    .status-sold {{ background: rgba(52,211,153,0.12); color: var(--success); }}
    .status-active {{ background: rgba(96,165,250,0.12); color: var(--blue); }}
    .status-pending {{ background: rgba(251,191,36,0.12); color: var(--warning); }}
    .cma-summary {{
      background: rgba(229,200,144,0.06); border: 1px solid var(--hairline-gold);
      border-radius: 12px; padding: 1rem 1.25rem; margin-top: 1rem;
    }}
    .cma-summary-title {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--gold-accent); margin-bottom: 0.5rem; }}
    .cma-price-tiers {{ display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }}
    .cma-tier {{
      flex: 1; background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: 10px; padding: 0.75rem 0.9rem; text-align: center;
    }}
    .cma-tier-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-secondary); }}
    .cma-tier-price {{ font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-top: 0.2rem; font-family: 'JetBrains Mono', monospace; }}

    /* ── FSBO / EXPIREDS ── */
    .prospect-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: 14px; padding: 1rem 1.25rem; margin-bottom: 0.65rem;
      transition: all 0.2s ease;
    }}
    .prospect-card:hover {{ border-color: var(--hairline-gold); }}
    .prospect-header {{ display: flex; justify-content: space-between; align-items: flex-start; }}
    .prospect-name {{ font-size: 0.88rem; font-weight: 600; }}
    .prospect-addr {{ font-size: 0.75rem; color: var(--text-secondary); margin: 0.2rem 0; }}
    .prospect-tags {{ display: flex; gap: 0.35rem; margin-top: 0.35rem; flex-wrap: wrap; }}
    .ptag {{
      font-size: 0.65rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
      padding: 0.18rem 0.5rem; border-radius: var(--pill);
    }}
    .ptag-fsbo {{ background: rgba(251,191,36,0.12); color: var(--warning); border: 1px solid rgba(251,191,36,0.25); }}
    .ptag-exp {{ background: rgba(248,113,113,0.12); color: var(--danger); border: 1px solid rgba(248,113,113,0.25); }}
    .ptag-follow {{ background: rgba(96,165,250,0.1); color: var(--blue); border: 1px solid rgba(96,165,250,0.2); }}
    .prospect-actions {{ display: flex; gap: 0.4rem; margin-top: 0.6rem; }}

    /* ── PLAYBOOK ── */
    .playbook-grid {{ display: grid; grid-template-columns: 240px 1fr; gap: 1.5rem; margin-top: 1.5rem; }}
    .script-menu {{ display: flex; flex-direction: column; gap: 0.35rem; }}
    .script-item {{
      font-size: 0.82rem; font-weight: 500; padding: 0.6rem 0.9rem;
      border-radius: 10px; border: 1px solid var(--hairline);
      background: transparent; color: var(--text-secondary); cursor: pointer;
      transition: all 0.2s ease; text-align: left;
    }}
    .script-item.active, .script-item:hover {{
      background: var(--gold-dim); border-color: var(--hairline-gold);
      color: var(--text-primary);
    }}
    .script-viewer {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: var(--r); padding: 1.5rem 1.75rem;
    }}
    .script-title {{ font-size: 1rem; font-weight: 600; margin-bottom: 0.25rem; }}
    .script-category {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--gold-accent); margin-bottom: 1.25rem; }}
    .script-block {{
      background: rgba(255,255,255,0.03); border: 1px solid var(--hairline);
      border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem;
    }}
    .script-speaker {{
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.09em;
      font-weight: 700; margin-bottom: 0.4rem;
    }}
    .script-speaker.agent {{ color: var(--gold-accent); }}
    .script-speaker.prospect {{ color: var(--blue); }}
    .script-speaker.objection {{ color: var(--danger); }}
    .script-text {{ font-size: 0.85rem; line-height: 1.55; color: var(--text-primary); }}
    .objection-tip {{
      background: rgba(248,113,113,0.06); border: 1px solid rgba(248,113,113,0.2);
      border-radius: 10px; padding: 0.75rem 1rem; font-size: 0.8rem;
      color: var(--text-secondary); margin-top: 0.75rem; line-height: 1.5;
    }}
    .objection-tip strong {{ color: var(--danger); }}

    /* ── COPILOT ── */
    .workspace-grid {{ display: grid; grid-template-columns: 1.4fr 0.85fr; gap: 1.75rem; margin-bottom: 3rem; }}
    .copilot-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: var(--r); display: flex; flex-direction: column;
      height: 600px; position: sticky; top: 4rem;
    }}
    .copilot-header {{
      padding: 1rem 1.25rem; border-bottom: 1px solid var(--hairline);
      display: flex; align-items: center; justify-content: space-between;
    }}
    .copilot-agent {{ display: flex; align-items: center; gap: 0.75rem; }}
    .copilot-avatar {{
      width: 36px; height: 36px; border-radius: 50%;
      border: 1.5px solid var(--gold-accent); object-fit: cover;
    }}
    .copilot-name {{ font-size: 0.9rem; font-weight: 600; }}
    .copilot-sub {{ font-size: 0.7rem; color: var(--success); display: flex; align-items: center; gap: 0.3rem; }}
    .copilot-feed {{
      flex: 1; padding: 1.25rem; overflow-y: auto;
      display: flex; flex-direction: column; gap: 0.85rem;
    }}
    .msg-bubble {{ padding: 0.8rem 1rem; border-radius: 14px; font-size: 0.84rem; line-height: 1.45; max-width: 92%; }}
    .msg-agent {{ background: rgba(255,255,255,0.05); border: 1px solid var(--hairline); align-self: flex-start; }}
    .msg-user {{ background: var(--gold-accent); color: #000; font-weight: 500; align-self: flex-end; }}
    .copilot-chips {{ display: flex; gap: 0.4rem; padding: 0 1.25rem 0.6rem; overflow-x: auto; scrollbar-width: none; flex-wrap: wrap; }}
    .chip {{
      font-size: 0.72rem; background: rgba(255,255,255,0.05); border: 1px solid var(--hairline);
      padding: 0.3rem 0.7rem; border-radius: var(--pill); color: var(--text-secondary);
      cursor: pointer; transition: all 0.2s ease; white-space: nowrap;
    }}
    .chip:hover {{ color: var(--text-primary); border-color: var(--gold-accent); background: rgba(229,200,144,0.08); }}
    .copilot-input-box {{ padding: 1rem 1.25rem; border-top: 1px solid var(--hairline); display: flex; gap: 0.65rem; }}
    .copilot-input {{
      flex: 1; background: rgba(255,255,255,0.04); border: 1px solid var(--hairline);
      border-radius: 10px; padding: 0.65rem 0.9rem; color: #fff; font-size: 0.84rem;
      outline: none; font-family: inherit;
    }}
    .copilot-input:focus {{ border-color: var(--gold-accent); }}
    .btn-send {{
      background: var(--text-primary); color: #000; border: none;
      padding: 0.65rem 1.1rem; border-radius: 10px; font-weight: 600;
      cursor: pointer; transition: transform 0.15s ease;
    }}
    .btn-send:hover {{ transform: scale(1.03); }}

    /* ── STAGED QUEUE ── */
    .staged-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: var(--r); padding: 1.5rem 1.75rem; margin-bottom: 1.25rem;
      transition: all 0.25s ease;
    }}
    .staged-card:hover {{ border-color: var(--hairline-gold); background: var(--bg-card-elevated); box-shadow: 0 12px 28px rgba(0,0,0,0.5); }}
    .staged-tag {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; }}
    .specialist-badge {{
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.1em;
      color: var(--gold-accent); font-weight: 700;
    }}
    .timestamp {{ font-size: 0.72rem; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; }}
    .staged-headline {{ font-size: 1.05rem; font-weight: 600; margin-bottom: 0.4rem; }}
    .staged-body {{ font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 1rem; }}
    .staged-actions {{ display: flex; gap: 0.65rem; }}
    .btn-approve {{
      background: var(--text-primary); color: #000; font-weight: 600; font-size: 0.8rem;
      padding: 0.45rem 1.1rem; border-radius: var(--pill); border: none;
      cursor: pointer; transition: all 0.2s ease;
    }}
    .btn-approve:hover {{ transform: scale(1.03); }}
    .btn-revise {{
      background: transparent; color: var(--text-secondary); font-size: 0.8rem;
      padding: 0.45rem 1.1rem; border-radius: var(--pill);
      border: 1px solid var(--hairline); cursor: pointer; transition: all 0.2s ease;
    }}
    .btn-revise:hover {{ border-color: var(--gold-accent); color: var(--gold-accent); }}

    /* ── TRANSACTION TRACKER ── */
    .txn-card {{
      background: var(--bg-card); border: 1px solid var(--hairline);
      border-radius: var(--r); padding: 1.5rem 1.75rem; margin-bottom: 1rem;
    }}
    .txn-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem; }}
    .txn-address {{ font-size: 1rem; font-weight: 600; }}
    .txn-price {{ font-size: 0.95rem; font-weight: 700; color: var(--gold-accent); font-family: 'JetBrains Mono', monospace; }}
    .milestone-row {{
      display: flex; align-items: center; gap: 0.85rem;
      padding: 0.65rem 0; border-bottom: 1px solid var(--hairline);
    }}
    .milestone-row:last-child {{ border-bottom: none; }}
    .milestone-icon {{
      width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
      display: flex; align-items: center; justify-content: center;
      font-size: 0.75rem;
    }}
    .m-done {{ background: rgba(52,211,153,0.15); color: var(--success); }}
    .m-active {{ background: rgba(251,191,36,0.15); color: var(--warning); }}
    .m-pending {{ background: rgba(255,255,255,0.06); color: var(--text-secondary); }}
    .milestone-name {{ font-size: 0.84rem; font-weight: 500; flex: 1; }}
    .milestone-date {{ font-size: 0.75rem; font-family: 'JetBrains Mono', monospace; color: var(--text-secondary); }}
    .milestone-countdown {{ font-size: 0.72rem; font-weight: 600; padding: 0.18rem 0.5rem; border-radius: var(--pill); }}
    .cd-urgent {{ background: rgba(248,113,113,0.12); color: var(--danger); }}
    .cd-ok {{ background: rgba(52,211,153,0.1); color: var(--success); }}

    /* ── FOOTER ── */
    .portal-footer {{
      border-top: 1px solid var(--hairline); padding: 1.75rem 2rem;
      max-width: 1400px; margin: 0 auto;
      display: flex; justify-content: space-between;
      color: var(--text-secondary); font-size: 0.75rem;
    }}

    /* ── CRM CLIENT DOSSIER & EMAIL TRACKER MODAL ── */
    .crm-modal-backdrop {{
      position: fixed; top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.78);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      z-index: 1000;
      display: flex; align-items: center; justify-content: center;
      padding: 1.5rem;
      opacity: 0; pointer-events: none;
      transition: opacity 0.25s ease;
    }}
    .crm-modal-backdrop.open {{
      opacity: 1; pointer-events: auto;
    }}
    .crm-modal-card {{
      background: rgba(16, 16, 22, 0.98);
      border: 1px solid rgba(229, 200, 144, 0.35);
      border-radius: 20px;
      box-shadow: 0 32px 80px rgba(0, 0, 0, 0.95), 0 0 30px rgba(229, 200, 144, 0.15);
      width: 100%; max-width: 860px;
      max-height: 90vh;
      display: flex; flex-direction: column;
      overflow: hidden;
      transform: translateY(15px) scale(0.98);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    .crm-modal-backdrop.open .crm-modal-card {{
      transform: translateY(0) scale(1);
    }}
    .crm-modal-header {{
      padding: 1.25rem 1.75rem;
      border-bottom: 1px solid var(--hairline);
      display: flex; justify-content: space-between; align-items: center;
      background: rgba(255, 255, 255, 0.02);
    }}
    .crm-header-profile {{ display: flex; align-items: center; gap: 1rem; }}
    .crm-header-avatar {{
      width: 46px; height: 46px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-weight: 700; font-size: 1.1rem;
      border: 2px solid var(--gold-accent);
      background: rgba(229, 200, 144, 0.15); color: #fff;
    }}
    .crm-header-name {{ font-size: 1.15rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; }}
    .crm-header-meta {{ font-size: 0.8rem; color: var(--text-secondary); margin-top: 0.2rem; display: flex; gap: 0.8rem; flex-wrap: wrap; }}
    .crm-close-btn {{
      background: transparent; border: none; color: var(--text-secondary);
      font-size: 1.3rem; cursor: pointer; padding: 0.3rem 0.6rem; border-radius: 8px;
    }}
    .crm-close-btn:hover {{ color: #fff; background: rgba(255, 255, 255, 0.08); }}
    
    .crm-tabs {{
      display: flex; gap: 0.4rem; padding: 0.75rem 1.75rem;
      border-bottom: 1px solid var(--hairline);
      background: rgba(0, 0, 0, 0.3);
    }}
    .crm-tab {{
      font-size: 0.82rem; font-weight: 500; padding: 0.4rem 1rem;
      border-radius: var(--pill); border: 1px solid var(--hairline);
      background: transparent; color: var(--text-secondary); cursor: pointer;
      transition: all 0.2s ease;
    }}
    .crm-tab.active {{
      background: rgba(255, 255, 255, 0.12); color: var(--text-primary);
      border-color: var(--gold-accent);
    }}
    .crm-body {{
      flex: 1; overflow-y: auto; padding: 1.5rem 1.75rem;
      display: flex; flex-direction: column; gap: 1rem;
    }}
    .crm-tab-content {{ display: none; }}
    .crm-tab-content.active {{ display: block; }}

    .thread-msg {{
      background: var(--bg-card);
      border: 1px solid var(--hairline);
      border-radius: 14px; padding: 1rem 1.25rem;
      margin-bottom: 0.85rem;
    }}
    .thread-msg.system {{
      border-left: 3px solid var(--gold-accent);
      background: rgba(229, 200, 144, 0.04);
    }}
    .thread-msg.sent {{
      border-left: 3px solid var(--blue);
    }}
    .thread-msg.received {{
      border-left: 3px solid var(--success);
    }}
    .thread-header {{
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 0.4rem;
    }}
    .thread-sender {{ font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; }}
    .thread-sender.system {{ color: var(--gold-accent); }}
    .thread-sender.sent {{ color: var(--blue); }}
    .thread-sender.received {{ color: var(--success); }}
    .thread-time {{ font-size: 0.72rem; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; }}
    .thread-subject {{ font-size: 0.9rem; font-weight: 600; margin-bottom: 0.3rem; color: var(--text-primary); }}
    .thread-body {{ font-size: 0.84rem; color: var(--text-secondary); line-height: 1.5; white-space: pre-line; }}
    
    .crm-field {{ margin-bottom: 1rem; }}
    .crm-label {{ font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.35rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }}
    .crm-input {{
      width: 100%; background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--hairline); border-radius: 10px;
      padding: 0.65rem 0.85rem; color: #fff; font-size: 0.85rem;
      outline: none; font-family: inherit;
    }}
    .crm-input:focus {{ border-color: var(--gold-accent); }}
    .crm-textarea {{
      width: 100%; height: 130px; background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--hairline); border-radius: 10px;
      padding: 0.75rem 0.85rem; color: #fff; font-size: 0.85rem;
      outline: none; font-family: inherit; resize: vertical; line-height: 1.5;
    }}
    .crm-textarea:focus {{ border-color: var(--gold-accent); }}
    .template-chips {{ display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.85rem; }}
    .tmpl-chip {{
      font-size: 0.72rem; background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--hairline); border-radius: var(--pill);
      padding: 0.3rem 0.65rem; color: var(--text-secondary); cursor: pointer;
      transition: all 0.15s ease;
    }}
    .tmpl-chip:hover {{ color: #fff; border-color: var(--gold-accent); background: rgba(229, 200, 144, 0.1); }}

    .crm-filter-bar {{
      display: flex; gap: 0.4rem; margin: 0.8rem 0 1.25rem 0;
      overflow-x: auto; scrollbar-width: none;
    }}
    .crm-filter-chip {{
      font-size: 0.75rem; font-weight: 500; padding: 0.32rem 0.8rem;
      border-radius: var(--pill); border: 1px solid var(--hairline);
      background: transparent; color: var(--text-secondary); cursor: pointer;
      transition: all 0.2s ease; white-space: nowrap;
    }}
    .crm-filter-chip.active, .crm-filter-chip:hover {{
      background: var(--gold-dim); border-color: var(--hairline-gold);
      color: var(--text-primary);
    }}

    /* ── LISTING INTAKE QUEUE ── */
    .intake-grid {{ display: grid; grid-template-columns: 1fr 1.2fr; gap: 1.25rem; margin-top: 1rem; }}
    .intake-form-card .crm-field {{ margin-bottom: 0.65rem; }}
    .listing-queue-card {{
      background: var(--bg-card-elevated); border: 1px solid var(--hairline);
      border-radius: 16px; padding: 1.1rem 1.25rem; margin-bottom: 0.75rem;
    }}
    .listing-queue-card:hover {{ border-color: var(--hairline-gold); }}
    .lq-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 0.75rem; }}
    .lq-title {{ font-size: 0.95rem; font-weight: 600; }}
    .lq-meta {{ font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.2rem; }}
    .lq-keystone {{
      font-size: 0.78rem; color: var(--gold-accent); margin: 0.65rem 0;
      font-family: 'JetBrains Mono', monospace;
    }}
    .lq-narrative {{
      font-size: 0.82rem; color: var(--text-secondary); line-height: 1.55;
      border-left: 2px solid var(--hairline-gold); padding-left: 0.75rem; margin: 0.5rem 0;
    }}
    .lq-actions {{ display: flex; gap: 0.5rem; margin-top: 0.75rem; flex-wrap: wrap; }}
    .btn-approve {{
      font-size: 0.78rem; font-weight: 600; padding: 0.45rem 1rem;
      border-radius: var(--pill); border: none; cursor: pointer;
      background: linear-gradient(135deg,#f7e7c4,#e5c890); color: #000;
    }}
    .btn-approve:disabled {{ opacity: 0.5; cursor: not-allowed; }}
    .intake-posture {{
      font-size: 0.72rem; color: var(--text-secondary); margin-top: 0.75rem;
      padding: 0.5rem 0.75rem; border-radius: 10px; background: rgba(255,255,255,0.03);
      border: 1px solid var(--hairline);
    }}

    @media (max-width: 1100px) {{
      .kpi-bar {{ grid-template-columns: repeat(3, 1fr); }}
      .workspace-grid, .net-grid, .cma-grid {{ grid-template-columns: 1fr; }}
      .playbook-grid {{ grid-template-columns: 1fr; }}
      .copilot-card {{ position: static; height: 480px; }}
      .intake-grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 680px) {{
      .kpi-bar {{ grid-template-columns: repeat(2, 1fr); }}
      .nav-tabs {{ display: none; }}
    }}
  </style>
</head>
<body>

  <!-- LIQUID GLASS NAV -->
  <header class="portal-nav">
    <div class="nav-inner">
      <div class="brand">
        <span class="brand-dot"></span>
        <span class="brand-name">{t.name}</span>
        <span class="badge">TENANT: {t.subdomain_slug}</span>
      </div>

      <div class="nav-tabs">
        <button class="nav-tab active" onclick="switchPanel('dashboard', this)">Dashboard</button>
        <button class="nav-tab" onclick="switchPanel('pipeline', this)">Pipeline</button>
        <button class="nav-tab" onclick="switchPanel('netsheets', this)">Net Sheets</button>
        <button class="nav-tab" onclick="switchPanel('cma', this)">CMA</button>
        <button class="nav-tab" onclick="switchPanel('prospects', this)">FSBO / Expired</button>
        <button class="nav-tab" onclick="switchPanel('listings', this)">Listings</button>
        <button class="nav-tab" onclick="switchPanel('playbook', this)">Playbook</button>
        <button class="nav-tab" onclick="switchPanel('transactions', this)">Transactions</button>
      </div>

      <div class="nav-right">
        <div class="live-dot"><span class="pulse-dot"></span>Fleet Active</div>
        <a href="index.html" class="btn-sm" target="_blank">Front Door ↗</a>
      </div>
    </div>
  </header>

  <div class="os-shell">

    <!-- ═══════════════════════════════════════════════
         PANEL 1: EXECUTIVE DASHBOARD
    ═══════════════════════════════════════════════ -->
    <div id="panel-dashboard" class="os-panel active">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:clamp(1.6rem,3vw,2.2rem); font-weight:600; letter-spacing:-0.025em;">Executive Workspace</h1>
        <p style="font-size:0.95rem; color:var(--text-secondary); margin-top:0.35rem;">{market_label} • Harbor, Keystone & Quill operating under your supervision.</p>
      </div>

      <!-- KPI BAR -->
      <div class="kpi-bar">
        <div class="kpi">
          <div class="kpi-num gold">$14.2M</div>
          <div class="kpi-lbl">Pipeline Value</div>
        </div>
        <div class="kpi">
          <div class="kpi-num gold">$284K</div>
          <div class="kpi-lbl">Projected GCI</div>
        </div>
        <div class="kpi">
          <div class="kpi-num green">7</div>
          <div class="kpi-lbl">Active Listings</div>
        </div>
        <div class="kpi">
          <div class="kpi-num green">3</div>
          <div class="kpi-lbl">Pending Closings</div>
        </div>
        <div class="kpi">
          <div class="kpi-num blue" id="kpi-calls">12</div>
          <div class="kpi-lbl">Calls Today</div>
        </div>
        <div class="kpi">
          <div class="kpi-num" id="kpi-appts">4</div>
          <div class="kpi-lbl">Appointments Set</div>
        </div>
      </div>

      <!-- WORKSPACE: QUEUE + COPILOT -->
      <div class="workspace-grid">
        <section>
          <!-- ACTION QUEUE -->
          <div class="section-header" style="display:flex; justify-content:space-between; align-items:center;">
            <span class="section-title">🔥 Who Needs Contact Today</span>
            <div style="display:flex; align-items:center; gap:0.5rem;">
              <span class="count-pill" id="action-queue-count">5 Pending</span>
              <button onclick="addTestLead()" class="btn-sm" style="font-size:0.7rem; padding:0.18rem 0.6rem; cursor:pointer;" title="Simulate incoming front-door dossier inquiry">+ Demo Lead</button>
            </div>
          </div>

          <!-- CRM CATEGORY FILTER BAR -->
          <div class="crm-filter-bar">
            <button class="crm-filter-chip active" onclick="filterCrmQueue('ALL', this)">All Contacts</button>
            <button class="crm-filter-chip" onclick="filterCrmQueue('HOT', this)">🔥 Hot Leads</button>
            <button class="crm-filter-chip" onclick="filterCrmQueue('BUYER', this)">👤 Buyers</button>
            <button class="crm-filter-chip" onclick="filterCrmQueue('SELLER', this)">🏡 Sellers</button>
            <button class="crm-filter-chip" onclick="filterCrmQueue('FSBO', this)">🚪 FSBO</button>
            <button class="crm-filter-chip" onclick="filterCrmQueue('SPHERE', this)">💌 Sphere</button>
          </div>

          <div id="contact-rows-container">
          <div class="contact-row" data-category="BUYER" data-heat="HOT" data-client-id="maria_rodriguez">
            <div class="contact-avatar av-hot">MR</div>
            <div class="contact-info">
              <div class="contact-name">Maria Rodriguez <span class="heat-badge heat-hot">HOT BUYER</span></div>
              <div class="contact-meta">Buyer — Pre-approved $680K • Showing: Bella Terra • Next: Tomorrow</div>
            </div>
            <div class="contact-actions">
              <button class="btn-action primary" onclick="openClientDossier('maria_rodriguez')">💬 Dossier & Emails</button>
              <a href="tel:2395550144" class="btn-action" style="text-decoration:none;" onclick="logAction(this,'Called Maria')">📞 Call</a>
              <button class="btn-action" onclick="logAction(this,'SMS Drafted')">✉ Text</button>
            </div>
          </div>

          <div class="contact-row" data-category="SELLER" data-heat="HOT" data-client-id="walsh_couple">
            <div class="contact-avatar av-hot">DW</div>
            <div class="contact-info">
              <div class="contact-name">David & Karen Walsh <span class="heat-badge heat-hot">HOT SELLER</span></div>
              <div class="contact-meta">Seller — 22001 West Bay Blvd ($1.89M) • Keystone CMA sent • Follow-up today</div>
            </div>
            <div class="contact-actions">
              <button class="btn-action primary" onclick="openClientDossier('walsh_couple')">💬 Dossier & Emails</button>
              <a href="tel:2395550189" class="btn-action" style="text-decoration:none;" onclick="logAction(this,'Called Walsh')">📞 Call</a>
              <button class="btn-action" onclick="logAction(this,'Email Drafted')">✉ Email</button>
            </div>
          </div>

          <div class="contact-row" data-category="BUYER" data-heat="WARM" data-client-id="jennifer_liu">
            <div class="contact-avatar av-warm">JL</div>
            <div class="contact-info">
              <div class="contact-name">Jennifer Liu <span class="heat-badge heat-warm">WARM BUYER</span></div>
              <div class="contact-meta">Referral Lead — Chicago Relocation • Budget $650K • Follow-up due today</div>
            </div>
            <div class="contact-actions">
              <button class="btn-action primary" onclick="openClientDossier('jennifer_liu')">💬 Dossier & Emails</button>
              <a href="tel:3125550177" class="btn-action" style="text-decoration:none;" onclick="logAction(this,'Called Liu')">📞 Call</a>
              <button class="btn-action" onclick="logAction(this,'Snoozed 3 days')">⏰ Snooze</button>
            </div>
          </div>

          <div class="contact-row" data-category="FSBO" data-heat="WARM" data-client-id="thomas_cruz">
            <div class="contact-avatar av-warm">TC</div>
            <div class="contact-info">
              <div class="contact-name">Thomas Cruz <span class="heat-badge heat-warm">FSBO PROSPECT</span></div>
              <div class="contact-meta">FSBO — 3812 Stoneybrook (~$525K) • Owner not listed with agent yet</div>
            </div>
            <div class="contact-actions">
              <button class="btn-action primary" onclick="openClientDossier('thomas_cruz')">💬 Dossier & Emails</button>
              <a href="tel:2395550133" class="btn-action" style="text-decoration:none;" onclick="logAction(this,'Called Cruz')">📞 Call</a>
              <button class="btn-action" onclick="logAction(this,'Door knock logged')">🚪 Knock</button>
            </div>
          </div>

          <div class="contact-row" data-category="SPHERE" data-heat="COLD" data-client-id="nguyen_family">
            <div class="contact-avatar av-cold">BP</div>
            <div class="contact-info">
              <div class="contact-name">Beth & Paul Nguyen <span class="heat-badge heat-cold">SPHERE CLIENT</span></div>
              <div class="contact-meta">Sphere — Past clients 2022 • Annual Home Equity check-in (3 yr)</div>
            </div>
            <div class="contact-actions">
              <button class="btn-action primary" onclick="openClientDossier('nguyen_family')">💬 Dossier & Emails</button>
              <a href="tel:2395550199" class="btn-action" style="text-decoration:none;" onclick="logAction(this,'Texted Nguyen')">✉ Text</a>
              <button class="btn-action" onclick="logAction(this,'Moved to nurture')">💌 Nurture</button>
            </div>
          </div>
          </div><!-- /contact-rows-container -->

          <!-- STAGED QUEUE -->
          <div class="section-header" style="margin-top:2rem;">
            <span class="section-title">Staged Deliverables</span>
            <span class="count-pill">Human-in-the-Loop</span>
          </div>

          <div class="staged-card" id="card-cma">
            <div class="staged-tag">
              <span class="specialist-badge">📐 KEYSTONE • CMA LEAD</span>
              <span class="timestamp">Today 10:21 AM</span>
            </div>
            <h3 class="staged-headline">Comparative Market Analysis: Estero Corridor</h3>
            <p class="staged-body">Micro-neighborhood baseline $310/sqft with +$80K pool & roof adjustment. Strategic list recommendation: <strong>$848,800</strong> — Alpha spread vs Zillow: +$286,400.</p>
            <div class="staged-actions">
              <button class="btn-approve" onclick="approveCard('card-cma','CMA Valuation Approved & Locked')">✓ Approve Valuation</button>
              <button class="btn-revise" onclick="alert('Revision sent to Keystone.')">✎ Revise</button>
            </div>
          </div>

          <div class="staged-card" id="card-copy">
            <div class="staged-tag">
              <span class="specialist-badge">✍️ QUILL • MLS COPY LEAD</span>
              <span class="timestamp">Today 10:21 AM</span>
            </div>
            <h3 class="staged-headline">MLS Remarks & Social Launch Draft</h3>
            <p class="staged-body"><em>"Welcome to your Southwest Florida sanctuary in Estero! Expansive screened lanai overlooking tranquil water views, brand-new 2023 tile roof, open-concept chef's kitchen..."</em></p>
            <div class="staged-actions">
              <button class="btn-approve" onclick="approveCard('card-copy','Copy Approved for MLS Syndication')">✓ Approve Copy</button>
              <button class="btn-revise" onclick="alert('Editing in Quill...')">✎ Edit</button>
            </div>
          </div>
        </section>

        <!-- COPILOT -->
        <aside>
          <div class="copilot-card">
            <div class="copilot-header">
              <div class="copilot-agent">
                <img src="assets/headshot.png" class="copilot-avatar" alt="Copilot" onerror="this.style.display='none'">
                <div>
                  <div class="copilot-name">{t.name} Copilot</div>
                  <div class="copilot-sub"><span class="pulse-dot"></span>Online • Apex Agent</div>
                </div>
              </div>
              <span class="badge">SOVEREIGN</span>
            </div>
            <div class="copilot-feed" id="chat-feed">
              <div class="msg-bubble msg-agent">Good morning {t.name}. You have 5 contacts needing outreach today and 2 deliverables pending approval. No messages will be sent without your sign-off.</div>
              <div class="msg-bubble msg-agent">How can I assist with your {market_label} pipeline today?</div>
            </div>
            <div class="copilot-chips">
              <span class="chip" onclick="quickMsg('Draft follow-up SMS for Maria Rodriguez')">💬 Draft SMS</span>
              <span class="chip" onclick="quickMsg('Summarize todays action queue')">📋 Today Summary</span>
              <span class="chip" onclick="quickMsg('What is my projected GCI at current pipeline?')">💰 GCI Calc</span>
              <span class="chip" onclick="quickMsg('Explain Keystone CMA breakdown')">📐 Explain CMA</span>
            </div>
            <form class="copilot-input-box" onsubmit="sendMsg(event)">
              <input type="text" class="copilot-input" id="chat-input" placeholder="Ask your copilot..." autocomplete="off">
              <button type="submit" class="btn-send">Send</button>
            </form>
          </div>
        </aside>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL 2: DUAL PIPELINE
    ═══════════════════════════════════════════════ -->
    <div id="panel-pipeline" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">Deal Pipelines</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">Listing & Buyer Kanban — drag cards to advance stages</p>
      </div>
      <div class="pipeline-tabs">
        <button class="pipe-tab active" onclick="switchPipe('listing', this)">🏡 Listing Pipeline</button>
        <button class="pipe-tab" onclick="switchPipe('buyer', this)">👤 Buyer Pipeline</button>
      </div>

      <!-- LISTING KANBAN -->
      <div id="pipe-listing">
        <div class="kanban-track">
          <div class="kanban">
            <div class="kanban-col"><div class="kanban-stage">Prospect</div>
              <div class="deal-card"><div class="deal-name">Thomas Cruz</div><div class="deal-addr">3812 Stoneybrook Dr</div><div class="deal-val">~$525K</div><div class="deal-days">FSBO • Day 1</div></div>
              <div class="kanban-add" onclick="alert('Add new prospect...')">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Contacted</div>
              <div class="deal-card"><div class="deal-name">K. Hoffman</div><div class="deal-addr">21088 Bella Terra</div><div class="deal-val">~$610K</div><div class="deal-days">Contacted • Day 3</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Follow-Up</div>
              <div class="deal-card"><div class="deal-name">D & K Walsh</div><div class="deal-addr">22001 West Bay Blvd</div><div class="deal-val">$1.89M</div><div class="deal-days">CMA Sent • Day 5</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Appt Set</div>
              <div class="deal-card"><div class="deal-name">A. Petrov</div><div class="deal-addr">14220 Riva Del Lago</div><div class="deal-val">~$790K</div><div class="deal-days">Fri 2PM</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">CMA Prepared</div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Listing Presentation</div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Signed</div>
              <div class="deal-card"><div class="deal-name">E. Nakamura</div><div class="deal-addr">9120 Corsea Del Fontana</div><div class="deal-val">$548K</div><div class="deal-days">Active MLS</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Under Contract</div>
              <div class="deal-card" style="border-color:rgba(251,191,36,0.35)"><div class="deal-name">Peralta LLC</div><div class="deal-addr">1646 Heritage Dr</div><div class="deal-val">$515K</div><div class="deal-days">Closes Oct 15</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Closed 🎉</div>
              <div class="deal-card" style="border-color:rgba(52,211,153,0.35)"><div class="deal-name">R. Okonkwo</div><div class="deal-addr">20125 Hammocks Ln</div><div class="deal-val">$592K</div><div class="deal-days">Sep 2 • +$17,760 GCI</div></div>
            </div>
          </div>
        </div>
      </div>

      <!-- BUYER KANBAN -->
      <div id="pipe-buyer" style="display:none;">
        <div class="kanban-track">
          <div class="kanban">
            <div class="kanban-col" id="buyer-col-new-lead"><div class="kanban-stage">New Lead</div>
              <div class="deal-card"><div class="deal-name">J. Liu</div><div class="deal-addr">Relocating from Chicago</div><div class="deal-val">Budget $650K</div><div class="deal-days">Referral • Day 1</div></div>
              <div class="kanban-add" onclick="addTestLead()">+ Add Lead</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Qualified</div>
              <div class="deal-card"><div class="deal-name">The Park Family</div><div class="deal-addr">Golf community pref</div><div class="deal-val">Budget $1.2M</div><div class="deal-days">Day 4</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Consultation</div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Pre-Approval</div>
              <div class="deal-card"><div class="deal-name">M. Rodriguez</div><div class="deal-addr">Estero / Bella Terra</div><div class="deal-val">Approved $680K</div><div class="deal-days">Day 12</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Showings</div>
              <div class="deal-card"><div class="deal-name">S. & T. Brennan</div><div class="deal-addr">West Bay Club area</div><div class="deal-val">Budget $890K</div><div class="deal-days">3 showings done</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Offer</div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Under Contract</div>
              <div class="deal-card" style="border-color:rgba(251,191,36,0.35)"><div class="deal-name">C. & L. Dumont</div><div class="deal-addr">21450 Bella Terra Blvd</div><div class="deal-val">$848,800</div><div class="deal-days">Closes Oct 29</div></div>
              <div class="kanban-add">+ Add</div>
            </div>
            <div class="kanban-col"><div class="kanban-stage">Closed 🎉</div>
              <div class="deal-card" style="border-color:rgba(52,211,153,0.35)"><div class="deal-name">A. Fernandez</div><div class="deal-addr">9301 Estero River Cir</div><div class="deal-val">$472K</div><div class="deal-days">Aug 28 • +$7,080 GCI</div></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL 3: NET SHEETS
    ═══════════════════════════════════════════════ -->
    <div id="panel-netsheets" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">Financial Net Sheets</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">Florida-calibrated • Use during listing appointments & buyer consultations</p>
      </div>
      <div class="net-grid">

        <!-- SELLER NET SHEET -->
        <div class="net-card">
          <div class="net-title">🏡 Seller Estimated Net Proceeds (Florida)</div>
          <div class="net-field">
            <div class="net-label">List / Sale Price</div>
            <input type="number" class="net-input" id="s-price" placeholder="848800" oninput="calcSeller()">
          </div>
          <div class="net-field">
            <div class="net-label">Brokerage Commission (%)</div>
            <input type="number" class="net-input" id="s-comm" placeholder="5.5" step="0.1" oninput="calcSeller()">
          </div>
          <div class="net-field">
            <div class="net-label">Estimated Mortgage Payoff ($)</div>
            <input type="number" class="net-input" id="s-mort" placeholder="94000" oninput="calcSeller()">
          </div>
          <div class="net-field">
            <div class="net-label">HOA Estoppel / Prorations ($)</div>
            <input type="number" class="net-input" id="s-hoa" placeholder="750" oninput="calcSeller()">
          </div>
          <button class="btn-calc" onclick="calcSeller()">Calculate Net Proceeds</button>

          <div style="margin-top:1.25rem;" id="seller-results"></div>
        </div>

        <!-- BUYER CASH-TO-CLOSE -->
        <div class="net-card">
          <div class="net-title">🔑 Buyer Estimated Cash-to-Close (Florida)</div>
          <div class="net-field">
            <div class="net-label">Purchase Price</div>
            <input type="number" class="net-input" id="b-price" placeholder="680000" oninput="calcBuyer()">
          </div>
          <div class="net-field">
            <div class="net-label">Down Payment (%)</div>
            <input type="number" class="net-input" id="b-down" placeholder="20" step="1" oninput="calcBuyer()">
          </div>
          <div class="net-field">
            <div class="net-label">Loan Origination / Lender Fees ($)</div>
            <input type="number" class="net-input" id="b-lender" placeholder="3500" oninput="calcBuyer()">
          </div>
          <div class="net-field">
            <div class="net-label">Annual Property Tax (for escrow)</div>
            <input type="number" class="net-input" id="b-tax" placeholder="6240" oninput="calcBuyer()">
          </div>
          <button class="btn-calc" onclick="calcBuyer()">Calculate Cash-to-Close</button>

          <div style="margin-top:1.25rem;" id="buyer-results"></div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL 4: CMA SYSTEM
    ═══════════════════════════════════════════════ -->
    <div id="panel-cma" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">CMA Reports</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">Dual market boards: Royal Palm Coast (SWFL) & Miami REALTORS®</p>
      </div>
      <div class="cma-grid">

        <!-- RPCRA CMA -->
        <div class="cma-card">
          <div class="cma-board-badge">📍 Royal Palm Coast (RPCRA)</div>
          <div style="font-size:0.95rem; font-weight:600; margin-bottom:1rem;">Bella Terra Subdivision — Estero, FL</div>
          <div class="comp-row"><span class="comp-addr">21390 Bella Terra Blvd</span><span class="comp-status status-sold">Sold</span><span class="comp-price">$579K</span></div>
          <div class="comp-row"><span class="comp-addr">21502 Bella Terra Blvd</span><span class="comp-status status-sold">Sold</span><span class="comp-price">$592K</span></div>
          <div class="comp-row"><span class="comp-addr">21620 Bella Terra Blvd</span><span class="comp-status status-active">Active</span><span class="comp-price">$615K</span></div>
          <div class="comp-row"><span class="comp-addr">21285 Bella Terra Blvd</span><span class="comp-status status-pending">Pending</span><span class="comp-price">$588K</span></div>
          <div class="cma-summary">
            <div class="cma-summary-title">Keystone Recommendation — 21450 Bella Terra</div>
            <div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.5rem;">Adjustments: +$50K Pool • +$30K Post-Ian Roof • Baseline $310/sqft</div>
            <div class="cma-price-tiers">
              <div class="cma-tier"><div class="cma-tier-label">14-Day Fast</div><div class="cma-tier-price">$789K</div></div>
              <div class="cma-tier"><div class="cma-tier-label">Recommended</div><div class="cma-tier-price">$849K</div></div>
              <div class="cma-tier"><div class="cma-tier-label">Stretch</div><div class="cma-tier-price">$900K</div></div>
            </div>
          </div>
        </div>

        <!-- MIAMI REALTORS CMA -->
        <div class="cma-card">
          <div class="cma-board-badge">📍 Miami REALTORS®</div>
          <div style="font-size:0.95rem; font-weight:600; margin-bottom:1rem;">Brickell / Edgewater — Miami, FL</div>
          <div class="comp-row"><span class="comp-addr">1000 Brickell Plaza #3205</span><span class="comp-status status-sold">Sold</span><span class="comp-price">$1.12M</span></div>
          <div class="comp-row"><span class="comp-addr">88 SW 7th St #4802</span><span class="comp-status status-sold">Sold</span><span class="comp-price">$945K</span></div>
          <div class="comp-row"><span class="comp-addr">Brickell City Centre Unit 18C</span><span class="comp-status status-active">Active</span><span class="comp-price">$1.29M</span></div>
          <div class="comp-row"><span class="comp-addr">2 Biscayne Blvd #5501</span><span class="comp-status status-pending">Pending</span><span class="comp-price">$1.05M</span></div>
          <div class="cma-summary">
            <div class="cma-summary-title">Keystone Miami Benchmark</div>
            <div style="font-size:0.82rem; color:var(--text-secondary); margin-bottom:0.5rem;">Waterfront premium $650/sqft • Bay view +15%</div>
            <div class="cma-price-tiers">
              <div class="cma-tier"><div class="cma-tier-label">Below Market</div><div class="cma-tier-price">$985K</div></div>
              <div class="cma-tier"><div class="cma-tier-label">Target</div><div class="cma-tier-price">$1.08M</div></div>
              <div class="cma-tier"><div class="cma-tier-label">Ceiling</div><div class="cma-tier-price">$1.22M</div></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL 5: FSBO / EXPIREDS
    ═══════════════════════════════════════════════ -->
    <div id="panel-prospects" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">FSBO & Expired Listings</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">Owner contacts, property data, and call/door-knock tracking</p>
      </div>
      <div class="section-header">
        <span class="section-title">Active Prospect List</span>
        <span class="count-pill">6 Properties</span>
      </div>

      <div class="prospect-card">
        <div class="prospect-header">
          <div>
            <div class="prospect-name">Thomas & Angela Cruz</div>
            <div class="prospect-addr">3812 Stoneybrook Dr, Estero, FL 33928</div>
            <div class="prospect-tags">
              <span class="ptag ptag-fsbo">FSBO</span>
              <span class="ptag ptag-follow">Call Today</span>
            </div>
          </div>
          <div style="text-align:right; font-size:0.78rem; color:var(--text-secondary);">
            List Ask: $499K<br>Est. Value: $521K<br>Equity: ~78%
          </div>
        </div>
        <div class="prospect-actions">
          <button class="btn-action primary" onclick="logAction(this,'Called Cruz — attempt 2')">📞 Call</button>
          <button class="btn-action" onclick="logAction(this,'Door knock logged')">🚪 Door Knock</button>
          <button class="btn-action" onclick="logAction(this,'Added to CRM')">+ Add to CRM</button>
          <button class="btn-action" onclick="logAction(this,'Scheduled follow-up')">⏰ Schedule</button>
        </div>
      </div>

      <div class="prospect-card">
        <div class="prospect-header">
          <div>
            <div class="prospect-name">Linda Kaufman (Trust Owner)</div>
            <div class="prospect-addr">21450 Bella Terra Blvd, Estero, FL 33928</div>
            <div class="prospect-tags">
              <span class="ptag ptag-exp">Expired 47 Days</span>
              <span class="ptag ptag-follow">High Equity 83%</span>
            </div>
          </div>
          <div style="text-align:right; font-size:0.78rem; color:var(--text-secondary);">
            Prev List: $585K<br>Keystone: $849K<br>Absentee: OH
          </div>
        </div>
        <div class="prospect-actions">
          <button class="btn-action primary" onclick="logAction(this,'Called Kaufman Trust')">📞 Call</button>
          <button class="btn-action" onclick="logAction(this,'Mailer sent')">📬 Mailer</button>
          <button class="btn-action" onclick="logAction(this,'Added to CRM')">+ Add to CRM</button>
        </div>
      </div>

      <div class="prospect-card">
        <div class="prospect-header">
          <div>
            <div class="prospect-name">Robert & Mary Oguike</div>
            <div class="prospect-addr">9844 Portside Terrace, Estero, FL 33928</div>
            <div class="prospect-tags">
              <span class="ptag ptag-exp">Expired 22 Days</span>
              <span class="ptag ptag-follow">Follow-Up Fri</span>
            </div>
          </div>
          <div style="text-align:right; font-size:0.78rem; color:var(--text-secondary);">
            Prev List: $540K<br>Est. Value: $568K<br>DOM: 91
          </div>
        </div>
        <div class="prospect-actions">
          <button class="btn-action primary" onclick="logAction(this,'Called Oguike')">📞 Call</button>
          <button class="btn-action" onclick="logAction(this,'Added to CRM')">+ Add to CRM</button>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL: MEDIA & LISTING INTAKE QUEUE
    ═══════════════════════════════════════════════ -->
    <div id="panel-listings" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">Media & Listing Intake Queue</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">
          Gulf Pointe / {t.name} • Submit property media — Keystone & Quill enrich drafts awaiting your approval
        </p>
      </div>

      <div class="intake-grid">
        <div class="card intake-form-card">
          <div class="card-title">New Property Submission</div>
          <form id="listing-intake-form" onsubmit="submitListingIntake(event)">
            <div class="crm-field">
              <label class="crm-label">Title</label>
              <input class="crm-input" name="title" required placeholder="Gulf Pointe Lanai Estate">
            </div>
            <div class="crm-field">
              <label class="crm-label">Address</label>
              <input class="crm-input" name="address" required placeholder="101 Bella Terra Blvd, Estero, FL">
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.65rem;">
              <div class="crm-field">
                <label class="crm-label">Subdivision</label>
                <input class="crm-input" name="subdivision" placeholder="West Bay Club">
              </div>
              <div class="crm-field">
                <label class="crm-label">Price ($)</label>
                <input class="crm-input" name="price" type="number" required>
              </div>
            </div>
            <div class="crm-field">
              <label class="crm-label">Status</label>
              <select class="crm-input" name="status" required>
                <option value="FOR_SALE">FOR SALE</option>
                <option value="UNDER_CONTRACT">UNDER CONTRACT</option>
                <option value="RECORD_SOLD">RECORD SOLD</option>
              </select>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.65rem;">
              <div class="crm-field"><label class="crm-label">Beds</label><input class="crm-input" name="beds" type="number" value="4"></div>
              <div class="crm-field"><label class="crm-label">Baths</label><input class="crm-input" name="baths" value="3.5"></div>
              <div class="crm-field"><label class="crm-label">Sqft</label><input class="crm-input" name="sqft" type="number" required></div>
            </div>
            <div class="crm-field">
              <label class="crm-label">View / Waterfront</label>
              <input class="crm-input" name="view" placeholder="Fairway / Gulf access">
            </div>
            <div class="crm-field">
              <label class="crm-label">Photo URLs (one per line)</label>
              <textarea class="crm-textarea" name="photos" rows="3" required placeholder="https://..."></textarea>
            </div>
            <div class="crm-field">
              <label class="crm-label">Video URL (optional)</label>
              <input class="crm-input" name="video_url" placeholder="https://...">
            </div>
            <button type="submit" class="btn-approve" style="width:100%; margin-top:0.5rem;">Submit to Intake Queue</button>
          </form>
          <div id="intake-form-feedback" style="display:none; color:var(--success); font-size:0.82rem; margin-top:0.75rem; font-weight:600;"></div>
          <div class="intake-posture">
            🛡️ SOP §12: STAGED ONLY — MLS connected: NO • Published live: NO • Awaiting realtor approval
          </div>
        </div>

        <section>
          <div class="section-header">
            <span class="section-title">Awaiting Approval</span>
            <span class="count-pill" id="listing-queue-count">0 Pending</span>
          </div>
          <div id="listing-intake-queue">
            <!-- Queue cards injected by JS -->
          </div>
        </section>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL 6: COACHING PLAYBOOK
    ═══════════════════════════════════════════════ -->
    <div id="panel-playbook" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">Coaching & Objection Playbook</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">{coaching_label} • One organized vault for all call scripts and objection handlers</p>
      </div>
      <div class="playbook-grid">
        <div class="script-menu">
{playbook_menu_markup}
        </div>
        <div class="script-viewer" id="script-viewer">
          <!-- Default script loaded -->
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         PANEL 7: TRANSACTIONS
    ═══════════════════════════════════════════════ -->
    <div id="panel-transactions" class="os-panel">
      <div style="padding: 2rem 0 1rem 0;">
        <h1 style="font-size:1.8rem; font-weight:600; letter-spacing:-0.025em;">Transaction Deadlines</h1>
        <p style="color:var(--text-secondary); font-size:0.9rem; margin-top:0.3rem;">Florida As-Is Contract milestone tracking — never miss a contingency date</p>
      </div>

      <div class="txn-card">
        <div class="txn-header">
          <div>
            <div class="txn-address">21450 Bella Terra Blvd, Estero, FL</div>
            <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.2rem;">Buyer: C. & L. Dumont • Effective Date: Sep 5, 2026</div>
          </div>
          <div class="txn-price">$848,800</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-done">✓</div>
          <div class="milestone-name">Initial Deposit (EMD)</div>
          <div class="milestone-date">Sep 7, 2026</div>
          <div class="milestone-countdown cd-ok">Received</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-active">!</div>
          <div class="milestone-name">Inspection Period Ends</div>
          <div class="milestone-date">Sep 20, 2026</div>
          <div class="milestone-countdown cd-urgent">16 days left</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-active">!</div>
          <div class="milestone-name">Loan Application Submitted</div>
          <div class="milestone-date">Sep 12, 2026</div>
          <div class="milestone-countdown cd-urgent">8 days left</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-pending">○</div>
          <div class="milestone-name">Appraisal Ordered</div>
          <div class="milestone-date">Sep 25, 2026</div>
          <div class="milestone-countdown cd-ok">21 days</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-pending">○</div>
          <div class="milestone-name">Title Commitment & HOA Estoppel</div>
          <div class="milestone-date">Oct 10, 2026</div>
          <div class="milestone-countdown cd-ok">36 days</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-pending">○</div>
          <div class="milestone-name">Financing Contingency Waiver / Approval</div>
          <div class="milestone-date">Oct 5, 2026</div>
          <div class="milestone-countdown cd-ok">31 days</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-pending">○</div>
          <div class="milestone-name">Final Walkthrough</div>
          <div class="milestone-date">Oct 28, 2026</div>
          <div class="milestone-countdown cd-ok">54 days</div>
        </div>
        <div class="milestone-row">
          <div class="milestone-icon m-pending">🏆</div>
          <div class="milestone-name">Closing Day</div>
          <div class="milestone-date">Oct 29, 2026</div>
          <div class="milestone-countdown cd-ok">55 days</div>
        </div>
      </div>

      <div class="txn-card">
        <div class="txn-header">
          <div>
            <div class="txn-address">1646 Heritage Dr, Estero, FL</div>
            <div style="font-size:0.8rem; color:var(--text-secondary); margin-top:0.2rem;">Buyer: Peralta Properties LLC • Effective Date: Aug 28, 2026</div>
          </div>
          <div class="txn-price">$515,000</div>
        </div>
        <div class="milestone-row"><div class="milestone-icon m-done">✓</div><div class="milestone-name">Initial Deposit</div><div class="milestone-date">Aug 30</div><div class="milestone-countdown cd-ok">Received</div></div>
        <div class="milestone-row"><div class="milestone-icon m-done">✓</div><div class="milestone-name">Inspection Period</div><div class="milestone-date">Sep 12</div><div class="milestone-countdown cd-ok">Cleared</div></div>
        <div class="milestone-row"><div class="milestone-icon m-active">!</div><div class="milestone-name">Loan Approval</div><div class="milestone-date">Sep 28</div><div class="milestone-countdown cd-urgent">24 days</div></div>
        <div class="milestone-row"><div class="milestone-icon m-pending">○</div><div class="milestone-name">Closing Day</div><div class="milestone-date">Oct 15, 2026</div><div class="milestone-countdown cd-ok">41 days</div></div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════
         CRM CLIENT DOSSIER & CONVERSATION TRACKER MODAL
    ═══════════════════════════════════════════════ -->
    <div id="crm-modal" class="crm-modal-backdrop" onclick="if(event.target===this)closeCrmModal()">
      <div class="crm-modal-card">
        <div class="crm-modal-header">
          <div class="crm-header-profile">
            <div class="crm-header-avatar" id="crm-modal-avatar">MR</div>
            <div>
              <div class="crm-header-name">
                <span id="crm-modal-name">Maria Rodriguez</span>
                <span class="heat-badge heat-hot" id="crm-modal-badge">HOT BUYER</span>
              </div>
              <div class="crm-header-meta">
                <span id="crm-modal-phone">📞 (239) 555-0144</span>
                <span id="crm-modal-email">✉️ maria.rodriguez@privateclient.com</span>
                <span id="crm-modal-interest">📍 Estero • Bella Terra</span>
              </div>
            </div>
          </div>
          <button class="crm-close-btn" onclick="closeCrmModal()">✕</button>
        </div>

        <div class="crm-tabs">
          <button class="crm-tab active" onclick="switchCrmTab('thread', this)">✉️ Conversation & Email Thread</button>
          <button class="crm-tab" onclick="switchCrmTab('compose', this)">✍️ Compose Reply</button>
          <button class="crm-tab" onclick="switchCrmTab('notes', this)">📝 Private Notes & Next Follow-Up</button>
        </div>

        <div class="crm-body">
          <!-- TAB 1: THREAD TIMELINE -->
          <div id="crm-tab-thread" class="crm-tab-content active">
            <div id="crm-thread-list">
              <!-- Thread items injected dynamically -->
            </div>
          </div>

          <!-- TAB 2: COMPOSE REPLY -->
          <div id="crm-tab-compose" class="crm-tab-content">
            <div class="crm-field">
              <div class="crm-label">Quick AI Response Templates (Staged for Sign-Off)</div>
              <div class="template-chips">
                <span class="tmpl-chip" onclick="applyEmailTemplate('cma')">📐 Send Keystone CMA Summary</span>
                <span class="tmpl-chip" onclick="applyEmailTemplate('showing')">🏡 Tour & Walkthrough Invitation</span>
                <span class="tmpl-chip" onclick="applyEmailTemplate('preapproval')">📋 Request Pre-Approval Update</span>
                <span class="tmpl-chip" onclick="applyEmailTemplate('closing')">✍️ Contract & Escrow Milestone Check</span>
              </div>
            </div>
            <div class="crm-field">
              <label class="crm-label">Subject</label>
              <input type="text" class="crm-input" id="crm-reply-subject" placeholder="Subject...">
            </div>
            <div class="crm-field">
              <label class="crm-label">Message Body</label>
              <textarea class="crm-textarea" id="crm-reply-body" placeholder="Write response..."></textarea>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.75rem; flex-wrap:wrap; gap:0.5rem;">
              <div style="font-size:0.75rem; color:var(--text-secondary);">
                🛡️ <em>Human-in-the-Loop: Logged to client CRM timeline. Use External Mail Client to dispatch.</em>
              </div>
              <div style="display:flex; gap:0.5rem;">
                <button class="btn-sm" onclick="openMailtoClient()">External Mail Client ↗</button>
                <button class="btn-approve" style="padding:0.55rem 1.25rem;" onclick="sendCrmReply()">✓ Log to Timeline</button>
              </div>
            </div>
            <div id="crm-reply-feedback" style="display:none; color:var(--success); font-size:0.82rem; margin-top:0.75rem; font-weight:600;">
              ✓ Message logged to client conversation timeline and Copilot updated.
            </div>
          </div>

          <!-- TAB 3: NOTES & FOLLOW-UP -->
          <div id="crm-tab-notes" class="crm-tab-content">
            <div class="crm-field">
              <label class="crm-label">Next Scheduled Follow-Up</label>
              <div style="display:flex; gap:0.5rem; align-items:center;">
                <input type="date" class="crm-input" id="crm-next-date" style="max-width:200px;">
                <button class="btn-sm" onclick="setQuickDate(1)">Tomorrow</button>
                <button class="btn-sm" onclick="setQuickDate(3)">In 3 Days</button>
                <button class="btn-sm" onclick="setQuickDate(7)">Next Week</button>
              </div>
            </div>
            <div class="crm-field">
              <label class="crm-label">Private Agent Notes (Confidential)</label>
              <textarea class="crm-textarea" id="crm-notes-text" style="height:140px;" placeholder="Add private client intel (preferred showing times, family criteria, 1031 exchange deadlines)..."></textarea>
            </div>
            <button class="btn-approve" onclick="saveCrmNotes()">✓ Save Notes & Reminder</button>
            <div id="crm-notes-feedback" style="display:none; color:var(--success); font-size:0.82rem; margin-top:0.75rem; font-weight:600;">
              ✓ Client notes & follow-up schedule saved.
            </div>
          </div>
        </div>
      </div>
    </div>

  </div><!-- /os-shell -->

  <footer class="portal-footer">
    <div>© 2026 {t.company_name} • Sovereign Client Workspace</div>
    <div>Powered by Apex Luxury AI • Multi-Agent Fleet Active</div>
  </footer>

  <script>
    const ADVISOR_NAME = {json.dumps(t.name)};

    // ── PANEL SWITCHER ──
    function switchPanel(name, btn) {{
      document.querySelectorAll('.os-panel').forEach(p => p.classList.remove('active'));
      document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
      document.getElementById('panel-' + name).classList.add('active');
      if (btn) btn.classList.add('active');
      if (name === 'playbook') loadScript('{first_script_key}', document.querySelector('.script-item'));
    }}

    // ── PIPE SWITCHER ──
    function switchPipe(name, btn) {{
      document.querySelectorAll('.pipe-tab').forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('pipe-listing').style.display = name === 'listing' ? '' : 'none';
      document.getElementById('pipe-buyer').style.display = name === 'buyer' ? '' : 'none';
    }}

    // ── CARD APPROVALS ──
    function approveCard(id, msg) {{
      const card = document.getElementById(id);
      card.style.borderColor = 'var(--success)';
      card.style.background = 'rgba(52,211,153,0.05)';
      card.querySelector('.staged-actions').innerHTML =
        '<div style="color:var(--success);font-weight:600;font-size:0.82rem;display:flex;align-items:center;gap:0.4rem;">✓ ' + msg + '</div>';
      addMsg(msg + ' — logged to tenant ledger.', 'agent');
    }}

    // ── ACTION LOG ──
    function logAction(btn, msg) {{
      btn.innerText = '✓ ' + msg.split('—')[0].trim();
      btn.classList.add('primary');
      btn.disabled = true;
    }}

    // ── NET SHEET: SELLER ──
    function calcSeller() {{
      const price = parseFloat(document.getElementById('s-price').value) || 0;
      const commRate = parseFloat(document.getElementById('s-comm').value) || 5.5;
      const mort = parseFloat(document.getElementById('s-mort').value) || 0;
      const hoa = parseFloat(document.getElementById('s-hoa').value) || 0;

      if (!price) return;
      const comm = price * (commRate / 100);
      const docStamp = price * 0.007; // FL $0.70/$100
      const titleFees = 1050;
      const totalDeductions = comm + docStamp + titleFees + mort + hoa;
      const net = price - totalDeductions;

      document.getElementById('seller-results').innerHTML = `
        <div class="net-result-row"><span>Sale Price</span><span class="net-result-val">$${{fmt(price)}}</span></div>
        <div class="net-result-row"><span>Brokerage Commission (${{commRate}}%)</span><span class="net-result-val negative">-$${{fmt(comm)}}</span></div>
        <div class="net-result-row"><span>FL Doc Stamp Tax ($0.70/$100)</span><span class="net-result-val negative">-$${{fmt(docStamp)}}</span></div>
        <div class="net-result-row"><span>Title & Closing Agent Fees</span><span class="net-result-val negative">-$${{fmt(titleFees)}}</span></div>
        <div class="net-result-row"><span>Mortgage Payoff</span><span class="net-result-val negative">-$${{fmt(mort)}}</span></div>
        <div class="net-result-row"><span>HOA / Prorations</span><span class="net-result-val negative">-$${{fmt(hoa)}}</span></div>
        <div class="net-result-row total"><span>Estimated Net Wire to Seller</span><span class="net-result-val positive">$${{fmt(net)}}</span></div>
      `;
    }}

    // ── NET SHEET: BUYER ──
    function calcBuyer() {{
      const price = parseFloat(document.getElementById('b-price').value) || 0;
      const downPct = parseFloat(document.getElementById('b-down').value) || 20;
      const lender = parseFloat(document.getElementById('b-lender').value) || 3500;
      const annualTax = parseFloat(document.getElementById('b-tax').value) || 6240;

      if (!price) return;
      const downAmt = price * (downPct / 100);
      const loanAmt = price - downAmt;
      const titleBuyer = 850;
      const intlInsurance = price * 0.004; // homeowners est
      const escrowTax = (annualTax / 12) * 3; // 3-mo escrow cushion
      const escrowIns = intlInsurance / 4;
      const prepaidInt = loanAmt * 0.065 / 365 * 15; // 15 days prepaid
      const total = downAmt + lender + titleBuyer + escrowTax + escrowIns + prepaidInt;

      document.getElementById('buyer-results').innerHTML = `
        <div class="net-result-row"><span>Down Payment (${{downPct}}%)</span><span class="net-result-val">$${{fmt(downAmt)}}</span></div>
        <div class="net-result-row"><span>Lender Origination & Fees</span><span class="net-result-val">$${{fmt(lender)}}</span></div>
        <div class="net-result-row"><span>Title Insurance (Buyer's)</span><span class="net-result-val">$${{fmt(titleBuyer)}}</span></div>
        <div class="net-result-row"><span>Property Tax Escrow (3 mo)</span><span class="net-result-val">$${{fmt(escrowTax)}}</span></div>
        <div class="net-result-row"><span>Homeowners Ins. Escrow</span><span class="net-result-val">$${{fmt(escrowIns)}}</span></div>
        <div class="net-result-row"><span>Prepaid Interest (15 days)</span><span class="net-result-val">$${{fmt(prepaidInt)}}</span></div>
        <div class="net-result-row total"><span>Total Cash Required at Closing</span><span class="net-result-val positive">$${{fmt(total)}}</span></div>
      `;
    }}

    function fmt(n) {{ return Math.round(n).toLocaleString(); }}

    // ── PLAYBOOK SCRIPTS ──
    const scripts = {playbook_json_str};

    function loadScript(key, btn) {{
      const s = scripts[key];
      if (!s) return;
      document.querySelectorAll('.script-item').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      document.getElementById('script-viewer').innerHTML = `
        <div class="script-title">${{s.title}}</div>
        <div class="script-category">${{s.cat}}</div>
        ${{s.html}}
      `;
    }}

    // ── COPILOT ──
    function quickMsg(txt) {{
      document.getElementById('chat-input').value = txt;
      sendMsg(new Event('submit'));
    }}
    function sendMsg(e) {{
      e.preventDefault();
      const inp = document.getElementById('chat-input');
      const val = inp.value.trim();
      if (!val) return;
      addMsg(val, 'user');
      inp.value = '';
      setTimeout(() => {{
        const q = val.toLowerCase();
        let reply;
        if (q.includes('gci') || q.includes('pipeline')) reply = "Current pipeline value: <strong>$14.2M</strong>. At 2% average net commission: projected GCI = <strong>$284,000</strong>. Top opportunity: Walsh listing at $1.89M = ~$52K GCI.";
        else if (q.includes('sms') || q.includes('maria')) reply = '<em>Draft SMS — Maria Rodriguez:</em><br>"Hi Maria! This is ' + ADVISOR_NAME + '. Just wanted to follow up on our Bella Terra conversation — I have 2 new listings that just hit the market today that match exactly what you are looking for. Can we chat this afternoon?"';
        else if (q.includes('cma') || q.includes('sqft')) reply = "Keystone benchmark: Bella Terra at <strong>$310/sqft</strong> + $80K adjustments = <strong>$848,800</strong> recommended list. Zillow Zestimate delta: +$286,400 in seller favor.";
        else if (q.includes('today') || q.includes('queue')) reply = "Today's priority actions:<br>1. 🔴 Call Maria Rodriguez (Buyer — 3 days cold)<br>2. 🔴 Call Walsh couple (Seller — CMA delivered, no reply)<br>3. 🟡 Approve Keystone CMA in queue<br>4. 🟡 Follow up Jennifer Liu<br>5. 🟢 Annual check-in Beth & Paul Nguyen";
        else reply = "Understood. Logged directive to the Apex fleet. All actions stage in your queue for final sign-off — nothing leaves without your approval.";
        addMsg(reply, 'agent');
      }}, 380);
    }}
    function addMsg(html, role) {{
      const feed = document.getElementById('chat-feed');
      const el = document.createElement('div');
      el.className = 'msg-bubble msg-' + role;
      el.innerHTML = html;
      feed.appendChild(el);
      feed.scrollTop = feed.scrollHeight;
    }}

    // ── LEAD FLOW INTEGRATION ──
    const LEADS_KEY = 'apex_leads_{t.subdomain_slug}';

    function loadInboundLeads() {{
      try {{
        const raw = localStorage.getItem(LEADS_KEY);
        if (!raw) return;
        const leads = JSON.parse(raw);
        if (!Array.isArray(leads) || leads.length === 0) return;

        const queueContainer = document.getElementById('contact-rows-container');
        const countPill = document.getElementById('action-queue-count');
        const buyerNewLeadCol = document.getElementById('buyer-col-new-lead');
        const chatFeed = document.getElementById('chat-feed');

        // Clear existing dynamic rows/cards before re-rendering
        document.querySelectorAll('.dynamic-inbound-row').forEach(el => el.remove());
        document.querySelectorAll('.dynamic-inbound-card').forEach(el => el.remove());

        if (countPill) {{
          countPill.innerText = (5 + leads.length) + ' Pending';
        }}

        // Render each lead into Action Queue & Buyer Pipeline
        leads.forEach(lead => {{
          const initials = (lead.full_name || 'IN').split(' ').map(n => n[0]).join('').toUpperCase() || 'IN';

          // 1. Action Queue row in Dashboard
          if (queueContainer) {{
            const row = document.createElement('div');
            row.className = 'contact-row dynamic-inbound-row';
            row.style.borderLeft = '3px solid var(--gold-accent)';
            row.style.background = 'rgba(229,200,144,0.05)';
            row.innerHTML = `
              <div class="contact-avatar av-hot" style="border: 1.5px solid var(--gold-accent);">${{initials}}</div>
              <div class="contact-info">
                <div class="contact-name">${{lead.full_name}} <span class="heat-badge heat-hot" style="background:rgba(229,200,144,0.25);color:var(--gold-accent);border:1px solid var(--gold-accent);">✨ FRONT-DOOR DOSSIER</span></div>
                <div class="contact-meta">Buyer Inquiry • Target: ${{lead.property_interest}} • Est: ${{lead.valuation_target}} • Received: ${{lead.timestamp}}</div>
              </div>
              <div class="contact-actions">
                <a href="tel:${{(lead.contact || '').replace(/[^0-9]/g, '')}}" class="btn-action primary" style="text-decoration:none;" onclick="logAction(this,'Called ${{lead.full_name}}')">📞 Call</a>
                <a href="sms:${{(lead.contact || '').replace(/[^0-9]/g, '')}}" class="btn-action" style="text-decoration:none;" onclick="logAction(this,'SMS Sent')">✉ Text</a>
              </div>
            `;
            queueContainer.insertBefore(row, queueContainer.firstChild);
          }}

          // 2. Deal card in Buyer Pipeline Kanban (New Lead column)
          if (buyerNewLeadCol) {{
            const card = document.createElement('div');
            card.className = 'deal-card dynamic-inbound-card';
            card.style.borderColor = 'var(--gold-accent)';
            card.style.boxShadow = '0 0 14px rgba(229,200,144,0.2)';
            card.innerHTML = `
              <div class="deal-name">${{lead.full_name}} <span style="font-size:0.6rem;background:var(--gold-dim);color:var(--gold-accent);padding:1px 5px;border-radius:6px;">ONLINE</span></div>
              <div class="deal-addr">${{lead.property_interest}}</div>
              <div class="deal-val">${{lead.valuation_target}}</div>
              <div class="deal-days" style="color:var(--success);">Just In (${{lead.timestamp}}) • ${{lead.contact}}</div>
            `;
            const addBtn = buyerNewLeadCol.querySelector('.kanban-add');
            if (addBtn) {{
              buyerNewLeadCol.insertBefore(card, addBtn);
            }} else {{
              buyerNewLeadCol.appendChild(card);
            }}
          }}
        }});

        // If leads exist, inject a live notification into Copilot chat feed if not already present
        if (chatFeed && !document.getElementById('copilot-inbound-alert')) {{
          const alertBubble = document.createElement('div');
          alertBubble.id = 'copilot-inbound-alert';
          alertBubble.className = 'msg-bubble msg-agent';
          alertBubble.style.borderColor = 'var(--gold-accent)';
          alertBubble.innerHTML = `✨ <strong>Inbound Dossier Alert:</strong> Received ${{leads.length}} principal inquiry from your Front Door. Staged directly into your <strong>Who Needs Contact Today</strong> queue and <strong>Buyer Pipeline</strong>.`;
          chatFeed.appendChild(alertBubble);
        }}
      }} catch (err) {{
        console.warn('Error loading inbound leads:', err);
      }}
    }}

    function addTestLead() {{
      const sampleNames = ['Dr. Aris Thorne', 'Elena Rostova', 'Harrison & Claire Vance', 'Marcus Sterling'];
      const sampleAddrs = ['Pelican Bay Penthouse', 'West Bay Club Fairway Villa', 'Bella Terra Executive Pool Home', 'Barefoot Beachfront Estate'];
      const sampleVals = ['$1,450,000', '$2,100,000', '$848,800', '$3,750,000'];
      const idx = Math.floor(Math.random() * sampleNames.length);

      const lead = {{
        id: 'lead_' + Date.now(),
        full_name: sampleNames[idx],
        contact: '(239) 555-' + Math.floor(1000 + Math.random() * 9000),
        property_interest: sampleAddrs[idx],
        valuation_target: sampleVals[idx],
        tenant: '{t.subdomain_slug}',
        timestamp: new Date().toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}}),
        date: new Date().toISOString(),
        heat: 'HOT'
      }};

      const existing = JSON.parse(localStorage.getItem(LEADS_KEY) || '[]');
      existing.unshift(lead);
      localStorage.setItem(LEADS_KEY, JSON.stringify(existing));
      loadInboundLeads();
    }}

    window.addEventListener('storage', (e) => {{
      if (e.key === LEADS_KEY) loadInboundLeads();
    }});
    setInterval(loadInboundLeads, 3000);

    // ── CRM CLIENT DOSSIERS & EMAIL CONVERSATION TRACKER ──
    const CRM_KEY = 'apex_crm_threads_{t.subdomain_slug}';
    let currentActiveClientId = null;

    const defaultClients = {{
      maria_rodriguez: {{
        id: 'maria_rodriguez',
        name: 'Maria Rodriguez',
        initials: 'MR',
        badge: 'HOT BUYER',
        heat: 'HOT',
        category: 'BUYER',
        phone: '(239) 555-0144',
        email: 'maria.rodriguez@privateclient.com',
        interest: 'Estero • Bella Terra (Budget $680K)',
        nextFollowUp: '2026-09-05',
        notes: 'Pre-approved with CrossCountry Mortgage ($680K). Looking for single-story pool home in Estero or Bonita Springs. Kids attend Pinewoods Elementary. Likes open-concept kitchens.',
        threads: [
          {{
            sender: 'client',
            type: 'received',
            subject: 'Re: Bella Terra showings this weekend',
            time: 'Yesterday 4:15 PM',
            body: "Hi {t.name}! We're really excited to see 21450 Bella Terra Blvd. We have our CrossCountry pre-approval letter for $680k in hand. Does Saturday morning at 11 AM work for you?"
          }},
          {{
            sender: 'agent',
            type: 'sent',
            subject: 'Bella Terra Walkthrough Confirmation & Keystone CMA',
            time: 'Yesterday 5:20 PM',
            body: "Hi Maria! I've booked our private walkthrough for Saturday at 11 AM. Attached is our Keystone comparative market breakdown showing the permitted 2023 roof and pool value spread. Looking forward to showing you the property!"
          }}
        ]
      }},
      walsh_couple: {{
        id: 'walsh_couple',
        name: 'David & Karen Walsh',
        initials: 'DW',
        badge: 'HOT SELLER',
        heat: 'HOT',
        category: 'SELLER',
        phone: '(239) 555-0189',
        email: 'dkwalsh@westbayfamily.com',
        interest: '22001 West Bay Blvd ($1.89M Listing)',
        nextFollowUp: '2026-09-04',
        notes: 'High-equity sellers. Concerned about FL doc stamps ($0.70/$100) and capital gains. Emphasize off-market discretion and private buyer pool.',
        threads: [
          {{
            sender: 'agent',
            type: 'sent',
            subject: 'Keystone Valuation Dossier — 22001 West Bay Blvd ($1.89M)',
            time: 'Yesterday 11:30 AM',
            body: "David & Karen, here is our full pricing analysis comparing your property with recent West Bay Club off-market comps. Net proceeds sheet reflects Florida $0.70/$100 doc stamp tax."
          }}
        ]
      }},
      jennifer_liu: {{
        id: 'jennifer_liu',
        name: 'Jennifer Liu',
        initials: 'JL',
        badge: 'WARM BUYER',
        heat: 'WARM',
        category: 'BUYER',
        phone: '(312) 555-0177',
        email: 'jliu@chicagolaw.com',
        interest: 'Relocating from Chicago • Budget $650K',
        nextFollowUp: '2026-09-04',
        notes: 'Referral from Marcus Sterling. Moving to SWFL in November. Wants private golf community with quick access to RSW airport.',
        threads: [
          {{
            sender: 'client',
            type: 'received',
            subject: 'Relocation from Chicago to SW Florida',
            time: 'Aug 31, 2026',
            body: "Hi {t.name}, our friend Marcus Sterling recommended we reach out. We're looking for a gated community near golf in Southwest FL."
          }},
          {{
            sender: 'agent',
            type: 'sent',
            subject: 'Welcome to Southwest Florida! Private Community Dossiers',
            time: 'Aug 31, 2026',
            body: "Excited to connect, Jennifer. Sending over our private neighborhood dossiers for Estero & Bonita Springs tailored to golf and airport access."
          }}
        ]
      }},
      thomas_cruz: {{
        id: 'thomas_cruz',
        name: 'Thomas Cruz',
        initials: 'TC',
        badge: 'FSBO PROSPECT',
        heat: 'WARM',
        category: 'FSBO',
        phone: '(239) 555-0133',
        email: 'cruz.thomas@gmail.com',
        interest: '3812 Stoneybrook Dr (~$525K)',
        nextFollowUp: '2026-09-06',
        notes: 'FSBO seller. Highly sensitive to commission. Goal: 15-minute CMA appointment. Shared data on 90-day sold comps.',
        threads: [
          {{
            sender: 'agent',
            type: 'sent',
            subject: 'Market Data & Recent Sold Comps for Stoneybrook',
            time: 'Sep 1, 2026',
            body: "Thomas, as promised on our call, here is the sold comp sheet for your neighborhood showing actual appraisal values over the last 90 days."
          }}
        ]
      }},
      nguyen_family: {{
        id: 'nguyen_family',
        name: 'Beth & Paul Nguyen',
        initials: 'BP',
        badge: 'SPHERE CLIENT',
        heat: 'COLD',
        category: 'SPHERE',
        phone: '(239) 555-0199',
        email: 'pnguyen@leecountyhealth.org',
        interest: 'Past Client (Closed 2022) • Annual Equity Review',
        nextFollowUp: '2026-09-15',
        notes: 'Past buyers 2022. Great advocates for referrals in Pelican Sound.',
        threads: [
          {{
            sender: 'agent',
            type: 'sent',
            subject: 'Happy 3-Year Home Anniversary! 🏡',
            time: 'Aug 29, 2026',
            body: "Beth & Paul, happy 3-year home anniversary! Values in your section of Estero are up ~14% since your closing. Would love to send a quick equity snapshot."
          }}
        ]
      }}
    }};

    function getCrmData() {{
      try {{
        const raw = localStorage.getItem(CRM_KEY);
        if (!raw) return defaultClients;
        const parsed = JSON.parse(raw);
        return Object.assign({{}}, defaultClients, parsed);
      }} catch (e) {{
        return defaultClients;
      }}
    }}

    function saveCrmData(data) {{
      try {{
        localStorage.setItem(CRM_KEY, JSON.stringify(data));
      }} catch (e) {{
        console.warn('Error saving CRM data:', e);
      }}
    }}

    function getActiveClient(id) {{
      const allCrm = getCrmData();
      if (allCrm[id]) return allCrm[id];

      // Check dynamic front-door leads
      try {{
        const rawLeads = localStorage.getItem(LEADS_KEY);
        if (rawLeads) {{
          const leads = JSON.parse(rawLeads);
          const found = leads.find(l => l.id === id);
          if (found) {{
            const initials = (found.full_name || 'IN').split(' ').map(n => n[0]).join('').toUpperCase() || 'IN';
            return {{
              id: found.id,
              name: found.full_name,
              initials: initials,
              badge: '✨ NEW DOSSIER',
              heat: 'HOT',
              category: 'BUYER',
              phone: found.contact,
              email: (found.contact && found.contact.includes('@')) ? found.contact : found.contact + '@client.phone',
              interest: found.property_interest + ' (Target: ' + found.valuation_target + ')',
              nextFollowUp: new Date(Date.now() + 86400000).toISOString().split('T')[0],
              notes: 'Inbound brief from Front-Door Dossier Form. Target valuation: ' + found.valuation_target + '. Received: ' + found.timestamp,
              threads: [
                {{
                  sender: 'client',
                  type: 'system',
                  subject: 'Confidential Front-Door Dossier Intake',
                  time: found.timestamp || 'Just Now',
                  body: 'Target Property / Address: ' + found.property_interest + '\\nTarget Valuation: ' + found.valuation_target + '\\nClient Contact: ' + found.contact + '\\nDispatched via Apex Front-Door Form'
                }}
              ]
            }};
          }}
        }}
      }} catch (err) {{
        console.warn('Error reading dynamic lead for CRM:', err);
      }}

      return defaultClients.maria_rodriguez;
    }}

    function openClientDossier(clientId) {{
      currentActiveClientId = clientId;
      const client = getActiveClient(clientId);
      if (!client) return;

      document.getElementById('crm-modal-avatar').innerText = client.initials || 'CL';
      document.getElementById('crm-modal-name').innerText = client.name;
      document.getElementById('crm-modal-badge').innerText = client.badge || 'CLIENT';
      document.getElementById('crm-modal-phone').innerText = '📞 ' + (client.phone || 'No phone');
      document.getElementById('crm-modal-email').innerText = '✉️ ' + (client.email || 'No email');
      document.getElementById('crm-modal-interest').innerText = '📍 ' + (client.interest || 'Southwest Florida');

      // Thread render
      renderClientThread(client);

      // Notes & Followup
      document.getElementById('crm-notes-text').value = client.notes || '';
      document.getElementById('crm-next-date').value = client.nextFollowUp || '';

      // Reset feedback
      document.getElementById('crm-reply-feedback').style.display = 'none';
      document.getElementById('crm-notes-feedback').style.display = 'none';

      // Default to thread tab
      switchCrmTab('thread');

      document.getElementById('crm-modal').classList.add('open');
    }}

    function closeCrmModal() {{
      document.getElementById('crm-modal').classList.remove('open');
      currentActiveClientId = null;
    }}

    function switchCrmTab(tabName, btn) {{
      document.querySelectorAll('.crm-tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.crm-tab-content').forEach(c => c.classList.remove('active'));
      document.getElementById('crm-tab-' + tabName).classList.add('active');
      if (btn) btn.classList.add('active');
      else {{
        const targetBtn = Array.from(document.querySelectorAll('.crm-tab')).find(b => b.getAttribute('onclick') && b.getAttribute('onclick').includes(tabName));
        if (targetBtn) targetBtn.classList.add('active');
      }}
    }}

    function renderClientThread(client) {{
      const list = document.getElementById('crm-thread-list');
      if (!client.threads || client.threads.length === 0) {{
        list.innerHTML = '<div style="color:var(--text-secondary);font-size:0.85rem;padding:1.5rem;text-align:center;">No previous messages logged yet. Use Compose Reply to start the thread.</div>';
        return;
      }}
      list.innerHTML = client.threads.map(m => `
        <div class="thread-msg ${{m.type}}">
          <div class="thread-header">
            <span class="thread-sender ${{m.type}}">${{m.sender === 'agent' ? ADVISOR_NAME + ' (Advisor)' : (m.sender === 'client' ? client.name : 'System Intake')}}</span>
            <span class="thread-time">${{m.time}}</span>
          </div>
          <div class="thread-subject">${{m.subject}}</div>
          <div class="thread-body">${{m.body}}</div>
        </div>
      `).join('');
    }}

    function applyEmailTemplate(type) {{
      const client = getActiveClient(currentActiveClientId);
      const firstName = (client.name || 'Client').split(' ')[0];
      const subjectInput = document.getElementById('crm-reply-subject');
      const bodyInput = document.getElementById('crm-reply-body');

      if (type === 'cma') {{
        subjectInput.value = 'Keystone CMA Valuation Analysis — ' + (client.interest || 'Your Property');
        bodyInput.value = 'Hi ' + firstName + ',\\n\\nI have prepared our Keystone Comparative Market Analysis for ' + (client.interest || 'your property') + '. Our pricing model indicates significant equity spread compared to automated estimates.\\n\\nWould you have 15 minutes tomorrow afternoon to review the net sheet together?\\n\\nBest regards,\\n' + ADVISOR_NAME;
      }} else if (type === 'showing') {{
        subjectInput.value = 'VIP Showing Confirmation — ' + (client.interest || 'Private Tour');
        bodyInput.value = 'Hi ' + firstName + ',\\n\\nI have scheduled our private showing for ' + (client.interest || 'the property') + '. I will meet you at the community gate with the full dossier and gate credentials.\\n\\nLooking forward to seeing you then!\\n\\nWarm regards,\\n' + ADVISOR_NAME;
      }} else if (type === 'preapproval') {{
        subjectInput.value = 'Financing & Pre-Approval Milestone Check-in';
        bodyInput.value = 'Hi ' + firstName + ',\\n\\nTo ensure our offer position remains dominant in today’s Southwest Florida market, our transaction team is ready to align your financing credentials with the listing agent prior to contract submission.\\n\\nPlease let me know if you would like me to connect directly with your lender.\\n\\nSincerely,\\n' + ADVISOR_NAME;
      }} else if (type === 'closing') {{
        subjectInput.value = 'Florida As-Is Contract Milestone Update';
        bodyInput.value = 'Hi ' + firstName + ',\\n\\nHere is your latest Florida contract milestone update for ' + (client.interest || 'your transaction') + '. Earnest money deposit is logged with title, and inspection period preparations are underway.\\n\\nFeel free to call my direct line if you have any questions!\\n\\nBest regards,\\n' + ADVISOR_NAME;
      }}
    }}

    function sendCrmReply() {{
      const subject = document.getElementById('crm-reply-subject').value.trim();
      const body = document.getElementById('crm-reply-body').value.trim();
      if (!subject || !body) {{
        alert('Please provide both a subject and message body.');
        return;
      }}
      const allCrm = getCrmData();
      const client = getActiveClient(currentActiveClientId);
      if (!client) return;

      const newMsg = {{
        sender: 'agent',
        type: 'sent',
        subject: subject,
        time: 'Today ' + new Date().toLocaleTimeString([], {{hour: '2-digit', minute:'2-digit'}}),
        body: body
      }};

      if (!client.threads) client.threads = [];
      client.threads.push(newMsg);
      allCrm[client.id] = client;
      saveCrmData(allCrm);

      renderClientThread(client);

      document.getElementById('crm-reply-subject').value = '';
      document.getElementById('crm-reply-body').value = '';
      document.getElementById('crm-reply-feedback').style.display = 'block';

      addMsg('Logged outbound email to <strong>' + client.name + '</strong> (' + subject + '). Thread updated in CRM.', 'agent');

      setTimeout(() => {{
        switchCrmTab('thread');
      }}, 1200);
    }}

    function openMailtoClient() {{
      const client = getActiveClient(currentActiveClientId);
      const subject = document.getElementById('crm-reply-subject').value.trim();
      const body = document.getElementById('crm-reply-body').value.trim();
      const email = (client.email && client.email.includes('@')) ? client.email : 'client@private.domain';
      window.open('mailto:' + encodeURIComponent(email) + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body));
    }}

    function setQuickDate(days) {{
      const d = new Date(Date.now() + days * 86400000);
      document.getElementById('crm-next-date').value = d.toISOString().split('T')[0];
    }}

    function saveCrmNotes() {{
      const allCrm = getCrmData();
      const client = getActiveClient(currentActiveClientId);
      if (!client) return;

      client.notes = document.getElementById('crm-notes-text').value.trim();
      client.nextFollowUp = document.getElementById('crm-next-date').value;
      allCrm[client.id] = client;
      saveCrmData(allCrm);

      document.getElementById('crm-notes-feedback').style.display = 'block';
      setTimeout(() => {{
        document.getElementById('crm-notes-feedback').style.display = 'none';
      }}, 2500);
    }}

    function filterCrmQueue(cat, btn) {{
      document.querySelectorAll('.crm-filter-chip').forEach(c => c.classList.remove('active'));
      if (btn) btn.classList.add('active');

      const rows = document.querySelectorAll('#contact-rows-container .contact-row');
      rows.forEach(r => {{
        const rCat = (r.getAttribute('data-category') || '').toUpperCase();
        const rHeat = (r.getAttribute('data-heat') || '').toUpperCase();

        if (cat === 'ALL') {{
          r.style.display = 'flex';
        }} else if (cat === 'HOT') {{
          r.style.display = rHeat === 'HOT' ? 'flex' : 'none';
        }} else if (cat === 'FSBO') {{
          r.style.display = (rCat === 'FSBO' || rCat === 'EXPIRED') ? 'flex' : 'none';
        }} else {{
          r.style.display = rCat === cat ? 'flex' : 'none';
        }}
      }});
    }}

    // ── LISTING INTAKE QUEUE ──
    const LISTING_INTAKE_API = 'http://127.0.0.1:8765';
    const TENANT_SLUG = {json.dumps(t.subdomain_slug)};
    let listingIntakeQueue = {intake_queue_json};

    function formatListingPrice(n) {{
      if (!n) return '—';
      return '$' + Number(n).toLocaleString();
    }}

    function renderListingIntakeQueue() {{
      const container = document.getElementById('listing-intake-queue');
      const countEl = document.getElementById('listing-queue-count');
      const pending = listingIntakeQueue.filter(e => e.queue_status === 'PENDING_APPROVAL');
      if (countEl) countEl.textContent = pending.length + ' Pending';

      if (!container) return;
      if (!pending.length) {{
        container.innerHTML = '<div class="card" style="color:var(--text-secondary); font-size:0.85rem;">No staged submissions yet. Use the form to submit property media.</div>';
        return;
      }}

      container.innerHTML = pending.map(entry => {{
        const listing = entry.listing || {{}};
        const keystone = entry.keystone || (entry.enrichment && entry.enrichment.keystone) || {{}};
        const narrative = (entry.enrichment && entry.enrichment.quill_narrative) || '';
        const ppsf = keystone.price_per_sqft_display || 'N/A';
        const spread = (keystone.comp_spread && keystone.comp_spread.display) || 'Pending';
        const photos = listing.photos || [];
        const thumb = photos[0] ? '<img src="' + photos[0] + '" alt="" style="width:72px;height:54px;object-fit:cover;border-radius:8px;margin-right:0.75rem;">' : '';
        return '<div class="listing-queue-card" id="lq-' + entry.listing_id + '">' +
          '<div class="lq-header">' +
            '<div style="display:flex;align-items:flex-start;">' + thumb +
              '<div><div class="lq-title">' + (listing.title || entry.listing_id) + '</div>' +
              '<div class="lq-meta">' + (listing.address || '') + ' • ' + (listing.subdivision || '') + '</div>' +
              '<div class="lq-meta">' + formatListingPrice(listing.price) + ' • ' + (listing.status || '') + '</div>' +
            '</div></div>' +
          '</div>' +
          '<div class="lq-keystone">📐 Keystone: ' + ppsf + ' • Comp corridor ±5%: ' + spread + '</div>' +
          '<div class="lq-narrative">✍️ Quill: ' + (narrative.substring(0, 220) + (narrative.length > 220 ? '…' : '')) + '</div>' +
          '<div class="lq-actions">' +
            '<button class="btn-approve" onclick="approveListingForShowcase(\\'' + entry.listing_id + '\\')">✓ Approve for Showcase</button>' +
            '<span style="font-size:0.72rem;color:var(--text-secondary);align-self:center;">STAGED — not live MLS</span>' +
          '</div></div>';
      }}).join('');
    }}

    async function refreshListingIntakeQueue() {{
      try {{
        const res = await fetch(LISTING_INTAKE_API + '/api/listing/queue?tenant=' + encodeURIComponent(TENANT_SLUG));
        if (!res.ok) throw new Error('Queue fetch failed');
        const data = await res.json();
        listingIntakeQueue = data.queue || [];
      }} catch (e) {{
        // Fall back to embedded queue when intake server offline
      }}
      renderListingIntakeQueue();
    }}

    async function submitListingIntake(ev) {{
      ev.preventDefault();
      const form = ev.target;
      const fd = new FormData(form);
      const photos = (fd.get('photos') || '').split('\\n').map(s => s.trim()).filter(Boolean);
      const payload = {{
        title: fd.get('title'), address: fd.get('address'), subdivision: fd.get('subdivision'),
        price: parseFloat(fd.get('price')), status: fd.get('status'),
        specs: {{
          beds: parseInt(fd.get('beds') || '4', 10), baths: fd.get('baths'),
          sqft: parseInt(fd.get('sqft'), 10), pool: true, view: fd.get('view')
        }},
        photos, video_url: fd.get('video_url') || null, tenant_slug: TENANT_SLUG
      }};
      const feedback = document.getElementById('intake-form-feedback');
      try {{
        const res = await fetch(LISTING_INTAKE_API + '/api/listing/submit', {{
          method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify(payload)
        }});
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Submit failed');
        feedback.style.display = 'block';
        feedback.style.color = 'var(--success)';
        feedback.textContent = '✓ Queued ' + data.listing_id + ' — Keystone & Quill drafts staged.';
        form.reset();
        await refreshListingIntakeQueue();
      }} catch (err) {{
        feedback.style.display = 'block';
        feedback.style.color = 'var(--danger)';
        feedback.textContent = '⚠ ' + err.message + ' — start intake server: python apex_core/listing_intake_server.py';
      }}
    }}

    async function approveListingForShowcase(listingId) {{
      const card = document.getElementById('lq-' + listingId);
      const btn = card ? card.querySelector('.btn-approve') : null;
      if (btn) {{ btn.disabled = true; btn.textContent = 'Approving…'; }}
      try {{
        const res = await fetch(LISTING_INTAKE_API + '/api/listing/approve', {{
          method: 'POST', headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ listing_id: listingId }})
        }});
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Approve failed');
        if (card) {{
          card.style.borderColor = 'var(--success)';
          card.querySelector('.lq-actions').innerHTML =
            '<div style="color:var(--success);font-weight:600;font-size:0.82rem;">✓ Approved for Apple showcase — rebuild front door to reflect.</div>';
        }}
        listingIntakeQueue = listingIntakeQueue.filter(e => e.listing_id !== listingId);
        renderListingIntakeQueue();
        addMsg('Listing <strong>' + listingId + '</strong> approved for kinetic showcase (STAGED — not live MLS).', 'agent');
      }} catch (err) {{
        if (btn) {{ btn.disabled = false; btn.textContent = '✓ Approve for Showcase'; }}
        alert('Approve failed: ' + err.message);
      }}
    }}

    // ── INIT ──
    loadScript('{first_script_key}', null);
    loadInboundLeads();
    renderListingIntakeQueue();
  </script>
</body>
</html>"""


fast_builder = FastSiteBuilder()

if __name__ == "__main__":
    for t in tenant_manager.list_tenants():
        fast_builder.build_site(t)
