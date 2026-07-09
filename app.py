from flask import Flask, request, jsonify
import anthropic
import os

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

SYSTEM_PROMPT = """You are a helpful sales assistant for a Monument Signs company.
You help customers with questions about monument signs, pricing, materials, and timelines.

Common info:
- We make custom monument signs for businesses, communities, churches, schools
- Materials: brick, stone, concrete, aluminum, HDU foam
- Process: design → approval → fabrication → installation
- Timeline: typically 4-8 weeks
- We offer free estimates/quotes

Your goals:
1. Answer questions about monument signs
2. Understand what the customer needs
3. Collect: name, business name, location, sign size/type if possible
4. When customer asks for a quote or price or says they want to order - say: "TRANSFER_TO_AGENT"

Always be friendly and professional. Keep answers short and clear.
If customer speaks Ukrainian or another language - respond in that language."""

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
                    "text": "Great! Let me connect you with one of our specialists right now. One moment please! 🙂"
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

@app.route("/", methods=["GET"])
def home():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
