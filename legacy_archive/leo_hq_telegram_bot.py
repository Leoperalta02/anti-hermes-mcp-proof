import asyncio
import datetime
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from escalation_engine import check_for_escalation

TELEGRAM_BOT_TOKEN = "8619488658:AAGE-cLUsVapoBJVhw68gGQZb0WF4FOpJCQ"
HERMES_EXE = r"C:\LEO-LAB-ANTIGRAVITY\hermes-agent\bin\hermes.exe"
HERMES_ROOT = r"C:\LEO-LAB-ANTIGRAVITY\hermes-state"
PROFILE_NAME = "anti-cos"
PROFILE_DIR = os.path.join(HERMES_ROOT, "profiles", PROFILE_NAME)

SURFACE_NAME = "Alienware HQ Mobile COS"
TRUST_TIER = "TIER-0 LOCAL CHIEF OF STAFF"
MODEL_ENGINE = "Ollama Local (qwen3.5:9b)"

# State tracking for active continuous session ID
CURRENT_SESSION_ID = None

def get_latest_session_id() -> str:
    db_path = os.path.join(PROFILE_DIR, "state.db")
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT session_id FROM messages ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception:
        return None

def clean_output(text: str) -> str:
    ansi_escape = re.compile(r'\x1b\[[0-9;]*[a-zA-Z]|\x1b\([a-zA-Z]|\b\[[0-9;]{1,15}[mK]')
    text = ansi_escape.sub('', text)
    text = re.sub(r'\[[0-9;]{1,30}m', '', text)
    text = re.sub(r'\[0m', '', text)
    if "Hermes" in text:
        parts = text.split("Hermes", 1)[1]
        if "Resume this session with:" in parts:
            parts = parts.split("Resume this session with:", 1)[0]
        clean_lines = []
        for line in parts.splitlines():
            if set(line.strip()).issubset(set("─╭╮╯╰│─ ┌┐└┘├┤┼\t\r\n")):
                continue
            l = line.strip()
            if l.startswith("│"):
                l = l[1:].strip()
            if l.endswith("│"):
                l = l[:-1].strip()
            clean_lines.append(l)
        text = "\n".join(clean_lines).strip()
    return text.strip()

def run_anti_cos(prompt: str) -> str:
    global CURRENT_SESSION_ID
    env = os.environ.copy()
    env["HERMES_HOME"] = PROFILE_DIR
    
    latest = get_latest_session_id()
    if latest and not CURRENT_SESSION_ID:
        CURRENT_SESSION_ID = latest

    now_str = datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M:%S %p")
    grounded_prompt = f"[System Context: Current Local Time is {now_str}]\n\n{prompt}"

    cmd = [HERMES_EXE, "-p", PROFILE_NAME, "chat"]
    if CURRENT_SESSION_ID:
        cmd.extend(["--resume", CURRENT_SESSION_ID])
    cmd.extend(["-q", grounded_prompt])

    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = clean_output(res.stdout or "")
        
        # Capture the newly created/resumed session id
        new_latest = get_latest_session_id()
        if new_latest:
            CURRENT_SESSION_ID = new_latest
            
        return out if out else (res.stderr or "No response returned.")
    except Exception as e:
        return f"Execution error: {e}"

