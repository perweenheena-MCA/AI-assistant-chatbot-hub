import os
from flask import Flask, jsonify, render_template, request

from chatbot import Chatbot




def create_app() -> Flask:
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Initialize chatbot engine
    bot = Chatbot(
        knowledge_path=os.path.join(app.root_path, "data", "responses.json"),
        weather_api_key=os.getenv("WEATHER_API_KEY"),
    )

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.post("/api/chat")
    def api_chat():
        payload = request.get_json(force=True, silent=True) or {}
        message = (payload.get("message") or "").strip()
        history = payload.get("history") or []

        if not message:
            return jsonify({"reply": "Please type a message."})

        reply = bot.reply(message=message, history=history)
        return jsonify({"reply": reply})

    @app.post("/api/clear_history")
    def api_clear_history():
        # Client clears localStorage; endpoint exists for future server-side persistence.
        return jsonify({"ok": True})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.get("/api/quick_suggestions")
    def quick_suggestions():
        return jsonify(
            {
                "suggestions": [
                    "Who are you?",
                    "Help",
                    "Convert 100 USD to INR",
                    "What time is it?",
                    "Tell me a joke",
                    "Give me motivation",
                    "Weather in London",
                ]
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    # For local development
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

