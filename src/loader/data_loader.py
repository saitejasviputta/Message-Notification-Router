import os
import json
import logging
import pandas as pd

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def load_messages(self, csv_filename: str = "messages.csv") -> pd.DataFrame:
        """
        Loads the main messages dataset.
        Expected columns: message_id, sender_id, group_id, raw_text, image_file, voice_file, label
        """
        csv_path = os.path.join(self.data_dir, csv_filename)
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Messages CSV not found at: {csv_path}")

        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} messages successfully from {csv_filename}")
            # Ensure text columns are handled cleanly
            df["raw_text"] = df["raw_text"].fillna("")
            df["image_file"] = df["image_file"].fillna("")
            df["voice_file"] = df["voice_file"].fillna("")
            return df
        except Exception as e:
            logger.error(f"Error loading message CSV: {e}")
            raise

    def load_json_db(self, json_filename: str) -> dict:
        """
        Loads auxiliary metadata mapping databases (User profile, Senders, Groups, History).
        """
        json_path = os.path.join(self.data_dir, json_filename)
        if not os.path.exists(json_path):
            logger.warning(f"Metadata file {json_filename} not found at {json_path}. Returning empty dictionary.")
            return {}

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded metadata from {json_filename} successfully.")
            return data
        except Exception as e:
            logger.error(f"Error reading JSON {json_filename}: {e}")
            return {}
