import logging
import re

logger = logging.getLogger(__name__)

class GroupExtractor:
    def extract(self, group_id: str, message_text: str, group_db: dict, user_profile: dict) -> dict:
        """
        Extracts features related to groups: category, mute status, user engagement, 
        and detects if there is a direct mention of the user.
        """
        features = {
            "group_priority": "Medium",
            "group_category": "unknown",
            "group_muted": False,
            "direct_mention": False
        }

        # If not a group chat, default back to Medium priority and personal category
        if not group_id:
            features["group_category"] = "personal"
            features["group_priority"] = "High"
            return features

        group_meta = group_db.get(group_id, {})
        category = group_meta.get("category", "unknown")
        priority = group_meta.get("priority", "Medium")
        muted_groups = user_profile.get("muted_groups", [])
        
        # Determine if group is muted in user preferences
        is_muted = (group_id in muted_groups) or group_meta.get("is_muted", False)

        # Direct mention detection
        user_name = user_profile.get("username", "user")
        user_handle = user_profile.get("user_handle", "@user")
        
        # Match "@username", "@user_handle", or "@user"
        mention_pattern = re.compile(
            rf"({re.escape(user_handle)}|@{re.escape(user_name)})", 
            re.IGNORECASE
        )
        
        has_mention = bool(mention_pattern.search(message_text))

        features["group_priority"] = priority
        features["group_category"] = category
        features["group_muted"] = is_muted
        features["direct_mention"] = has_mention

        logger.debug(f"Group {group_id} features: Priority={priority}, Category={category}, Muted={is_muted}, Mention={has_mention}")
        return features
