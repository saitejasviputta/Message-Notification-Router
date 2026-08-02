import unittest
import os
from src.processors.normalizer import TextNormalizer
from src.extractors.sender_extractor import SenderExtractor
from src.extractors.group_extractor import GroupExtractor
from src.extractors.urgency_extractor import UrgencyExtractor
from src.extractors.personalization import PersonalizationExtractor
from src.extractors.safety_checker import SafetyChecker

class TestNotificationRouter(unittest.TestCase):
    def setUp(self):
        self.normalizer = TextNormalizer()
        self.sender_ext = SenderExtractor()
        self.group_ext = GroupExtractor()
        self.urgency_ext = UrgencyExtractor()
        self.personalization_ext = PersonalizationExtractor()
        self.safety_chk = SafetyChecker()

    def test_text_normalization(self):
        raw = "Hello World"
        ocr = "Text from flyer"
        stt = "Voice transcript"
        result = self.normalizer.normalize(raw, ocr, stt)
        self.assertIn("Hello World", result)
        self.assertIn("[Image Text: Text from flyer]", result)
        self.assertIn("[Voice Transcript: Voice transcript]", result)

    def test_urgency_extractor(self):
        # Critical urgency
        res_critical = self.urgency_ext.extract("This is an EMERGENCY, help me please!")
        self.assertEqual(res_critical["urgency"], "Critical")
        self.assertTrue(res_critical["contains_deadline"])

        # High urgency (deadline + meeting)
        res_high = self.urgency_ext.extract("The project meeting deadline is tomorrow.")
        self.assertEqual(res_high["urgency"], "High")

        # Medium urgency (just question)
        res_med = self.urgency_ext.extract("What is your status?")
        self.assertEqual(res_med["urgency"], "Medium")

        # Low urgency
        res_low = self.urgency_ext.extract("Just chilling at home.")
        self.assertEqual(res_low["urgency"], "Low")

    def test_safety_checker(self):
        # OTP phishing
        res_phish = self.safety_chk.extract("Please send your bank verification OTP code immediately.")
        self.assertTrue(res_phish["contains_otp_request"])
        self.assertGreaterEqual(res_phish["scam_score"], 0.5)

        # Suspicious link
        res_link = self.safety_chk.extract("Check this out: http://secure-otp-verification-update.com/login")
        self.assertTrue(res_link["contains_suspicious_link"])

    def test_sender_trust(self):
        senders = {
            "mom": {"name": "Mom", "is_verified": False, "is_vip": True},
            "spammer": {"name": "Spam Corp", "is_verified": False, "is_vip": False}
        }
        history = {
            "mom": {"frequency_per_week": 10.0, "reply_rate": 0.9, "report_count": 0},
            "spammer": {"frequency_per_week": 0.5, "reply_rate": 0.0, "report_count": 5}
        }
        
        # Test VIP
        res_mom = self.sender_ext.extract("mom", senders, history)
        self.assertEqual(res_mom["sender_trust"], "Very Trusted")
        self.assertTrue(res_mom["is_vip_sender"])

        # Test Spammer
        res_spam = self.sender_ext.extract("spammer", senders, history)
        self.assertEqual(res_spam["sender_trust"], "Suspicious")

if __name__ == "__main__":
    unittest.main()
