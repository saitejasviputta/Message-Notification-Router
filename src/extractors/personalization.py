import logging

logger = logging.getLogger(__name__)

class PersonalizationExtractor:
    def extract(self, message_text: str, sender_id: str, group_id: str, user_profile: dict) -> dict:
        """
        Extracts user personalization settings: VIP status, favored groups, 
        topics of interest, and calculates a graded user interest rating (High, Medium, Low).
        """
        features = {
            "user_interest": "Medium",
            "user_favored_group": False,
            "user_ignores_promotions": False
        }

        # Check ignores_promotions preference
        user_ignores_promotions = user_profile.get("ignores_promotions", True)
        features["user_ignores_promotions"] = user_ignores_promotions

        # Check favored groups list
        fav_groups = user_profile.get("favorite_groups", [])
        is_favored_group = group_id in fav_groups if group_id else False
        features["user_favored_group"] = is_favored_group

        # Calculate semantic interest alignment
        user_interests = user_profile.get("interests", [])
        vip_contacts = user_profile.get("vip_contacts", [])
        is_vip = sender_id in vip_contacts

        # Heuristic scoring for interest level
        interest_score = 0
        if is_vip:
            interest_score += 3
        if is_favored_group:
            interest_score += 2

        # Check text alignment against user's interests (keywords)
        text_lower = message_text.lower()
        matched_interests = []
        for interest in user_interests:
            if interest.lower() in text_lower:
                interest_score += 1
                matched_interests.append(interest)

        # Categorize interest score
        if interest_score >= 3:
            interest_level = "High"
        elif interest_score >= 1:
            interest_level = "Medium"
        else:
            interest_level = "Low"

        features["user_interest"] = interest_level
        logger.debug(
            f"Personalization evaluated: Interest={interest_level} "
            f"(VIP={is_vip}, FavGroup={is_favored_group}, MatchedInterests={matched_interests})"
        )
        return features
