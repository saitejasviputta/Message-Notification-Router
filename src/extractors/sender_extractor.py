import logging

logger = logging.getLogger(__name__)

class SenderExtractor:
    def extract(self, sender_id: str, sender_db: dict, historical_interactions: dict) -> dict:
        """
        Extracts features related to the sender from the metadata DB.
        Assigns trust grades: Very Trusted, Trusted, Neutral, Unknown, Suspicious.
        """
        features = {
            "sender_trust": "Neutral",
            "sender_verification": False,
            "sender_frequency": 0.0,
            "is_vip_sender": False
        }

        if not sender_id:
            return features

        # Retrieve sender profile details
        sender_profile = sender_db.get(sender_id, {})
        is_verified = sender_profile.get("is_verified", False)
        is_vip = sender_profile.get("is_vip", False)
        
        # Calculate messaging frequency
        interaction_history = historical_interactions.get(sender_id, {})
        msg_freq = interaction_history.get("frequency_per_week", 0.0)
        reply_rate = interaction_history.get("reply_rate", 0.0)
        report_count = interaction_history.get("report_count", 0)

        # Base Trust Heuristics
        if report_count > 0:
            trust = "Suspicious"
        elif is_vip:
            trust = "Very Trusted"
        elif reply_rate > 0.6 or (msg_freq > 10 and reply_rate > 0.4):
            trust = "Trusted"
        elif msg_freq == 0.0 and reply_rate == 0.0:
            trust = "Unknown"
        else:
            trust = "Neutral"

        # Special overrides based on verification flag
        if is_verified:
            features["sender_verification"] = True

        features["sender_trust"] = trust
        features["sender_frequency"] = msg_freq
        features["is_vip_sender"] = is_vip

        logger.debug(f"Sender {sender_id} trust evaluated as: {trust} (VIP={is_vip}, Verified={is_verified})")
        return features
