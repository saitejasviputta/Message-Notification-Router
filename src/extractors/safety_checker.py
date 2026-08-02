import logging
import re

logger = logging.getLogger(__name__)

class SafetyChecker:
    def __init__(self):
        # OTP credential request regexes
        self.otp_rx = re.compile(
            r"\b(otp|one time password|verification code|verify code|secret pin|verification pin|passcode)\b", 
            re.IGNORECASE
        )
        # Phishing and urgency scams
        self.phishing_rx = re.compile(
            r"\b(account (suspended|blocked|locked)|verify your identity|login here|security alert|update details|update bank)\b", 
            re.IGNORECASE
        )
        # Spam/scam giveaways
        self.spam_rx = re.compile(
            r"\b(lottery|won|cash prize|free money|click here|claim reward|inherited|billions|gift card)\b", 
            re.IGNORECASE
        )
        # Suspicious URLs
        self.url_rx = re.compile(
            r"https?://[^\s/$.?#].[^\s]*", 
            re.IGNORECASE
        )
        # White list domain keywords for normal URLs (optional)
        self.trusted_domains = ["google.com", "microsoft.com", "github.com", "zoom.us", "teams.live.com", "whatsapp.com"]

    def extract(self, message_text: str) -> dict:
        """
        Scans message text for security vulnerability triggers: phishing, OTPs, suspicious URLs.
        Returns a dict of safety indicators and an aggregate scam score between 0.0 and 1.0.
        """
        features = {
            "contains_suspicious_link": False,
            "contains_otp_request": False,
            "contains_phishing_language": False,
            "scam_score": 0.0
        }

        if not message_text:
            return features

        text = message_text.lower()

        # OTP check
        has_otp = bool(self.otp_rx.search(text))
        
        # Phishing check
        has_phishing = bool(self.phishing_rx.search(text))
        
        # Spam check
        has_spam = bool(self.spam_rx.search(text))

        # URL security checks
        urls = self.url_rx.findall(text)
        has_suspicious_link = False
        
        for url in urls:
            # Simple heuristic: non-https is suspicious, or doesn't match common domains
            if url.startswith("http://"):
                has_suspicious_link = True
                break
            # Check domain pattern for look-alike phishing domains (e.g. secure-bank-login)
            if any(term in url for term in ["login", "verify", "secure", "update", "bank", "free", "gift"]):
                if not any(trusted in url for trusted in self.trusted_domains):
                    has_suspicious_link = True
                    break

        features["contains_otp_request"] = has_otp
        features["contains_phishing_language"] = has_phishing
        features["contains_suspicious_link"] = has_suspicious_link

        # Compute aggregate scam risk score
        score = 0.0
        if has_otp:
            score += 0.5
        if has_phishing:
            score += 0.4
        if has_suspicious_link:
            score += 0.3
        if has_spam:
            score += 0.2

        features["scam_score"] = min(score, 1.0)
        logger.debug(f"Safety evaluation: ScamScore={features['scam_score']} (OTP={has_otp}, Phish={has_phishing}, Link={has_suspicious_link})")
        return features
