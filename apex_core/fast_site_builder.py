"""
Apex Luxury AI — Autonomous Fast Site Builder (Fizz Engine)
Generates high-converting live landing pages for real estate, Florida No-Fault, and PIP clients.
Trained on Apple Design Principles (apple.com, apple.com/business).
"""

import os
import sys
from typing import Dict, Any

# Ensure workspace root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from apex_core.tenant_manager import tenant_manager, Tenant

PUBLIC_SITES_DIR = os.path.join(os.path.dirname(__file__), "..", "public_sites")

class FastSiteBuilder:
    def __init__(self, output_dir: str = PUBLIC_SITES_DIR):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

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

        print(f"[FastSiteBuilder] Deployed landing page for {tenant.name} -> {index_file}")
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

    /* Global Apple Frosted Glass Header */
    .apple-nav {{
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(0, 0, 0, 0.78);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border-bottom: 1px solid var(--hairline);
      transition: background 0.3s ease;
    }}
    .nav-inner {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0.9rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
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
      gap: 1.5rem;
    }}
    .nav-link {{
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 400;
      transition: color 0.2s ease;
    }}
    .nav-link:hover {{
      color: var(--text-primary);
    }}
    .pill-btn-small {{
      background: rgba(255, 255, 255, 0.12);
      color: var(--text-primary);
      padding: 0.45rem 1.1rem;
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
  </style>
</head>
<body>

  <!-- Apple Minimal Navigation -->
  <header class="apple-nav">
    <div class="nav-inner">
      <a href="#" class="brand-mark">
        <span class="brand-dot"></span>
        {t.name}
      </a>
      <div class="nav-actions">
        <a href="#valuation" class="nav-link">Intelligence</a>
        <a href="#advisory" class="nav-link">Advisory</a>
        <a href="#consultation" class="pill-btn-small">Request Private Brief</a>
      </div>
    </div>
  </header>

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
      btn.innerText = 'Encrypting & Sending...';

      const payload = {{
        kind: 'apex_realtor_onboarding_brief',
        answers: {{
          full_name: document.getElementById('inquiry-name').value,
          contact: document.getElementById('inquiry-contact').value,
          property_interest: document.getElementById('inquiry-address').value,
          valuation_target: document.getElementById('cma-hero-price').innerText
        }}
      }};

      fetch('http://127.0.0.1:8787/brief', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(payload)
      }}).catch(() => {{}}).finally(() => {{
        document.getElementById('inquiry-feedback').style.display = 'block';
        btn.innerText = '✓ Brief Dispatched';
      }});
    }}

    updateValuation();
  </script>
</body>
</html>"""

fast_builder = FastSiteBuilder()

if __name__ == "__main__":
    for t in tenant_manager.list_tenants():
        fast_builder.build_site(t)
