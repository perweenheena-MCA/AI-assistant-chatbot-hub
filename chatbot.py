import difflib
import json
import os
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests


@dataclass
class MatchResult:
    intent: str
    score: float
    payload: Optional[Dict[str, Any]] = None


class Chatbot:
    """A rule-based + fuzzy matching chatbot.

    Designed for hackathon friendliness: predictable, fast, no heavy ML dependencies.
    """

    def __init__(self, knowledge_path: str, weather_api_key: Optional[str] = None):
        self.weather_api_key = weather_api_key
        self.knowledge_path = knowledge_path
        self.knowledge = self._load_knowledge(knowledge_path)

        # Precompile patterns
        self._currency_re = re.compile(
            r"convert\s+(?P<amount>[-+]?\d+(?:\.\d+)?)\s*(?P<from>[a-zA-Z]{3})\s*(?:to|into)\s*(?P<to>[a-zA-Z]{3})",
            re.IGNORECASE,
        )
        self._time_re = re.compile(r"\b(time|date|today|current time)\b", re.IGNORECASE)
        self._weather_re = re.compile(r"\bweather\b", re.IGNORECASE)

    def _load_knowledge(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            # Minimal fallback
            return {"intents": []}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _normalize(self, s: str) -> str:
        s = s.strip().lower()
        s = re.sub(r"\s+", " ", s)
        return s

    def _fuzzy_match_intent(self, message: str) -> MatchResult:
        msg = self._normalize(message)

        best_intent = "fallback"
        best_score = 0.0
        best_payload = None

        intents = self.knowledge.get("intents", [])
        for intent in intents:
            name = intent.get("name", "")
            examples = intent.get("examples", [])
            if not name or not examples:
                continue

            # difflib ratio against each example; keep best.
            scores = [difflib.SequenceMatcher(None, msg, self._normalize(ex)).ratio() for ex in examples]
            score = max(scores) if scores else 0
            if score > best_score:
                best_score = score
                best_intent = name

        # Threshold tuned for hackathon reliability.
        if best_score < 0.55:
            return MatchResult(intent="fallback", score=best_score)

        # For certain intents, extract payload.
        payload = self._extract_payload(best_intent, message)
        return MatchResult(intent=best_intent, score=best_score, payload=payload)

    def _extract_payload(self, intent: str, message: str) -> Optional[Dict[str, Any]]:
        if intent == "currency_converter":
            m = self._currency_re.search(message)
            if m:
                return {
                    "amount": float(m.group("amount")),
                    "from": m.group("from").upper(),
                    "to": m.group("to").upper(),
                }
        if intent == "weather":
            # Try to get city after the word weather
            city = None
            m = re.search(r"weather\s+(?:in\s+)?(?P<city>[a-zA-Z\s]{2,})", message, re.IGNORECASE)
            if m:
                city = m.group("city").strip()
            return {"city": city}
        return None

    def _pick_response(self, intent: str, payload: Optional[Dict[str, Any]] = None) -> str:
        """Pick a response template from knowledge base."""
        intent_block = None
        for it in self.knowledge.get("intents", []):
            if it.get("name") == intent:
                intent_block = it
                break

        if not intent_block:
            return "I’m not sure how to respond to that yet."

        responses = intent_block.get("responses", [])
        if not responses:
            return "Got it."

        # Deterministic enough to be beginner-friendly; still varied.
        template = random.choice(responses)

        if payload:
            # Simple template substitution for known keys.
            for k, v in payload.items():
                template = template.replace("{{" + k + "}}", str(v))

        return template

    # ---------- Feature implementations ----------

    def _handle_currency(self, payload: Dict[str, Any]) -> str:
        amount = payload["amount"]
        from_cur = payload["from"]
        to_cur = payload["to"]

        # Public/free approach: exchangerate.host (no API key requirement)
        # Some environments may block; handle gracefully.
        url = f"https://api.exchangerate.host/convert?from={from_cur}&to={to_cur}&amount={amount}"
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            result = data.get("result")
            if result is None:
                raise ValueError("No result in response")
            return f"{amount:.2f} {from_cur} ≈ {result:.2f} {to_cur}."
        except Exception:
            return (
                f"I couldn’t fetch live exchange rates right now. "
                f"Try again later or check your connection. (Requested: {amount} {from_cur} to {to_cur})"
            )

    def _handle_weather(self, payload: Dict[str, Any]) -> str:
        city = payload.get("city")
        if not city:
            return "Tell me a city for the weather (example: Weather in London)."

        # Use OpenWeatherMap if WEATHER_API_KEY is provided.
        # Falls back to an offline message if not configured.
        if not self.weather_api_key:
            return (
                "Weather API key not configured. Set WEATHER_API_KEY as an environment variable "
                "to enable live weather. Example: Weather in London."
            )

        url = (
            "https://api.openweathermap.org/data/2.5/weather"
            f"?q={requests.utils.quote(city)}&appid={self.weather_api_key}&units=metric"
        )
        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()
            name = data.get("name") or city
            temp = data.get("main", {}).get("temp")
            desc = data.get("weather", [{}])[0].get("description")
            if temp is None:
                raise ValueError("No temperature")
            desc = desc or "weather"
            return f"Weather in {name}: {temp:.1f}°C, {desc}."
        except Exception:
            return f"I couldn’t fetch the weather for {city}. Try another city."

    def _handle_time_date(self) -> str:
        now = datetime.now()
        return f"Current date: {now.strftime('%Y-%m-%d')} | Current time: {now.strftime('%H:%M:%S')}"

    def _handle_typing_delay(self, history: List[Dict[str, str]], seconds: float = 0.8) -> None:
        # Backend delay is optional; frontend typing indicator handles UI.
        # Keep minimal to not slow judge demos.
        _ = history
        if seconds:
            time.sleep(0.2)

    # ---------- Public reply API ----------

    def reply(self, message: str, history: List[Dict[str, str]]) -> str:
        self._handle_typing_delay(history)

        msg = message.strip()
        if not msg:
            return "Please type something."

        # Command-style intents based on keywords first (more reliable than fuzzy).
        if self._currency_re.search(msg):
            payload = self._extract_payload("currency_converter", msg) or {}
            return self._handle_currency(payload)

        if self._weather_re.search(msg) and "in" in msg.lower() or "weather" in msg.lower():
            # Try best-effort parsing
            payload = self._extract_payload("weather", msg) or {}
            return self._handle_weather(payload)

        if self._time_re.search(msg):
            return self._handle_time_date()

        # Handle assistant basic commands.
        match = self._fuzzy_match_intent(msg)
        intent = match.intent

        if intent == "currency_converter":
            payload = match.payload or {}
            if payload:
                return self._handle_currency(payload)
            return "Example: Convert 100 USD to INR"

        if intent == "weather":
            payload = match.payload or {}
            return self._handle_weather(payload)

        if intent == "time_date":
            return self._handle_time_date()

        if intent == "joke":
            jokes = self.knowledge.get("jokes", [])
            if jokes:
                return random.choice(jokes)
            return self._pick_response("joke")

        if intent == "motivation":
            quotes = self.knowledge.get("motivational_quotes", [])
            if quotes:
                return random.choice(quotes)
            return self._pick_response("motivation")

        # Fallback to fuzzy-responses from JSON.
        if intent != "fallback":
            return self._pick_response(intent, match.payload)

        # Context-based fallback (simple): use last user message for continuity.
        if history:
            last_user = None
            for item in reversed(history):
                if item.get("role") == "user":
                    last_user = item.get("message")
                    break
            if last_user:
                # Small hint
                return (
                    "I’m still learning. Try asking one of these: "
                    "Who are you?, Help, Convert X USD to INR, Weather in London, or Tell me a joke."
                )

        return (
            "I’m not sure I understood. Try: \n"
            "• Who are you?\n"
            "• Convert 100 USD to INR\n"
            "• Weather in London\n"
            "• Tell me a joke\n"
            "• Give me motivation"
        )

