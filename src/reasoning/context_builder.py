import logging
import json
from src.extractors.schemas import MessageContextSchema

logger = logging.getLogger(__name__)

class ContextBuilder:
    def assemble_context(self, feature_dicts: list) -> MessageContextSchema:
        """
        Combines multiple feature dictionaries (Sender, Group, Urgency, Personalization, Safety)
        into a single validated MessageContextSchema object.
        """
        combined = {}
        for fd in feature_dicts:
            if fd:
                combined.update(fd)
                
        # Pydantic parses and validates the keys
        context_schema = MessageContextSchema(**combined)
        return context_schema

    def build_prompt_inputs(self, message_text: str, context: MessageContextSchema, user_profile: dict) -> dict:
        """
        Builds instructions, background, and structured features for the LLM prompts.
        """
        # Convert schema features into a clean formatted string
        structured_features_str = json.dumps(context.model_dump(), indent=2)
        
        system_instruction = (
            "You are the Core AI Reasoning Engine of an intelligent WhatsApp Notification Router.\n"
            "Your task is to analyze the incoming message and its structured metadata context, "
            "then decide the routing action: Notify, Digest, or Mute.\n\n"
            "Routing Definitions:\n"
            "- Notify: Interrupt the user immediately. Reserved for important, time-sensitive, personal or VIP messages.\n"
            "- Digest: Save for later summary. Used for lower-priority or informational messages that the user cares about but don't need instant response (e.g. general group chats, interesting promos, non-urgent syncs).\n"
            "- Mute: Completely suppress. Used for low-value, repetitive, spam, OTP/suspicious, or ignored promotional messages.\n\n"
            "You MUST perform Chain-of-Thought reasoning to explain the trade-offs of your decision. "
            "Think about the sender trust, direct mentions, urgency, and user personalization preferences. "
            "Always output your final conclusion in structured JSON format containing:\n"
            "{\n"
            '  "reasoning": "A concise explanation of the decision,",\n'
            '  "decision": "Notify" | "Digest" | "Mute",\n'
            '  "confidence": 0-100\n'
            "}"
        )

        user_content = (
            f"User Profile Info:\n"
            f"- User Name: {user_profile.get('username', 'user')}\n"
            f"- Interests: {', '.join(user_profile.get('interests', []))}\n\n"
            f"Message Text Payload:\n"
            f'"{message_text}"\n\n'
            f"Extracted Context Features:\n"
            f"{structured_features_str}\n\n"
            f"Provide your analysis and output the final JSON decision block."
        )

        return {
            "system_instruction": system_instruction,
            "user_content": user_content
        }
