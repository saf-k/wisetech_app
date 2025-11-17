from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import random
from dotenv import load_dotenv
import requests

# Load .env
load_dotenv()

app = Flask(__name__)
app.secret_key = "changeme-secret-key"


# HELPERS

# Copilot suggested a simple random.randint-based 2FA generator.
# I kept the 6-digit formatting but rewrote spacing, naming, and docstring.

def generate_2fa_code():
    """Generate a six-digit 2FA code."""
    return "{:06d}".format(random.randint(0, 999999))

# REST API request format adapted from Google Gemini Quickstart documentation:
# https://ai.google.dev/gemini-api/docs/quickstart

def call_gemini(prompt):
    """Universal Gemini 2.5 Flash Caller (used by both AI helper + scam checker)."""
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

        headers = {"Content-Type": "application/json"}
        params = {"key": os.getenv("GEMINI_API_KEY")}

        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }

        response = requests.post(url, headers=headers, params=params, json=data)
        result = response.json()

        # Error
        if "error" in result:
            print("\n❌ GEMINI ERROR:", result["error"])
            return None

        # Missing candidates
        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]

        print("\n❌ NO CANDIDATES:", result)
        return None

    except Exception as e:
        print("\n❌ GEMINI EXCEPTION:", e)
        return None


# GitHub Copilot suggested a starter example of calling the Gemini API.
# I rewrote the request structure, shortened the response for simplicity,
# and added error handling, custom instructions, and accessibility-focused controls.

def call_gemini_ai(question):
    """AI Helper → Short simplified answer."""
    prompt = (
        "You are WiseTech, a gentle tech helper for seniors.\n"
        "Answer in **3 short, simple sentences maximum**.\n\n"
        f"Question: {question}"
    )

    response = call_gemini(prompt)
    return response or "AI helper is unavailable."

# Citation: Prompt and "generateContent" structure adapted from Google Gemini REST examples:
# https://ai.google.dev/gemini-api/docs/api-overview

def call_gemini_scam_checker(text):
    """Scam Checker → Short structured answer."""
    prompt = (
      "You are a scam detection assistant for seniors.\n"
    "You must ALWAYS assign a risk level that matches the message.\n\n"
    "Rules:\n"
    "- High Risk: message asks for money, codes, passwords, or personal info.\n"
    "- Medium Risk: message seems suspicious, unknown sender, unusual links.\n"
    "- Low Risk: normal everyday message with no scam indicators.\n\n"
    "Your response MUST be ONLY:\n"
    "Risk: High/Medium/Low\n"
    "Explanation: 1–2 very short sentences.\n\n"
    f"Message:\n{text}"
    )

    response = call_gemini(prompt)
    if not response:
        return {"label": "Unknown", "explanation": "AI unavailable."}

    label = "Unknown"
    explanation = response

    for line in response.splitlines():
        if line.lower().startswith("risk:"):
            label = line.split(":", 1)[1].strip().lower()
        if line.lower().startswith("explanation:"):
            explanation = line.split(":", 1)[1].strip()

        # fallback if model misbehaves
    if label not in ["high", "medium", "low"]:
        label = "low"

    return {
        "label": label.capitalize(),   
        "css_label": label,           
        "explanation": explanation
    }


# ROUTES 

# Citation: Session handling and redirect patterns learned from Flask official docs:
# https://flask.palletsprojects.com/en/3.0.x/quickstart/#sessions

 # GPT suggested the initial structure for a login POST handler (checking username/password
    # and redirecting). I rewrote the validation logic, session management, 
    # and the 2FA generation to fit WiseTech's design.
@app.route("/", methods=["GET", "POST"])
def login():
    # Reset login each time user loads /
    session.clear()

    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if not user or not pwd:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("login"))

        session["username"] = user
        code = generate_2fa_code()
        session["2fa"] = code

        print("\n======================")
        print("  2FA CODE:", code)
        print("======================\n")

        return redirect(url_for("verify"))

    return render_template("login.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        entered = request.form.get("code")
        if entered == session.get("2fa"):
            session["authenticated"] = True
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect code.", "error")

    return render_template("verify_2fa.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("dashboard.html", username=session["username"])


@app.route("/ai-helper", methods=["GET", "POST"])
def ai_helper():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    question = None
    answer = None

    if request.method == "POST":
        question = request.form.get("question")
        answer = call_gemini_ai(question)

    return render_template("ai_helper.html", question=question, answer=answer)


@app.route("/scam-checker", methods=["GET", "POST"])
def scam_checker():
    if not session.get("authenticated"):
        return redirect(url_for("login"))

    text = None
    result = None

    if request.method == "POST":
        text = request.form.get("message_text")
        result = call_gemini_scam_checker(text)

    return render_template("scam_checker.html", text=text, result=result)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ------------------ MAIN ------------------

if __name__ == "__main__":
    app.run(debug=True)
