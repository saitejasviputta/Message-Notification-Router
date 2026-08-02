import logging
import re

logger = logging.getLogger(__name__)

class UrgencyExtractor:
    def __init__(self):
        # Compile regex patterns for fast evaluation
        self.emergency_rx = re.compile(
            r"\b(emergency|urgent|panic|help|accident|hospital|critical|asap|run to|danger|immediate)\b", 
            re.IGNORECASE
        )
        self.deadline_rx = re.compile(
            r"\b(deadline|due date|expires|expiry|tonight|by tomorrow|by \d+|last chance|before clock|final warning)\b", 
            re.IGNORECASE
        )
        self.exam_meeting_rx = re.compile(
            r"\b(exam|test|quiz|meeting|calendar|zoom|teams|schedule|sync|interview|appointment)\b", 
            re.IGNORECASE
        )
        self.payment_rx = re.compile(
            r"\b(payment|pay|invoice|bill|rent|due fee|amount due|transaction|remind|receipt)\b", 
            re.IGNORECASE
        )
        self.question_rx = re.compile(
            r"\b(who|what|where|when|why|how|can you|could you|please do)\b.*\?", 
            re.IGNORECASE
        )

    def extract(self, message_text: str) -> dict:
        """
        Scans message text for urgency contexts: deadlines, meetings, payments, questions.
        Grades overall urgency: Critical, High, Medium, Low.
        """
        features = {
            "urgency": "Low",
            "contains_deadline": False,
            "contains_meeting": False,
            "contains_payment_reminder": False,
            "is_question_to_user": False
        }

        if not message_text:
            return features

        text = message_text.lower()

        # Check subcomponents
        has_emergency = bool(self.emergency_rx.search(text))
        has_deadline = bool(self.deadline_rx.search(text))
        has_meeting = bool(self.exam_meeting_rx.search(text))
        has_payment = bool(self.payment_rx.search(text))
        has_question = bool(self.question_rx.search(text)) or "?" in text

        # Assign subfeatures
        features["contains_deadline"] = has_deadline or has_emergency
        features["contains_meeting"] = has_meeting
        features["contains_payment_reminder"] = has_payment
        features["is_question_to_user"] = has_question

        # Determine graded urgency level
        if has_emergency:
            urgency = "Critical"
        elif (has_deadline and has_payment) or (has_deadline and has_meeting):
            urgency = "High"
        elif has_deadline or has_meeting or has_payment or has_question:
            urgency = "Medium"
        else:
            urgency = "Low"

        features["urgency"] = urgency
        logger.debug(f"Urgency evaluated as: {urgency} (Emergency={has_emergency}, Deadline={has_deadline})")
        return features
