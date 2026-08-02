import os
import json
import pandas as pd

def create_mock_media_file(base_path, filename, text_content):
    """
    Creates a dummy binary file so os.path.exists passes, 
    and writes the companion transcript/OCR text file.
    """
    os.makedirs(base_path, exist_ok=True)
    bin_path = os.path.join(base_path, filename)
    txt_path = os.path.splitext(bin_path)[0] + ".txt"
    
    # Create empty dummy binary representation
    with open(bin_path, 'wb') as f:
        f.write(b'\x00' * 100) # 100 dummy bytes
        
    # Write companion text content
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text_content)
        
    print(f"Created media asset: {filename} with companion metadata text.")

def generate_all_data():
    raw_dir = "data"
    raw_media_dir = os.path.join(raw_dir, "raw")
    os.makedirs(raw_media_dir, exist_ok=True)
    os.makedirs("data/output", exist_ok=True)

    # 1. Write User Profile JSON
    user_profile = {
        "username": "Saiteja",
        "user_handle": "@saiteja",
        "vip_contacts": ["sender_mom", "sender_boss"],
        "favorite_groups": ["group_project_team", "group_family_chat"],
        "muted_groups": ["group_promotions_spam", "group_gaming_guild"],
        "interests": ["coding", "ai", "machine learning", "hiking", "deals", "shoes"],
        "ignores_promotions": True
    }
    with open(os.path.join(raw_dir, "user_profile.json"), "w", encoding="utf-8") as f:
        json.dump(user_profile, f, indent=2)

    # 2. Write Senders database JSON
    senders = {
        "sender_mom": {"name": "Mom", "is_verified": False, "is_vip": True},
        "sender_boss": {"name": "Boss (Manager)", "is_verified": True, "is_vip": True},
        "sender_spammer": {"name": "MegaDeals Direct", "is_verified": False, "is_vip": False},
        "sender_colleague": {"name": "Alice Developer", "is_verified": False, "is_vip": False},
        "sender_stranger": {"name": "+1 415 555 0199", "is_verified": False, "is_vip": False},
        "sender_bank": {"name": "Apex Trust Bank", "is_verified": True, "is_vip": False}
    }
    with open(os.path.join(raw_dir, "senders.json"), "w", encoding="utf-8") as f:
        json.dump(senders, f, indent=2)

    # 3. Write Groups database JSON
    groups = {
        "group_project_team": {"name": "Q3 Planning Sync", "category": "work", "priority": "High", "is_muted": False},
        "group_family_chat": {"name": "Home Sweet Home", "category": "family", "priority": "High", "is_muted": False},
        "group_promotions_spam": {"name": "Flash Deals & Coupons", "category": "promotions", "priority": "Low", "is_muted": True},
        "group_gaming_guild": {"name": "CS2 Fragging", "category": "society", "priority": "Low", "is_muted": True},
        "group_school_announcements": {"name": "Uni-Class 2026", "category": "school", "priority": "Medium", "is_muted": False}
    }
    with open(os.path.join(raw_dir, "groups.json"), "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=2)

    # 4. Write Historical Interactions database JSON
    history = {
        "sender_mom": {"frequency_per_week": 45.0, "reply_rate": 0.95, "report_count": 0},
        "sender_boss": {"frequency_per_week": 15.0, "reply_rate": 0.85, "report_count": 0},
        "sender_spammer": {"frequency_per_week": 1.2, "reply_rate": 0.00, "report_count": 12},
        "sender_colleague": {"frequency_per_week": 22.0, "reply_rate": 0.70, "report_count": 0},
        "sender_stranger": {"frequency_per_week": 0.0, "reply_rate": 0.00, "report_count": 0},
        "sender_bank": {"frequency_per_week": 2.0, "reply_rate": 0.10, "report_count": 0}
    }
    with open(os.path.join(raw_dir, "history.json"), "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    # 5. Create Mock Media Assets
    create_mock_media_file(
        raw_media_dir, 
        "promo_coupon.png", 
        "FLASH SALE! 50% off running shoes at Nike retail outlets. Present code NIKE50."
    )
    create_mock_media_file(
        raw_media_dir, 
        "emergency_car.wav", 
        "Hey! The car broke down on route 101. Please call me back right away, it's an emergency!"
    )
    create_mock_media_file(
        raw_media_dir, 
        "meeting_slide.png", 
        "Project Review Meeting. Time: Monday 10 AM EST. Zoom Link: https://zoom.us/j/123456789"
    )

    # 6. Generate messages.csv
    # Fields: message_id, sender_id, group_id, raw_text, image_file, voice_file, label
    messages = [
        {
            "message_id": "msg_001",
            "sender_id": "sender_mom",
            "group_id": "",
            "raw_text": "Hey Saiteja, are you coming home for dinner tonight?",
            "image_file": "",
            "voice_file": "",
            "label": "Notify" # Expected VIP/Direct
        },
        {
            "message_id": "msg_002",
            "sender_id": "sender_spammer",
            "group_id": "group_promotions_spam",
            "raw_text": "Claim your free $1000 gift card now! Limited availability.",
            "image_file": "promo_coupon.png",
            "voice_file": "",
            "label": "Mute" # Expected Promo + Ignore preference + spam score
        },
        {
            "message_id": "msg_003",
            "sender_id": "sender_colleague",
            "group_id": "group_project_team",
            "raw_text": "Hey @saiteja, can you double-check the deadline for the model deployment tomorrow?",
            "image_file": "",
            "voice_file": "",
            "label": "Notify" # Expected Mentions + urgency
        },
        {
            "message_id": "msg_004",
            "sender_id": "sender_stranger",
            "group_id": "",
            "raw_text": "Dear customer, your bank card is suspended. Please verify your OTP login code at http://secure-verify-otp-bank.com/online to restore.",
            "image_file": "",
            "voice_file": "",
            "label": "Mute" # Expected Phishing scam override
        },
        {
            "message_id": "msg_005",
            "sender_id": "sender_mom",
            "group_id": "group_family_chat",
            "raw_text": "",
            "image_file": "",
            "voice_file": "emergency_car.wav",
            "label": "Notify" # Expected Voice emergency + VIP group
        },
        {
            "message_id": "msg_006",
            "sender_id": "sender_colleague",
            "group_id": "group_project_team",
            "raw_text": "Here is the summary of the slides we discussed today.",
            "image_file": "meeting_slide.png",
            "voice_file": "",
            "label": "Digest" # Expected Work meeting info - standard digest
        },
        {
            "message_id": "msg_007",
            "sender_id": "sender_spammer",
            "group_id": "",
            "raw_text": "Buy one get one free shoe coupons inside!",
            "image_file": "",
            "voice_file": "",
            "label": "Mute" # Expected Spammer, Promo mute
        },
        {
            "message_id": "msg_008",
            "sender_id": "sender_colleague",
            "group_id": "group_gaming_guild",
            "raw_text": "Anyone up for a CS2 match tonight?",
            "image_file": "",
            "voice_file": "",
            "label": "Mute" # Expected Muted Group + no mentions
        },
        {
            "message_id": "msg_009",
            "sender_id": "sender_boss",
            "group_id": "",
            "raw_text": "Did you submit the payment receipt for the client invoice?",
            "image_file": "",
            "voice_file": "",
            "label": "Notify" # Expected VIP/Verified Business + Payment reminder + Direct Query
        },
        {
            "message_id": "msg_010",
            "sender_id": "sender_colleague",
            "group_id": "group_school_announcements",
            "raw_text": "Note that the university exam schedules have been posted on the main board.",
            "image_file": "",
            "voice_file": "",
            "label": "Digest" # Expected School info - no urgent direct query
        }
    ]

    df = pd.DataFrame(messages)
    df.to_csv(os.path.join(raw_dir, "messages.csv"), index=False)
    print("Created messages.csv with 10 test records.")

if __name__ == "__main__":
    generate_all_data()
