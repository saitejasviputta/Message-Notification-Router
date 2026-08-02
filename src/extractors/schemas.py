from pydantic import BaseModel, Field
from typing import Optional

class MessageContextSchema(BaseModel):
    # Sender features
    sender_trust: str = Field(
        default="Neutral", 
        description="Sender trust rating: Very Trusted, Trusted, Neutral, Unknown, Suspicious"
    )
    sender_verification: bool = Field(default=False, description="Whether the sender is business verified")
    sender_frequency: float = Field(default=0.0, description="Estimated message frequency per week")
    is_vip_sender: bool = Field(default=False, description="True if sender is on user's VIP contacts list")

    # Group features
    group_priority: str = Field(default="Medium", description="Estimated group priority: High, Medium, Low")
    group_category: str = Field(default="unknown", description="Group category: family, work, school, promotions, society, personal, unknown")
    group_muted: bool = Field(default=False, description="True if the group is muted in user preferences")
    direct_mention: bool = Field(default=False, description="True if message contains @user mention")

    # Message Context features
    urgency: str = Field(default="Low", description="Calculated urgency: Critical, High, Medium, Low")
    contains_deadline: bool = Field(default=False, description="True if message references a specific deadline/exam/due-date")
    contains_meeting: bool = Field(default=False, description="True if message contains meeting/calendar invites")
    contains_payment_reminder: bool = Field(default=False, description="True if message reminds the user of payments/dues")
    is_question_to_user: bool = Field(default=False, description="True if message is a direct question to the user")

    # Personalization features
    user_interest: str = Field(default="Medium", description="Calculated user affinity/interest: High, Medium, Low")
    user_favored_group: bool = Field(default=False, description="True if user frequently opens/participates in this group")
    user_ignores_promotions: bool = Field(default=False, description="True if user historically ignores ads/promos")

    # Safety features
    contains_suspicious_link: bool = Field(default=False, description="True if message contains sketchy/shortened/non-secure links")
    contains_otp_request: bool = Field(default=False, description="True if message requests One-Time-Password credentials")
    contains_phishing_language: bool = Field(default=False, description="True if message uses identity-theft phishing cues")
    scam_score: float = Field(default=0.0, description="Overall risk index score [0.0 - 1.0]")
