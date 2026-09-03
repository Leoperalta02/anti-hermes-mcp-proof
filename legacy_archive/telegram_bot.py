import asyncio
import os
import re
import subprocess
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from escalation_engine import check_for_escalation

TELEGRAM_BOT_TOKEN = "8957280827:AAFn8rasL3h_zMRJGhGn67f6BwfOppc-STw"
HERMES_EXE = r"C:\LEO-LAB-ANTIGRAVITY\hermes-agent\bin\hermes.exe"
HERMES_PROFILE = "real-estate-copilot"
HERMES_HOME = r"C:\LEO-LAB-ANTIGRAVITY\hermes-state\profiles\real-estate-copilot"

ROSIE_REAL_ESTATE_SYSTEM_PROMPT = (
    "You are Rosie's Private Real Estate AI CoPilot for Southwest Florida (Estero, Bonita Springs, Naples, Fort Myers, Cape Coral). "
    "When given a property address or notes for a CMA, Listing, Lead, or Contract: "
    "DO NOT apologize or say you cannot access MLS databases. "
    "If a request requires elevated permissions or capabilities beyond your scope, append '[ESCALATE_TO_ANTI: <reason>]' to your response. "
    "Otherwise, execute the professional Florida real estate framework: "
    "1. For CMAs: Provide benchmark $/sqft ranges (e.g. $320-$380/sqft for Estero golf communities), feature adjustments (pool +$40k, new roof +$25k, view +$30k), and 3 clear price tiers (Conservative, Target Market Value, Premium List Price). "
    "2. For Listings: Write compelling MLS public remarks emphasizing the SWFL lifestyle and private broker notes. "
    "3. For Leads: Draft quick SMS and email follow-up scripts. "
    "4. For Contracts: Calculate FAR/BAR inspection, loan commitment, and closing milestone dates. "
    "Always deliver polished, ready-to-use real estate output."
)

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

def run_hermes_agent(prompt: str) -> str:
    env = os.environ.copy()
    env["HERMES_HOME"] = HERMES_HOME
    
    full_prompt = f"{ROSIE_REAL_ESTATE_SYSTEM_PROMPT}\n\n[Rosie Task / Property Query]:\n{prompt}"
    cmd = [HERMES_EXE, "-p", HERMES_PROFILE, "chat", "-q", full_prompt]
    try:
        res = subprocess.run(cmd, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out = clean_output(res.stdout or "")
        raw_res = out if out else (res.stderr or "No output returned.")
        is_esc, final_msg, _ = check_for_escalation(prompt, raw_res, source_bot="Rosie CoPilot")
        return final_msg
    except Exception as e:
        is_esc, final_msg, _ = check_for_escalation(prompt, f"Error executing assistant: {e}", source_bot="Rosie CoPilot")
        return final_msg

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🏡 *Welcome Rosie!* 👋\n\n"
        "I am your *Private Real Estate AI CoPilot*, running live on your Alienware AI engine at $0 cost.\n\n"
        "Here are quick commands you can use:\n"
        "📊 `/cma <address & details>` — Get valuation & price/sqft comps\n"
        "🏡 `/listing <property notes>` — Generate MLS description & Instagram post\n"
        "🎯 `/lead <inquiry info>` — Draft personalized buyer/seller SMS & emails\n"
        "📄 `/tc <contract details>` — Calculate FAR/BAR closing milestone dates\n\n"
        "Or simply *text or voice-dictate any message* and I will handle it directly!"
    )
    await update.message.reply_text(welcome_text)

async def handle_cma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text
    if not query:
        await update.message.reply_text("Please provide property details after /cma (e.g. /cma 10450 Stoneybrook 3/2 pool home).")
        return
    await update.message.reply_text("📊 Analyzing comps and calculating valuation range...")
    prompt = f"[Channel: Comps & CMA Valuation]\n{query}"
    response = await asyncio.to_thread(run_hermes_agent, prompt)
    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)

async def handle_listing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text
    if not query:
        await update.message.reply_text("Please provide listing details after /listing.")
        return
    await update.message.reply_text("🏡 Drafting MLS remarks and social media package...")
    prompt = f"[Channel: MLS Remarks & Social Copy]\n{query}"
    response = await asyncio.to_thread(run_hermes_agent, prompt)
    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)

async def handle_lead(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text
    if not query:
        await update.message.reply_text("Please provide lead inquiry details after /lead.")
        return
    await update.message.reply_text("🎯 Drafting personalized follow-up SMS and email options...")
    prompt = f"[Channel: Lead Triage & Follow-up]\n{query}"
    response = await asyncio.to_thread(run_hermes_agent, prompt)
    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)

async def handle_tc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else update.message.text
    if not query:
        await update.message.reply_text("Please provide contract details after /tc.")
        return
    await update.message.reply_text("📄 Calculating contract milestone dates and checklists...")
    prompt = f"[Channel: Contract Milestones & TC]\n{query}"
    response = await asyncio.to_thread(run_hermes_agent, prompt)
    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return
    await update.message.reply_text("🤖 Processing with your Alienware AI engine...")
    response = await asyncio.to_thread(run_hermes_agent, user_text)
    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)

def main():
    print("Starting Rosie Realestate CoPilot Telegram Bot (Enhanced Skills)...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cma", handle_cma))
    app.add_handler(CommandHandler("listing", handle_listing))
    app.add_handler(CommandHandler("lead", handle_lead))
    app.add_handler(CommandHandler("tc", handle_tc))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
