import os
import json
import logging
from src.extractors.schemas import MessageContextSchema

logger = logging.getLogger(__name__)

class ReasoningEngine:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        self.model_name = "gemini-2.5-flash"
        
        if self.api_key:
            try:
                from google import genai
                from google.genai import types
                self.client = genai.Client(api_key=self.api_key)
                self.types = types
                logger.info(f"Gemini Client initialized using model {self.model_name}.")
            except Exception as e:
                logger.error(f"Failed to initialize google-genai client: {e}. Running in Simulation mode.")
                self.client = None
        else:
            logger.warning("GEMINI_API_KEY environment variable not found. Routing will run in Simulation Mode.")

    def reason(self, prompt_inputs: dict, context: MessageContextSchema) -> dict:
        """
        Runs reasoning over prompt inputs and structured contexts.
        Returns a dict: {"decision": str, "confidence": int, "reasoning": str}
        """
        if self.client:
            try:
                logger.info("Executing live reasoning with Gemini...")
                # Request JSON output structure
                config = self.types.GenerateContentConfig(
                    system_instruction=prompt_inputs["system_instruction"],
                    response_mime_type="application/json",
                    temperature=0.1
                )
                
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt_inputs["user_content"],
                    config=config
                )
                
                # Parse JSON response
                result = json.loads(response.text.strip())
                # Ensure keys are present
                if "decision" in result and "confidence" in result and "reasoning" in result:
                    # Clean/normalize decision capitalization
                    result["decision"] = result["decision"].strip().capitalize()
                    return result
                else:
                    logger.warning("Gemini output structure did not match schema. Reverting to parser fallback.")
            except Exception as e:
                logger.error(f"Gemini API call or JSON parsing failed: {e}. Falling back to simulation.")

        # Simulation Mode / Heuristic Engine
        logger.info("Executing simulated reasoning model...")
        return self._simulate_reasoning(context)

    def _simulate_reasoning(self, context: MessageContextSchema) -> dict:
        """
        Simulates the LLM reasoning process using a robust heuristic set.
        Returns the matching JSON response structure.
        """
        decision = "Digest"
        confidence = 70
        reasoning = "General message default."

        # Safety scam checks (Scam score triggers Mute immediately)
        if context.scam_score >= 0.5 or context.contains_otp_request or context.contains_suspicious_link:
            decision = "Mute"
            confidence = 95
            reasoning = "Security threat detected: message contains OTP request or suspicious link patterns."
            return {"decision": decision, "confidence": confidence, "reasoning": reasoning}

        # Urgent VIP/Direct communication checks
        if context.is_vip_sender or (context.sender_trust == "Very Trusted" and context.urgency in ["Critical", "High"]):
            decision = "Notify"
            confidence = 90
            reasoning = f"Urgent request from VIP sender ({context.sender_trust}). User attention required."
            return {"decision": decision, "confidence": confidence, "reasoning": reasoning}

        # Direct mentions in urgent groups overriding muted status
        if context.direct_mention and context.urgency in ["Critical", "High"]:
            decision = "Notify"
            confidence = 85
            reasoning = "Direct user mention paired with critical/high urgency overrides group settings."
            return {"decision": decision, "confidence": confidence, "reasoning": reasoning}

        # Muted groups check
        if context.group_muted:
            if context.direct_mention:
                decision = "Notify"
                confidence = 80
                reasoning = "User is directly mentioned in a muted group. Overriding mute."
            else:
                decision = "Mute"
                confidence = 85
                reasoning = "Group is muted by the user, and no priority override triggers occurred."
            return {"decision": decision, "confidence": confidence, "reasoning": reasoning}

        # User interest personalization checks
        if context.group_category == "promotions":
            if context.user_ignores_promotions:
                decision = "Mute"
                confidence = 85
                reasoning = "Promotional advertisement. User profile is configured to ignore promotions."
            elif context.user_interest == "High":
                decision = "Digest"
                confidence = 75
                reasoning = "Promotional content aligned with expressed user interests. Scheduled for Digest."
            else:
                decision = "Mute"
                confidence = 80
                reasoning = "Low interest promotion, standard mute."
            return {"decision": decision, "confidence": confidence, "reasoning": reasoning}

        # Normal category handling
        if context.group_category in ["family", "work"] and context.urgency in ["Critical", "High", "Medium"]:
            decision = "Notify"
            confidence = 80
            reasoning = f"High-relevance category group ({context.group_category}) containing active deadlines or questions."
        elif context.is_question_to_user:
            decision = "Notify"
            confidence = 75
            reasoning = "Direct query directed to the user. Requiring attention."
        elif context.urgency == "Low" and context.user_interest == "Low":
            decision = "Digest"
            confidence = 70
            reasoning = "Low urgency message with low personalized interest score. Routed to later summary digest."
        else:
            decision = "Digest"
            confidence = 75
            reasoning = "Informational message from regular group/sender. Added to summary digest."

        return {
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning
        }
