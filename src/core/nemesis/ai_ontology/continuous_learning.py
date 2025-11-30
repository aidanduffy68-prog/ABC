"""
Continuous Learning & Feedback Loop Architecture
Enables ABC to learn and evolve from new intelligence and outcomes
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class FeedbackType(Enum):
    """Types of feedback for model improvement"""
    TRUE_POSITIVE = "true_positive"
    FALSE_POSITIVE = "false_positive"
    TRUE_NEGATIVE = "true_negative"
    FALSE_NEGATIVE = "false_negative"
    OUTCOME_VALIDATION = "outcome_validation"
    PATTERN_CORRECTION = "pattern_correction"


@dataclass
class LearningFeedback:
    """Feedback entry for continuous learning"""
    feedback_id: str
    feedback_type: FeedbackType
    entity_id: str
    prediction_id: Optional[str]
    actual_outcome: Dict[str, Any]
    predicted_outcome: Optional[Dict[str, Any]]
    timestamp: datetime
    source: str  # "analyst", "automated", "external_api"
    confidence_impact: float
    notes: Optional[str] = None


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    false_positive_rate: float
    evaluated_at: datetime
    sample_size: int
    performance_by_category: Dict[str, float] = field(default_factory=dict)


class ContinuousLearningSystem:
    """
    Continuous learning system that improves ABC from feedback
    """
    
    def __init__(self, model_registry_path: Optional[str] = None):
        self.model_registry_path = model_registry_path
        self.feedback_history: List[LearningFeedback] = []
        self.model_versions: Dict[str, ModelPerformance] = {}
        
    def record_feedback(
        self,
        feedback_type: FeedbackType,
        entity_id: str,
        actual_outcome: Dict[str, Any],
        predicted_outcome: Optional[Dict[str, Any]] = None,
        prediction_id: Optional[str] = None,
        source: str = "analyst",
        notes: Optional[str] = None
    ) -> LearningFeedback:
        """
        Record feedback for learning
        
        Args:
            feedback_type: Type of feedback (TP, FP, TN, FN)
            entity_id: Entity the feedback relates to
            actual_outcome: What actually happened
            predicted_outcome: What was predicted (if applicable)
            prediction_id: ID of the prediction
            source: Source of feedback
            notes: Additional notes
            
        Returns:
            LearningFeedback entry
        """
        # Calculate confidence impact
        confidence_impact = self._calculate_confidence_impact(
            feedback_type, predicted_outcome, actual_outcome
        )
        
        feedback = LearningFeedback(
            feedback_id=f"feedback_{datetime.now().isoformat()}",
            feedback_type=feedback_type,
            entity_id=entity_id,
            prediction_id=prediction_id,
            actual_outcome=actual_outcome,
            predicted_outcome=predicted_outcome,
            timestamp=datetime.now(),
            source=source,
            confidence_impact=confidence_impact,
            notes=notes
        )
        
        self.feedback_history.append(feedback)
        
        # Trigger learning update if threshold reached
        if len(self.feedback_history) % 100 == 0:
            self._trigger_model_update()
        
        return feedback
    
    def evaluate_model_performance(
        self,
        model_version: str,
        test_data: List[Dict[str, Any]]
    ) -> ModelPerformance:
        """
        Evaluate model performance on test data
        
        Args:
            model_version: Version of model to evaluate
            test_data: Test dataset with predictions and outcomes
            
        Returns:
            ModelPerformance metrics
        """
        # Calculate metrics
        tp = sum(1 for d in test_data if d.get('predicted') and d.get('actual'))
        fp = sum(1 for d in test_data if d.get('predicted') and not d.get('actual'))
        tn = sum(1 for d in test_data if not d.get('predicted') and not d.get('actual'))
        fn = sum(1 for d in test_data if not d.get('predicted') and d.get('actual'))
        
        total = len(test_data)
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        
        # Performance by category
        performance_by_category = self._calculate_category_performance(test_data)
        
        performance = ModelPerformance(
            model_version=model_version,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            false_positive_rate=false_positive_rate,
            evaluated_at=datetime.now(),
            sample_size=total,
            performance_by_category=performance_by_category
        )
        
        self.model_versions[model_version] = performance
        
        return performance
    
    def update_ontology_from_feedback(self) -> Dict[str, Any]:
        """
        Update ontology schema based on feedback patterns
        
        Returns:
            Summary of updates made
        """
        updates = {
            "new_entity_types": [],
            "updated_relationships": [],
            "new_patterns": [],
            "confidence_adjustments": {}
        }
        
        # Analyze feedback for patterns
        false_positives = [f for f in self.feedback_history if f.feedback_type == FeedbackType.FALSE_POSITIVE]
        false_negatives = [f for f in self.feedback_history if f.feedback_type == FeedbackType.FALSE_NEGATIVE]
        
        # Identify new entity types from false negatives
        new_entity_types = self._identify_new_entity_types(false_negatives)
        updates["new_entity_types"] = new_entity_types
        
        # Identify new relationships from patterns
        new_relationships = self._identify_new_relationships(self.feedback_history)
        updates["updated_relationships"] = new_relationships
        
        # Identify new behavioral patterns
        new_patterns = self._identify_new_patterns(self.feedback_history)
        updates["new_patterns"] = new_patterns
        
        # Adjust confidence thresholds
        confidence_adjustments = self._calculate_confidence_adjustments(self.feedback_history)
        updates["confidence_adjustments"] = confidence_adjustments
        
        return updates
    
    def generate_learning_report(self) -> Dict[str, Any]:
        """Generate report on learning progress"""
        recent_feedback = [
            f for f in self.feedback_history
            if (datetime.now() - f.timestamp).days <= 30
        ]
        
        return {
            "total_feedback": len(self.feedback_history),
            "recent_feedback": len(recent_feedback),
            "feedback_by_type": self._count_feedback_by_type(),
            "model_performance": {
                version: {
                    "accuracy": perf.accuracy,
                    "f1_score": perf.f1_score
                }
                for version, perf in self.model_versions.items()
            },
            "improvement_trends": self._calculate_improvement_trends(),
            "recommendations": self._generate_recommendations()
        }
    
    def _calculate_confidence_impact(
        self,
        feedback_type: FeedbackType,
        predicted: Optional[Dict[str, Any]],
        actual: Dict[str, Any]
    ) -> float:
        """Calculate how much this feedback should impact confidence"""
        if not predicted:
            return 0.0
        
        pred_confidence = predicted.get('confidence', 0.5)
        
        if feedback_type == FeedbackType.TRUE_POSITIVE:
            # Positive feedback increases confidence
            return min(0.1, (1.0 - pred_confidence) * 0.2)
        elif feedback_type == FeedbackType.FALSE_POSITIVE:
            # False positive decreases confidence
            return -min(0.15, pred_confidence * 0.3)
        elif feedback_type == FeedbackType.FALSE_NEGATIVE:
            # Missed detection - significant impact
            return -0.2
        else:
            return 0.0
    
    def _trigger_model_update(self):
        """Trigger model retraining when enough feedback collected"""
        # Implementation: Schedule model retraining
        pass
    
    def _identify_new_entity_types(self, false_negatives: List[LearningFeedback]) -> List[str]:
        """Identify new entity types from false negatives"""
        # Implementation: Analyze false negatives for new patterns
        return []
    
    def _identify_new_relationships(self, feedback: List[LearningFeedback]) -> List[Dict[str, Any]]:
        """Identify new relationship types from feedback"""
        # Implementation: Pattern analysis
        return []
    
    def _identify_new_patterns(self, feedback: List[LearningFeedback]) -> List[Dict[str, Any]]:
        """Identify new behavioral patterns"""
        # Implementation: Pattern discovery
        return []
    
    def _calculate_confidence_adjustments(self, feedback: List[LearningFeedback]) -> Dict[str, float]:
        """Calculate confidence threshold adjustments"""
        # Implementation: Statistical analysis
        return {}
    
    def _calculate_category_performance(self, test_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance by category"""
        # Implementation: Category-based metrics
        return {}
    
    def _count_feedback_by_type(self) -> Dict[str, int]:
        """Count feedback by type"""
        counts = {}
        for feedback_type in FeedbackType:
            counts[feedback_type.value] = sum(
                1 for f in self.feedback_history
                if f.feedback_type == feedback_type
            )
        return counts
    
    def _calculate_improvement_trends(self) -> Dict[str, Any]:
        """Calculate improvement trends over time"""
        # Implementation: Trend analysis
        return {"trend": "improving", "rate": 0.05}
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        fp_count = sum(1 for f in self.feedback_history if f.feedback_type == FeedbackType.FALSE_POSITIVE)
        fn_count = sum(1 for f in self.feedback_history if f.feedback_type == FeedbackType.FALSE_NEGATIVE)
        
        if fp_count > len(self.feedback_history) * 0.2:
            recommendations.append("High false positive rate - consider raising confidence thresholds")
        
        if fn_count > len(self.feedback_history) * 0.15:
            recommendations.append("High false negative rate - consider expanding pattern recognition")
        
        if not recommendations:
            recommendations.append("Model performance is stable")
        
        return recommendations

