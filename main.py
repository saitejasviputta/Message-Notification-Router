import os
import logging
import pandas as pd

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("WhatsAppNotificationRouter")

# Import System Components
from src.loader.data_loader import DataLoader
from src.processors.ocr_engine import OCREngine
from src.processors.stt_engine import STTEngine
from src.processors.normalizer import TextNormalizer
from src.extractors.sender_extractor import SenderExtractor
from src.extractors.group_extractor import GroupExtractor
from src.extractors.urgency_extractor import UrgencyExtractor
from src.extractors.personalization import PersonalizationExtractor
from src.extractors.safety_checker import SafetyChecker
from src.reasoning.context_builder import ContextBuilder
from src.reasoning.reasoning_engine import ReasoningEngine
from src.reasoning.decision_guard import DecisionGuard
from src.evaluation.metrics_calculator import MetricsCalculator

def run_pipeline(data_dir: str = "data", csv_filename: str = "messages.csv", output_filename: str = "data/output/output.csv"):
    logger.info("Initializing Notification Router Pipeline...")
    
    # 1. Initialize Components
    loader = DataLoader(data_dir=data_dir)
    ocr_engine = OCREngine()
    stt_engine = STTEngine()
    normalizer = TextNormalizer()
    
    sender_extractor = SenderExtractor()
    group_extractor = GroupExtractor()
    urgency_extractor = UrgencyExtractor()
    personalization_extractor = PersonalizationExtractor()
    safety_checker = SafetyChecker()
    
    context_builder = ContextBuilder()
    reasoning_engine = ReasoningEngine()
    decision_guard = DecisionGuard()
    metrics_calculator = MetricsCalculator()

    # 2. Ingest Data Databases
    logger.info("Loading input messages and metadata tables...")
    try:
        messages_df = loader.load_messages(csv_filename)
    except FileNotFoundError:
        logger.error(
            f"Could not find {csv_filename} in directory '{data_dir}'. "
            "Please run 'python generate_mock_data.py' first to populate mock workspace assets."
        )
        return

    user_profile = loader.load_json_db("user_profile.json")
    sender_db = loader.load_json_db("senders.json")
    group_db = loader.load_json_db("groups.json")
    history_db = loader.load_json_db("history.json")

    results = []

    # 3. Process records
    logger.info(f"Processing {len(messages_df)} incoming messages...")
    for idx, row in messages_df.iterrows():
        msg_id = row["message_id"]
        sender_id = row["sender_id"]
        group_id = row["group_id"] if pd.notna(row["group_id"]) else ""
        raw_text = row["raw_text"]
        image_file = row["image_file"]
        voice_file = row["voice_file"]
        
        logger.info(f"--- Processing Message ID: {msg_id} (Sender: {sender_id}) ---")

        # Media Processing
        ocr_text = ""
        if image_file:
            img_path = os.path.join(data_dir, "raw", image_file)
            ocr_text = ocr_engine.extract_text(img_path)

        stt_text = ""
        if voice_file:
            audio_path = os.path.join(data_dir, "raw", voice_file)
            stt_text = stt_engine.transcribe(audio_path)

        # Unify Text Modalities
        normalized_body = normalizer.normalize(raw_text, ocr_text, stt_text)
        logger.info(f"Standardized Content: '{normalized_body}'")

        # Parallel Feature Extractions
        sender_features = sender_extractor.extract(sender_id, sender_db, history_db)
        group_features = group_extractor.extract(group_id, normalized_body, group_db, user_profile)
        urgency_features = urgency_extractor.extract(normalized_body)
        personal_features = personalization_extractor.extract(normalized_body, sender_id, group_id, user_profile)
        safety_features = safety_checker.extract(normalized_body)

        # Assemble and Validate Context Schema (Pydantic validation check)
        context_schema = context_builder.assemble_context([
            sender_features, group_features, urgency_features, personal_features, safety_features
        ])

        # AI Reasoning Model Call (Prompt Generation & Gemini/Simulation call)
        prompt_payload = context_builder.build_prompt_inputs(normalized_body, context_schema, user_profile)
        raw_decision = reasoning_engine.reason(prompt_payload, context_schema)

        # Apply Safety/Priority Rule Overrides (Guard Layer)
        final_decision_block = decision_guard.enforce(raw_decision, context_schema)
        
        logger.info(f"Decision: {final_decision_block['decision']} | Confidence: {final_decision_block['confidence']}%")
        logger.info(f"Reasoning: {final_decision_block['reasoning']}")

        results.append({
            "message_id": msg_id,
            "decision": final_decision_block["decision"],
            "confidence": final_decision_block["confidence"],
            "reasoning": final_decision_block["reasoning"]
        })

    # 4. Save and Output results.csv
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    output_df = pd.DataFrame(results)
    
    # Merge back label column for metrics validation if present
    if "label" in messages_df.columns:
        output_df["label"] = messages_df["label"]
        
    output_df.to_csv(output_filename, index=False)
    logger.info(f"Routing calculations successfully exported to {output_filename}")

    # 5. Evaluate Metrics
    metrics_calculator.evaluate(
        output_df, 
        true_label_col="label", 
        pred_col="decision",
        output_dir=os.path.dirname(output_filename)
    )

if __name__ == "__main__":
    run_pipeline()
