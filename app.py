from flask import Flask, request, jsonify
import anthropic
import os

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a sales assistant for a Monument Signs company called 3D Sign Factory.
You handle the full conversation with customers professionally.

About us:
- We make custom monument signs for businesses, churches, schools, communities
- Materials: brick, stone, concrete, aluminum, HDU foam
- Timeline: 4-8 weeks
- We offer free estimates

Your job:
1. Greet the customer warmly
2. Ask what kind of sign they need
3. Ask about their business name and location
4. Ask about size and material preferences
5. Answer any questions about monument signs
6. When customer wants a quote, price, or is ready to order - write exactly: TRANSFER_TO_AGENT

Always respond in English only.
Keep responses short and friendly."""

conversation_history = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    visitor_id = data.get("visitor", {}).get("id", "unknown")
    user_message = data.get("message", "")

    if visitor_id not in conversation_history:
        conversation_history[visitor_id] = []

    conversation_history[visitor_id].append({
        "role": "user",
        "content": user_message
    })

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=conversation_history[visitor_id]
    )

    reply = response.content[0].text

    conversation_history[visitor_id].append({
        "role": "assistant",
        "content": reply
    })

    if "TRANSFER_TO_AGENT" in reply:
        return jsonify({
            "responses": [
                {
                    "type": "message",
                    "text": "Perfect! Let me connect you with one of our specialists right away. One moment please! 😊"
                },
                {
                    "type": "handoff"
                }
            ]
        })

    return jsonify({
        "responses": [
            {
                "type": "message",
                "text": reply
            }
        ]
    })

@app.route("/chat_started", methods=["POST"])
def chat_started():
    return jsonify({
        "responses": [
            {
                "type": "message",
                "text": "Hello! Welcome to 3D Sign Factory! 👋 I'm your virtual assistant. How can I help you today? Are you looking for a monument sign for your business?"
            }
        ]
    })

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
