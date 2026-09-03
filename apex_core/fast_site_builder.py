"""
Apex Luxury AI — Autonomous Fast Site Builder (Fizz Engine)
Generates high-converting live landing pages for real estate, Florida No-Fault, and PIP clients.
"""

import os
from typing import Dict, Any
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
        return f"<!-- Luxury Realty template for {t.name} -->"

fast_builder = FastSiteBuilder()

if __name__ == "__main__":
    for t in tenant_manager.list_tenants():
        fast_builder.build_site(t)
