# WiseTech: Accessible Tech Support Application
This project is a Flask-based web application designed to help older adults navigate basic technology tasks with the assistance of a simple AI helper and a scam-detection tool. The application includes login, two-factor authentication, an AI assistant, and a scam-checking feature. The interface is intentionally designed with accessibility, large fonts, simplified language, and a friendly visual layout.

## Project Overview
WiseTech aims to provide a supportive environment where seniors can receive help with common technical issues. AI responses are intentionally short and easy to understand. Scam detection is framed in simple and direct language to help users identify risky messages.

## Technologies Used
- Python 3.9
- Flask
- HTML/CSS (custom responsive UI design)
- Google Gemini 2.5 Flash API
- Sessions and 2FA implemented manually for demonstration purposes

## AI Assistance and Code References
Generative AI tools were used during development to assist with drafting portions of the code and structure. All generated pieces were rewritten to match the project’s accessibility goals and design requirements.

### Examples of AI/Code Assistant Use
**1. Google Gemini (via GPT models)**
Gemini and GPT models provided initial versions of:
- Flask route structures (login, POST handling, redirect flow)
- API request formats for the Gemini `generateContent` call
- Error handling patterns
- Prompt design for the AI helper and the scam checker

These suggestions were edited and rewritten to simplify the logic and fit WiseTech’s theme and user audience.

**2. GitHub Copilot**
Copilot provided basic skeletons for:
- HTML structure for forms and layout
- CSS card styling and button templates
- Initial Flask route boilerplate

All Copilot-generated code was rewritten to match WiseTech’s color palette, spacing, simplified layout, and accessibility standards.

### Citations
Some portions of this project reference external documentation:
- Google Gemini 2.5 Flash REST API documentation: https://ai.google.dev/gemini-api/docs/quickstart
- Flask session and redirect patterns: https://flask.palletsprojects.com/

API request structures, templates, and routing were adapted from these sources and modified heavily to fit the project’s goals.

## Setup Instructions
1. Install dependencies:
   pip install -r requirements.txt

2. Create a .env file with your API key:
(echo "GEMINI_API_KEY=YOUR_KEY_HERE" > .env)

For CodeSpace: cp .env.example .env
open file and paste API key 

3. Run the application:
  flask run

For CodeSpace: python app.py

## Notes
This application is a prototype for educational use. AI responses are intentionally simplified. The authentication and scam-analysis features are not intended for production or real-world security use.