def format_banner() -> str:
    sess_disp = CURRENT_SESSION_ID[:8] if CURRENT_SESSION_ID else "active"
    return (
        f"👑 `[SURFACE: {SURFACE_NAME} | TIER: {TRUST_TIER}]`\n"
        f"🧠 `[ROLE: Anti (Chief of Staff) | SESSION: #{sess_disp}]`\n"
        f"────────────────────────────────────────\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "👑 *Welcome Leo! — Alienware HQ Chief of Staff (Anti)* 🖥️\n\n"
        "🛡️ *Trust Tier:* `TIER-0 LOCAL CHIEF OF STAFF`\n"
        "🧠 *Memory Engine:* `Persistent Thread Active` (Continuous Context)\n\n"
        "Available Executive Commands:\n"
        "⚡ `/status` — System health, GPU, active daemons, & persistence check\n"
        "🔬 `/research <topic>` — Trigger deep research dossier via Research Analyst\n"
        "🏡 `/realestate <query>` — Dispatch tasks to Rosie's Real Estate Copilot\n"
        "🔄 `/reset_thread` — Archive current thread and begin fresh persistent session\n\n"
        "Send any message or voice memo to collaborate directly with Anti!"
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def handle_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    total, used, free = shutil.disk_usage("C:\\")
    disk_free_gb = free // (2**30)
    
    status_msg = (
        f"{format_banner()}\n"
        f"🖥️ *Alienware HQ Status Report*\n"
        f"⏱️ *Time:* {now}\n\n"
        f"✅ *System Core:* ONLINE (Persistent Session Bound)\n"
        f"💾 *C: Drive Free:* {disk_free_gb} GB\n"
        f"🧠 *Local Anti Profile:* `profiles/anti-cos` (Active)\n"
        f"🤖 *Local AI Engine:* Ollama qwen3.5:9b ($0.00 Token Cost)\n"
        f"🏡 *Rosie Real Estate Bot:* Active (@FaithFLRealestate_Bot)\n"
        f"👑 *Leo Chief of Staff Bot:* Active (@LeoAlienwareHQ_Bot)\n"
        f"🛡️ *Security Plane:* Tier-0 Provenance & Identity Handshake Active"
    )
    await update.message.reply_text(status_msg, parse_mode="Markdown")

async def handle_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text
    if not query:
        await update.message.reply_text("Please specify a topic (e.g. `/research Best remote IT tools`).")
        return
    await update.message.reply_text("🔬 *Dispatching task to Hermes Research Analyst...*", parse_mode="Markdown")
    
    env = os.environ.copy()
    env["HERMES_HOME"] = os.path.join(HERMES_ROOT, "profiles", "research-analyst")
    cmd = [HERMES_EXE, "-p", "research-analyst", "chat", "-q", query]
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        resp = clean_output(res.stdout or "")
    except Exception as e:
        resp = f"Research execution error: {e}"

    is_esc, final_resp, _ = check_for_escalation(query, resp, source_bot="Hermes Research Analyst")
    if is_esc:
        full_resp = final_resp
    else:
        full_resp = f"🔬 `[ROLE: Research Specialist | TIER: TIER-1 SPECIALIST]`\n────────────────────────────────────────\n{resp}"

    for chunk in [full_resp[i:i+4000] for i in range(0, len(full_resp), 4000)]:
        await update.message.reply_text(chunk)

async def handle_realestate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text
    if not query:
        await update.message.reply_text("Please specify a real estate query.")
        return
    await update.message.reply_text("🏡 *Dispatching to Real Estate Copilot...*", parse_mode="Markdown")
    
    env = os.environ.copy()
    env["HERMES_HOME"] = os.path.join(HERMES_ROOT, "profiles", "real-estate-copilot")
    cmd = [HERMES_EXE, "-p", "real-estate-copilot", "chat", "-q", query]
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        resp = clean_output(res.stdout or "")
    except Exception as e:
        resp = f"Real estate execution error: {e}"

    is_esc, final_resp, _ = check_for_escalation(query, resp, source_bot="Real Estate Copilot")
    if is_esc:
        full_resp = final_resp
    else:
        full_resp = f"🏡 `[ROLE: Real Estate CoPilot | TIER: TIER-1 SPECIALIST]`\n────────────────────────────────────────\n{resp}"

    for chunk in [full_resp[i:i+4000] for i in range(0, len(full_resp), 4000)]:
        await update.message.reply_text(chunk)

async def handle_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_SESSION_ID
    CURRENT_SESSION_ID = None
    await update.message.reply_text("🔄 *Active persistent thread reset. Next message will initialize a fresh continuous session.*", parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return
    await update.message.reply_text("👑 *Anti (COS) is thinking...*", parse_mode="Markdown")
    resp = await asyncio.to_thread(run_anti_cos, user_text)
    full_resp = f"{format_banner()}{resp}"
    for chunk in [full_resp[i:i+4000] for i in range(0, len(full_resp), 4000)]:
        await update.message.reply_text(chunk)

def main():
    print("Starting Persistent Anti Chief of Staff Telegram Bot (Tier-0 Engine)...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", handle_status))
    app.add_handler(CommandHandler("research", handle_research))
    app.add_handler(CommandHandler("realestate", handle_realestate))
    app.add_handler(CommandHandler("reset_thread", handle_reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
