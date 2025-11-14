from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import random
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "changeme-secret-key"


# ------------------ HELPERS ------------------

def generate_2fa_code():
    """Generate a six-digit 2FA code."""
    return "{:06d}".format(random.randint(0, 999999))


def call_gemini_ai(prompt):
    """AI helper using the updated Gemini REST API."""
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": os.getenv("GOOGLE_API_KEY")}

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "You are WiseTech, a patient helper for older adults. "
                                "Explain simply, step-by-step:\n\n" + prompt
                            )
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, params=params, json=data)
        result = response.json()

        if "error" in result:
            print("\n❌ Gemini API Error:", result["error"])
            return "AI helper is unavailable (Gemini error)."

        if "candidates" not in result:
            print("\n❌ Missing 'candidates':", result)
            return "AI helper could not generate a response."

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        print("Gemini REST Exception:", e)
        return "AI helper is unavailable."




def call_gemini_scam_checker(text):
    """Scam detection using updated Gemini REST API."""
    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        params = {"key": os.getenv("GOOGLE_API_KEY")}

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "You help seniors identify scams.\n"
                                "Respond EXACTLY:\n"
                                "Risk: High/Medium/Low\n"
                                "Explanation: short and simple.\n\n"
                                f"Message:\n{text}"
                            )
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, params=params, json=data)
        result = response.json()

        if "error" in result:
            print("\n❌ Gemini API Error:", result["error"])
            return {"label": "Unknown", "explanation": "Gemini API error."}

        if "candidates" not in result:
            print("\n❌ Missing 'candidates':", result)
            return {"label": "Unknown", "explanation": "Could not analyze message."}

        output = result["candidates"][0]["content"]["parts"][0]["text"]

        label = "Unknown"
        explanation = output

        for line in output.splitlines():
            if line.lower().startswith("risk"):
                label = line.split(":", 1)[1].strip()
            if line.lower().startswith("explanation"):
                explanation = line.split(":", 1)[1].strip()

        return {"label": label, "explanation": explanation}

    except Exception as e:
        print("Gemini REST Exception:", e)
        return {"label": "Unknown", "explanation": "Scam checker unavailable."}



# ------------------ ROUTES ------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        pwd = request.form.get("password")

        if not user or not pwd:
            flash("Please enter both username and password.", "error")
            return redirect(url_for("login"))

        session["username"] = user

        # Generate 2FA
        code = generate_2fa_code()
        session["2fa"] = code

        print("\n======================")
        print("  2FA CODE:", code)
        print("======================\n")

        flash("A 2FA code was sent (check terminal).", "info")
        return redirect(url_for("verify"))

    return render_template("login.html")


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        entered = request.form.get("code")
        real = session.get("2fa")

        if entered == real:
            session["authenticated"] = True
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect code. Try again.", "error")

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
    flash("Logged out.", "info")
    return redirect(url_for("login"))


# ------------------ MAIN ------------------

if __name__ == "__main__":
    app.run(debug=True)
