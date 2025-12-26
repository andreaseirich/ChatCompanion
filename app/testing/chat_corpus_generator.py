"""Deterministic chat corpus generator for testing.

Generates synthetic, web-inspired youth slang chats with obfuscation variants.
All chats are fully synthetic and designed for testing the detection pipeline.
"""

import random
from typing import Dict, List


class ChatCorpusGenerator:
    """Generates deterministic synthetic chat conversations for testing."""

    def __init__(self, seed: int = 1337):
        """
        Initialize generator with seed for reproducibility.

        Args:
            seed: Random seed for deterministic generation
        """
        self.rng = random.Random(seed)
        self._init_phrase_banks()

    def _init_phrase_banks(self):
        """Initialize phrase banks for different risk levels."""
        # Youth slang tokens
        self.slang_tokens = [
            "frfr", "istg", "ong", "wtv", "sm", "bc", "cuz", "rn", "ngl",
            "lowkey", "highkey", "bruh", "jk", "lol", "lmao", "idk", "idc",
            "wbu", "hbu", "tmr", "ttyl", "np", "tbh", "imo", "nvm", "wyd"
        ]

        # GREEN: Healthy, no pressure phrases
        self.green_phrases = [
            "no pressure", "take your time", "np", "all good", "whenever",
            "it's fine", "no worries", "no rush", "take care", "see you later",
            "talk to you later", "have a good day", "sounds good", "okay",
            "sure thing", "that works", "no problem", "you're welcome"
        ]

        # YELLOW: Guilt-shifting + mild pressure (no coercive control)
        self.yellow_guilt_phrases = [
            "you never", "you always", "why don't you", "if you cared",
            "you don't care", "you're not listening", "you're ignoring me",
            "you never respond", "you always do this", "why can't you",
            "you should", "you could", "if you wanted to"
        ]

        self.yellow_pressure_phrases = [
            "please", "come on", "just do it", "it's not that hard",
            "it won't take long", "just a minute", "quick question",
            "can you", "will you", "would you", "could you"
        ]

        # RED: Coercive control + secrecy + isolation + ultimatums
        self.red_secrecy_phrases = [
            "don't tell anyone", "keep this between us", "this is our secret",
            "don't screenshot", "delete this", "don't save this",
            "just between you and me", "nobody needs to know",
            "this stays here", "don't share this"
        ]

        self.red_isolation_phrases = [
            "they don't understand", "they're not like us", "we're different",
            "they wouldn't get it", "don't listen to them", "they're wrong",
            "only I understand you", "they don't care about you"
        ]

        self.red_coercive_phrases = [
            "you have to", "you must", "you need to", "you better",
            "or else", "if you don't", "unless you", "you can't",
            "you're not allowed", "I won't let you"
        ]

        self.red_ultimatum_phrases = [
            "or I'll", "or else I'll", "if you don't I'll", "unless you I'll",
            "I'll leave if", "I'll stop talking if", "we're done if",
            "this is over if", "I'm done if"
        ]

        self.red_proof_phrases = [
            "send me a screenshot", "prove it", "show me", "send proof",
            "I need to see", "take a picture", "send a photo"
        ]

        # Obfuscation variants
        self.obfuscation_spacing = ["r n", "r.n.", "r  n", "r  .  n"]
        self.obfuscation_repeats = ["nowww", "pleeease", "comeee", "dooo it"]
        self.obfuscation_typos = ["rite now", "rite noww", "do itt", "pleease"]
        self.obfuscation_masked = ["stf*u", "st fu", "st f u", "st*f*u"]

    def _add_slang(self, text: str, probability: float = 0.3) -> str:
        """Randomly add slang tokens to text."""
        if self.rng.random() < probability:
            slang = self.rng.choice(self.slang_tokens)
            # Insert slang at random position
            words = text.split()
            if words:
                pos = self.rng.randint(0, len(words))
                words.insert(pos, slang)
                return " ".join(words)
        return text

    def _add_obfuscation(self, text: str, probability: float = 0.2) -> str:
        """Add obfuscation variants to text."""
        if self.rng.random() < probability:
            # Replace "right now" with obfuscated variants
            if "right now" in text.lower() or "rn" in text.lower():
                variant = self.rng.choice(
                    self.obfuscation_spacing + 
                    self.obfuscation_repeats + 
                    self.obfuscation_typos
                )
                text = text.replace("right now", variant).replace("rn", variant)
            
            # Add masked hostility occasionally
            if self.rng.random() < 0.1:
                masked = self.rng.choice(self.obfuscation_masked)
                text = f"{text} {masked}"
        
        return text

    def generate_green_chat(self, chat_id: str) -> Dict:
        """Generate a GREEN (safe) chat conversation."""
        phrases = self.rng.sample(self.green_phrases, k=self.rng.randint(2, 4))
        
        # Create a simple back-and-forth
        messages = []
        for i, phrase in enumerate(phrases):
            speaker = "Friend" if i % 2 == 0 else "You"
            text = phrase
            text = self._add_slang(text, probability=0.2)
            messages.append(f"{speaker}: {text}")
        
        chat_text = "\n".join(messages)
        
        return {
            "id": chat_id,
            "risk_expected": "green",
            "chat_text": chat_text,
            "contains": {
                "no_pressure": True,
                "guilt_shifting": False,
                "threats": False,
                "coercive_control": False,
                "secrecy": False,
                "isolation": False
            }
        }

    def generate_yellow_chat(self, chat_id: str) -> Dict:
        """Generate a YELLOW (concerning) chat conversation."""
        has_guilt = self.rng.random() < 0.7
        has_pressure = self.rng.random() < 0.8
        
        messages = []
        
        # Add guilt-shifting if present
        if has_guilt:
            guilt_phrase = self.rng.choice(self.yellow_guilt_phrases)
            guilt_phrase = self._add_slang(guilt_phrase, probability=0.3)
            messages.append(f"Friend: {guilt_phrase}")
        
        # Add mild pressure
        if has_pressure:
            pressure_phrase = self.rng.choice(self.yellow_pressure_phrases)
            pressure_phrase = self._add_slang(pressure_phrase, probability=0.3)
            messages.append(f"Friend: {pressure_phrase}")
        
        # Add response
        messages.append("You: I'm busy rn")
        
        chat_text = "\n".join(messages)
        chat_text = self._add_obfuscation(chat_text, probability=0.1)
        
        return {
            "id": chat_id,
            "risk_expected": "yellow",
            "chat_text": chat_text,
            "contains": {
                "no_pressure": False,
                "guilt_shifting": has_guilt,
                "threats": False,
                "coercive_control": False,
                "secrecy": False,
                "isolation": False
            }
        }

    def generate_red_chat(self, chat_id: str) -> Dict:
        """Generate a RED (high-risk) chat conversation."""
        has_secrecy = self.rng.random() < 0.8
        has_isolation = self.rng.random() < 0.6
        has_coercive = self.rng.random() < 0.9
        has_ultimatum = self.rng.random() < 0.7
        has_proof = self.rng.random() < 0.5
        
        messages = []
        
        # Add secrecy demands
        if has_secrecy:
            secrecy_phrase = self.rng.choice(self.red_secrecy_phrases)
            secrecy_phrase = self._add_slang(secrecy_phrase, probability=0.2)
            messages.append(f"Friend: {secrecy_phrase}")
        
        # Add isolation attempts
        if has_isolation:
            isolation_phrase = self.rng.choice(self.red_isolation_phrases)
            isolation_phrase = self._add_slang(isolation_phrase, probability=0.2)
            messages.append(f"Friend: {isolation_phrase}")
        
        # Add coercive control
        if has_coercive:
            coercive_phrase = self.rng.choice(self.red_coercive_phrases)
            coercive_phrase = self._add_slang(coercive_phrase, probability=0.2)
            messages.append(f"Friend: {coercive_phrase} answer rn")
        
        # Add ultimatum
        if has_ultimatum:
            ultimatum_phrase = self.rng.choice(self.red_ultimatum_phrases)
            ultimatum_phrase = self._add_slang(ultimatum_phrase, probability=0.2)
            messages.append(f"Friend: Do it {ultimatum_phrase} leave")
        
        # Add proof demand
        if has_proof:
            proof_phrase = self.rng.choice(self.red_proof_phrases)
            proof_phrase = self._add_slang(proof_phrase, probability=0.2)
            messages.append(f"Friend: {proof_phrase}")
        
        chat_text = "\n".join(messages)
        chat_text = self._add_obfuscation(chat_text, probability=0.2)
        
        return {
            "id": chat_id,
            "risk_expected": "red",
            "chat_text": chat_text,
            "contains": {
                "no_pressure": False,
                "guilt_shifting": False,
                "threats": has_ultimatum,
                "coercive_control": has_coercive,
                "secrecy": has_secrecy,
                "isolation": has_isolation
            }
        }

    def generate_chat(self, risk_level: str, chat_id: str) -> Dict:
        """
        Generate a chat for a specific risk level.

        Args:
            risk_level: "green", "yellow", or "red"
            chat_id: Unique identifier for the chat

        Returns:
            Dictionary with chat data
        """
        if risk_level == "green":
            return self.generate_green_chat(chat_id)
        elif risk_level == "yellow":
            return self.generate_yellow_chat(chat_id)
        elif risk_level == "red":
            return self.generate_red_chat(chat_id)
        else:
            raise ValueError(f"Unknown risk level: {risk_level}")

    def generate_corpus(self, count_per_level: int = 30) -> List[Dict]:
        """
        Generate a corpus of chats.

        Args:
            count_per_level: Number of chats to generate per risk level

        Returns:
            List of chat dictionaries
        """
        corpus = []
        
        for level in ["green", "yellow", "red"]:
            for i in range(count_per_level):
                chat_id = f"{level}_{i+1:03d}"
                chat = self.generate_chat(level, chat_id)
                corpus.append(chat)
        
        return corpus

