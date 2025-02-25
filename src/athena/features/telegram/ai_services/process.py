from typing import List, Tuple
from collections import defaultdict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from src.athena.core.ai_models.shared import LLMBase
from ..schemas.telegram_schemas import ChatMessage
from src.athena.core import logger


class CommunityMessageProcessor:
    MIN_CLUSTER_SIZE = 2
    MIN_SAMPLES = 2
    CLUSTER_SELECTION_EPSILON = 0.7
    CLUSTER_SELECTION_METHOD = "leaf"
    INITIAL_ENGAGEMENT_THRESHOLD = 0.75
    MIN_MESSAGE_PERCENTAGE = 0.1
    MAX_MESSAGES = 1000
    STOP_WORDS = "english"
    NGRAM_RANGE = (1, 2)
    MIN_DF = 0.0
    MAX_DF = 1.0
    MAX_FEATURES = 1000

    def __init__(self, model: LLMBase):
        self.model = model

        self.tfidf = TfidfVectorizer(
            stop_words=self.STOP_WORDS,
            ngram_range=self.NGRAM_RANGE,
            min_df=self.MIN_DF,
            max_df=self.MAX_DF,
        )

    async def calculate_composite_score(
        self, messages: List[ChatMessage]
    ) -> np.ndarray:
        # Calculate TF-IDF scores
        texts = [msg.message for msg in messages]

        tfidf_matrix = self.tfidf.fit_transform(texts)

        # Get messages with high TF-IDF scores
        importance_scores = tfidf_matrix.sum(axis=1).A1

        # Get engagement scores from messages
        engagement_scores = np.array([msg.engagement_score for msg in messages])

        # Combine with TF-IDF scores (70% importance, 30% engagement)
        weighted_importance_scores = (
            self.COMPOSITE_SCORE_IMPORTANCE_WEIGHT * importance_scores
        )
        weighted_engagement_scores = (
            self.COMPOSITE_SCORE_ENGAGEMENT_WEIGHT * engagement_scores
        )

        composite_scores = weighted_importance_scores + weighted_engagement_scores

        return composite_scores

    async def threshold_calculations(self, composite_scores: np.ndarray) -> float:
        q75, q25 = np.percentile(
            composite_scores, [self.QUANTILE_TOP, self.QUANTILE_BOTTOM]
        )
        iqr = q75 - q25
        threshold = q75 + self.IQR_MULTIPLIER * iqr

        return threshold

    async def analyze_messages(
        self, messages: List[ChatMessage], batch_size: int = 20
    ) -> Tuple[List[ChatMessage], np.ndarray]:
        # --- 1. Initial Filtering (Engagement Only) ---
        important_msgs = [
            msg
            for msg in messages
            if msg.engagement_score > self.INITIAL_ENGAGEMENT_THRESHOLD
        ]

        # Fallback: Ensure we have a minimum number of messages
        if len(important_msgs) < len(messages) * self.MIN_MESSAGE_PERCENTAGE:
            # Sort by engagement and take top N (percentage or MAX_MESSAGES)
            important_msgs = sorted(
                messages, key=lambda msg: msg.engagement_score, reverse=True
            )[
                : max(
                    int(len(messages) * self.MIN_MESSAGE_PERCENTAGE), self.MAX_MESSAGES
                )
            ]
        # --- 2. TF-IDF Calculation (on Filtered Messages) ---
        if not important_msgs:  # Handle the case where no messages pass the filter
            return [], np.array([])

        texts = [msg.message for msg in important_msgs]
        tfidf_matrix = self.tfidf.fit_transform(texts)
        importance_scores = tfidf_matrix.sum(
            axis=1
        ).A1  # This is our final "importance score"

        # --- 3. Get Embeddings ---
        embeddings = await self.get_model_embeddings(important_msgs)

        # Store importance scores *with* the messages for later use.
        important_msgs_with_scores = list(zip(important_msgs, importance_scores))
        return important_msgs_with_scores, embeddings

    async def get_model_embeddings(
        self, messages: List[ChatMessage], batch_size: int = 256
    ) -> np.ndarray:
        from sklearn.preprocessing import StandardScaler

        text_embeddings = []
        time_features = []

        # Process in batches to respect API limits
        for i in range(0, len(messages), batch_size):
            embedding_attempts = 0

            batch = messages[i : i + batch_size]
            batch_texts = []
            batch_time_features = [int(msg.timestamp.timestamp()) for msg in batch]
            time_features.extend(batch_time_features)

            for msg in batch:
                message = msg.message
                if msg.link_preview_title:
                    message += f"\n{msg.link_preview_title}"
                if msg.link_preview_description:
                    message += f"\n{msg.link_preview_description}"

                batch_texts.append(message)

            # Get embeddings from Gemini
            try:
                for _ in range(3):
                    response = self.model.embed_content(batch_texts)
                    break
            except Exception as e:
                embedding_attempts += 1
                logger.error(f"Error embedding content: {e}")
                raise e

            text_embeddings.extend(response)

        # Normalize time features
        time_features = np.array(time_features).reshape(-1, 1)
        time_scaler = StandardScaler()
        normalized_time = time_scaler.fit_transform(time_features)

        combined_embeddings = np.hstack([text_embeddings, normalized_time])

        return np.array(combined_embeddings)

    async def cluster_messages(
        self,
        messages_with_scores: List[Tuple[ChatMessage, float]],
        embeddings: np.ndarray,
    ) -> List[List[ChatMessage]]:
        from sklearn.cluster import HDBSCAN
        from sklearn.preprocessing import StandardScaler

        messages, importance_scores = zip(*messages_with_scores)  # Unpack
        messages, importance_scores = (
            list(messages),
            list(importance_scores),
        )  # Convert to list

        if not embeddings.size:  # Handle empty embeddings array
            return []

        scaler = StandardScaler()
        scaled_embeddings = scaler.fit_transform(embeddings)

        clusterer = HDBSCAN(
            min_cluster_size=self.MIN_CLUSTER_SIZE,
            min_samples=self.MIN_SAMPLES,
            cluster_selection_epsilon=self.CLUSTER_SELECTION_EPSILON,
            cluster_selection_method=self.CLUSTER_SELECTION_METHOD,
        ).fit(scaled_embeddings)

        clusters = defaultdict(list)
        # --- NOISE HANDLING: Discard Noise Messages ---
        for i, label in enumerate(clusterer.labels_):
            if label != -1:  # Only process non-noise messages
                clusters[label].append((messages[i], importance_scores[i]))

        # --- Representative Message Selection (Highest Importance Score) ---
        representative_clusters = []
        for cluster_label, msg_score_pairs in clusters.items():
            # Sort by importance score (descending) and take the top 2
            sorted_msgs = sorted(msg_score_pairs, key=lambda x: x[1], reverse=True)
            representative_clusters.append(
                [msg for msg, score in sorted_msgs[:2]]
            )  # Keep top 2

        return representative_clusters
