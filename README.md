# Message-Notification-Router

(This project is built as a part of Hackerrank Orchestrate)

An AI-powered system for WhatsApp that decides which messages deserve immediate attention, which should wait, and which should be muted.

## Problem Statement

Modern messaging applications generate an overwhelming number of notifications.

This project builds an AI-powered routing engine that decides whether each incoming WhatsApp message should:

- 🔔 Notify immediately
- 📰 Be included in a digest
- 🔕 Be muted

The system supports text, images, screenshots, posters, and voice notes while personalizing decisions based on user behavior and context.

## Features

- Multimodal message understanding
- OCR for image posters
- Speech-to-text for voice notes
- Personalized notification routing
- Sender trust analysis
- Group importance detection
- Deadline & urgency extraction
- Direct mention override
- Scam & spam detection
- Explainable AI decisions
- Evaluation pipeline

  ## Architecture

- Incoming Message
        │
        ▼
Media Processing
        │
        ▼
Feature Extraction
        │
        ▼
Context Builder
        │
        ▼
AI Reasoning Engine
        │
        ▼
Decision Engine
        │
        ▼
output.csv

## Evaluation

The model is evaluated using

- Accuracy
- Precision
- Recall
- F1 Score
- Confusion Matrix

  ## Why This Architecture?

Unlike a simple prompt-based solution, this project separates the workflow into independent modules:

- Media Processing
- Feature Extraction
- Context Building
- AI Reasoning
- Decision Engine

This modular design improves explainability, scalability, testing, and maintainability while allowing individual components to evolve independently.
