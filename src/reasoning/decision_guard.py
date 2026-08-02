import logging
from src.extractors.schemas import MessageContextSchema

logger = logging.getLogger(__name__)

class DecisionGuard:
    def enforce(self, raw_decision: dict, context: MessageContextSchema) -> dict:
        """
        Enforces final guardrails and deterministic overrides over the LLM routing decision.
        Returns final decision block with reasoning additions if overrides occur.
        """
        final_decision = raw_decision["decision"]
        confidence = raw_decision["confidence"]
        reasoning = raw_decision["reasoning"]
        
        # 1. Safety Override: OTP requests or High Scam Scores must ALWAYS be Muted
        if context.contains_otp_request or context.scam_score >= 0.5:
            if final_decision != "Mute":
                logger.warning(
                    f"Safety Override triggered! ScamScore={context.scam_score}, OTP={context.contains_otp_request}. "
                    f"Overriding decision '{final_decision}' to 'Mute'."
                )
                final_decision = "Mute"
                confidence = 100
                reasoning = "[GUARDRAIL OVERRIDE] Safety hazard detected. Message muted due to OTP phishing patterns."

        # 2. Critical Personal Emergency Override: Critical Urgency + VIP/Direct Mention must ALWAYS Notify
        elif context.urgency == "Critical" and (context.is_vip_sender or context.direct_mention):
            if final_decision != "Notify":
                logger.info(
                    f"Priority Override triggered! Critical urgency from VIP or Direct mention. "
                    f"Overriding decision '{final_decision}' to 'Notify'."
                )
                final_decision = "Notify"
                confidence = 100
                reasoning = "[GUARDRAIL OVERRIDE] Critical priority signal detected from VIP/direct mention."

        # 3. Confidence Threshold Fallback: Low-confidence notifications get routed to Digest
        elif final_decision == "Notify" and confidence < 65:
            logger.info(f"Downgrading low-confidence Notify ({confidence}%) to Digest.")
            final_decision = "Digest"
            reasoning = f"[CONFIDENCE GUARD] {reasoning} (Downgraded from Notify due to low confidence score)."

        return {
            "decision": final_decision,
            "confidence": confidence,
            "reasoning": reasoning
        }
