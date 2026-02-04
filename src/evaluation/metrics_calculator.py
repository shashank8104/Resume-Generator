"""Comprehensive evaluation and metrics calculation module"""

import time
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import cross_val_score
from datetime import datetime

from ..models.resume_schema import Resume
from ..models.job_schema import JobDescription
from ..data.data_storage import DataStorage
from ..screening.screening_pipeline import ScreeningPipeline
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

class MetricsCalculator:
    """Calculate and track performance metrics for the ML models"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.evaluation_history: List[Dict[str, Any]] = []
        
        logger.info("Metrics calculator initialized")
    
    def run_comprehensive_evaluation(self) -> Dict[str, Any]:
        """Run comprehensive evaluation of all models"""
        logger.info("Starting comprehensive model evaluation")
        
        start_time = time.time()
        
        evaluation_results = {
            "evaluation_id": f"eval_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "models_evaluated": [],
            "performance_metrics": {},
            "latency_metrics": {},
            "consistency_metrics": {},
            "recommendations": []
        }
        
        try:
            # Evaluate screening pipeline
            screening_metrics = self._evaluate_screening_pipeline()
            evaluation_results["models_evaluated"].append("screening_pipeline")
            evaluation_results["performance_metrics"]["screening"] = screening_metrics
            
            # Evaluate latency performance
            latency_metrics = self._evaluate_latency()
            evaluation_results["latency_metrics"] = latency_metrics
            
            # Evaluate consistency across roles
            consistency_metrics = self._evaluate_consistency()
            evaluation_results["consistency_metrics"] = consistency_metrics
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                screening_metrics, latency_metrics, consistency_metrics
            )
            evaluation_results["recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"Error during comprehensive evaluation: {e}")
            evaluation_results["error"] = str(e)
        
        evaluation_results["total_evaluation_time"] = time.time() - start_time
        
        # Store evaluation results
        self.evaluation_history.append(evaluation_results)
        
        logger.info(f"Comprehensive evaluation completed in {evaluation_results['total_evaluation_time']:.2f}s")
        
        return evaluation_results
    
    def evaluate_screening_accuracy(
        self,
        test_data: List[Tuple[Resume, JobDescription, bool]],
        screening_pipeline: ScreeningPipeline
    ) -> Dict[str, float]:
        """Evaluate screening pipeline accuracy"""
        logger.info(f"Evaluating screening accuracy on {len(test_data)} samples")
        
        if len(test_data) == 0:
            return {"error": "No test data provided"}
        
        predictions = []
        ground_truth = []
        scores = []
        
        for resume, job_description, true_label in test_data:
            try:
                # Get screening result
                result = screening_pipeline.screen_resume(resume, job_description, explain=False)
                
                # Use overall score as prediction (threshold at 0.6)
                predicted_label = result.overall_score >= 0.6
                
                predictions.append(predicted_label)
                ground_truth.append(true_label)
                scores.append(result.overall_score)
                
            except Exception as e:
                logger.error(f"Error screening resume: {e}")
                continue
        
        if len(predictions) == 0:
            return {"error": "No valid predictions generated"}
        
        # Calculate metrics
        accuracy = accuracy_score(ground_truth, predictions)
        precision = precision_score(ground_truth, predictions, zero_division=0)
        recall = recall_score(ground_truth, predictions, zero_division=0)
        f1 = f1_score(ground_truth, predictions, zero_division=0)
        
        # Additional metrics
        avg_score = np.mean(scores)
        score_std = np.std(scores)
        
        metrics = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "average_score": float(avg_score),
            "score_std": float(score_std),
            "total_samples": len(predictions),
            "positive_predictions": sum(predictions),
            "positive_ground_truth": sum(ground_truth)
        }
        
        logger.info(f"Screening accuracy evaluation completed: {metrics}")
        
        return metrics
    
    def evaluate_score_distribution(
        self,
        resumes: List[Resume],
        job_descriptions: List[JobDescription],
        screening_pipeline: ScreeningPipeline
    ) -> Dict[str, Any]:
        """Evaluate score distribution across different combinations"""
        logger.info("Evaluating score distributions")
        
        scores_by_role = {}
        all_scores = []
        
        for job in job_descriptions:
            role_scores = []
            
            for resume in resumes:
                try:
                    result = screening_pipeline.screen_resume(resume, job, explain=False)
                    role_scores.append(result.overall_score)
                    all_scores.append(result.overall_score)
                except Exception as e:
                    logger.error(f"Error scoring resume: {e}")
                    continue
            
            if role_scores:
                scores_by_role[job.title] = {
                    "mean": float(np.mean(role_scores)),
                    "std": float(np.std(role_scores)),
                    "min": float(np.min(role_scores)),
                    "max": float(np.max(role_scores)),
                    "median": float(np.median(role_scores)),
                    "count": len(role_scores)
                }
        
        # Overall distribution
        overall_distribution = {
            "mean": float(np.mean(all_scores)) if all_scores else 0.0,
            "std": float(np.std(all_scores)) if all_scores else 0.0,
            "min": float(np.min(all_scores)) if all_scores else 0.0,
            "max": float(np.max(all_scores)) if all_scores else 0.0,
            "median": float(np.median(all_scores)) if all_scores else 0.0,
            "percentiles": {
                "25th": float(np.percentile(all_scores, 25)) if all_scores else 0.0,
                "75th": float(np.percentile(all_scores, 75)) if all_scores else 0.0,
                "90th": float(np.percentile(all_scores, 90)) if all_scores else 0.0
            }
        }
        
        return {
            "by_role": scores_by_role,
            "overall": overall_distribution,
            "total_combinations": len(all_scores)
        }
    
    def benchmark_latency(
        self,
        resumes: List[Resume],
        job_descriptions: List[JobDescription],
        screening_pipeline: ScreeningPipeline,
        num_iterations: int = 10
    ) -> Dict[str, float]:
        """Benchmark inference latency"""
        logger.info(f"Benchmarking latency with {num_iterations} iterations")
        
        latencies = []
        
        for i in range(min(num_iterations, len(resumes))):
            resume = resumes[i % len(resumes)]
            job = job_descriptions[i % len(job_descriptions)]
            
            start_time = time.time()
            
            try:
                screening_pipeline.screen_resume(resume, job, explain=False)
                latency = time.time() - start_time
                latencies.append(latency)
            except Exception as e:
                logger.error(f"Error in latency benchmark: {e}")
                continue
        
        if latencies:
            return {
                "mean_latency": float(np.mean(latencies)),
                "std_latency": float(np.std(latencies)),
                "min_latency": float(np.min(latencies)),
                "max_latency": float(np.max(latencies)),
                "median_latency": float(np.median(latencies)),
                "p95_latency": float(np.percentile(latencies, 95)),
                "p99_latency": float(np.percentile(latencies, 99)),
                "total_iterations": len(latencies)
            }
        else:
            return {"error": "No successful latency measurements"}
    
    def compare_baseline_advanced(
        self,
        test_data: List[Tuple[Resume, JobDescription, bool]],
        baseline_pipeline: ScreeningPipeline,
        advanced_pipeline: ScreeningPipeline
    ) -> Dict[str, Any]:
        """Compare baseline vs advanced model performance"""
        logger.info("Comparing baseline vs advanced models")
        
        # Evaluate baseline
        baseline_metrics = self.evaluate_screening_accuracy(test_data, baseline_pipeline)
        
        # Evaluate advanced
        advanced_metrics = self.evaluate_screening_accuracy(test_data, advanced_pipeline)
        
        # Calculate improvements
        improvements = {}
        for metric in ["accuracy", "precision", "recall", "f1_score"]:
            if metric in baseline_metrics and metric in advanced_metrics:
                baseline_val = baseline_metrics[metric]
                advanced_val = advanced_metrics[metric]
                improvement = advanced_val - baseline_val
                improvement_pct = (improvement / baseline_val * 100) if baseline_val > 0 else 0
                
                improvements[metric] = {
                    "absolute_improvement": float(improvement),
                    "percentage_improvement": float(improvement_pct)
                }
        
        return {
            "baseline_metrics": baseline_metrics,
            "advanced_metrics": advanced_metrics,
            "improvements": improvements,
            "recommendation": self._get_model_recommendation(improvements)
        }
    
    def _evaluate_screening_pipeline(self) -> Dict[str, Any]:
        """Evaluate the screening pipeline with synthetic data"""
        # Generate synthetic test data for evaluation
        from ..data.synthetic_data_generator import SyntheticDataGenerator
        
        generator = SyntheticDataGenerator()
        dataset = generator.generate_dataset(50, 25)  # Small dataset for testing
        
        # Create test cases
        test_cases = []
        resumes_data = dataset["resumes"][:20]  # Use first 20 resumes
        jobs_data = dataset["job_descriptions"][:10]  # Use first 10 jobs
        
        # Convert to Resume and JobDescription objects
        resumes = []
        for resume_data in resumes_data:
            try:
                resume = Resume(**resume_data)
                resumes.append(resume)
            except Exception as e:
                logger.error(f"Error creating resume object: {e}")
                continue
        
        jobs = []
        for job_data in jobs_data:
            try:
                job = JobDescription(**job_data)
                jobs.append(job)
            except Exception as e:
                logger.error(f"Error creating job object: {e}")
                continue
        
        # Generate synthetic ground truth labels
        for resume in resumes[:5]:  # Use subset for evaluation
            for job in jobs[:3]:
                # Simple heuristic for ground truth: match if role matches
                ground_truth = resume_data.get("role") == job_data.get("role")
                test_cases.append((resume, job, ground_truth))
        
        if not test_cases:
            return {"error": "No valid test cases generated"}
        
        # Evaluate using test cases
        screening_pipeline = ScreeningPipeline()
        metrics = self.evaluate_screening_accuracy(test_cases, screening_pipeline)
        
        return metrics
    
    def _evaluate_latency(self) -> Dict[str, float]:
        """Evaluate system latency"""
        # Generate test data
        from ..data.synthetic_data_generator import SyntheticDataGenerator
        from ..models.resume_schema import ExperienceLevel
        from ..models.job_schema import JobLevel
        
        generator = SyntheticDataGenerator()
        
        # Generate small test set
        test_resumes = []
        test_jobs = []
        
        for i in range(5):
            resume = generator.generate_resume("software_engineer", ExperienceLevel.MID)
            job = generator.generate_job_description("software_engineer", JobLevel.MID)
            test_resumes.append(resume)
            test_jobs.append(job)
        
        screening_pipeline = ScreeningPipeline()
        latency_metrics = self.benchmark_latency(test_resumes, test_jobs, screening_pipeline, 5)
        
        return latency_metrics
    
    def _evaluate_consistency(self) -> Dict[str, Any]:
        """Evaluate model consistency across roles"""
        roles = ["software_engineer", "data_scientist", "marketing_manager"]
        consistency_scores = {}
        
        from ..data.synthetic_data_generator import SyntheticDataGenerator
        from ..models.resume_schema import ExperienceLevel
        from ..models.job_schema import JobLevel
        
        generator = SyntheticDataGenerator()
        screening_pipeline = ScreeningPipeline()
        
        for role in roles:
            role_scores = []
            
            try:
                # Generate test data for this role
                for i in range(3):  # Small sample size
                    resume = generator.generate_resume(role, ExperienceLevel.MID)
                    job = generator.generate_job_description(role, JobLevel.MID)
                    
                    result = screening_pipeline.screen_resume(resume, job, explain=False)
                    role_scores.append(result.overall_score)
                
                if role_scores:
                    consistency_scores[role] = {
                        "mean_score": float(np.mean(role_scores)),
                        "std_score": float(np.std(role_scores)),
                        "sample_count": len(role_scores)
                    }
                
            except Exception as e:
                logger.error(f"Error evaluating consistency for {role}: {e}")
                consistency_scores[role] = {"error": str(e)}
        
        # Calculate overall consistency
        all_stds = [scores.get("std_score", 0) for scores in consistency_scores.values() if "std_score" in scores]
        overall_consistency = {
            "average_std": float(np.mean(all_stds)) if all_stds else 0.0,
            "roles_evaluated": len(consistency_scores)
        }
        
        return {
            "by_role": consistency_scores,
            "overall": overall_consistency
        }
    
    def _generate_recommendations(
        self,
        screening_metrics: Dict[str, Any],
        latency_metrics: Dict[str, float],
        consistency_metrics: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on evaluation results"""
        recommendations = []
        
        # Accuracy recommendations
        if "accuracy" in screening_metrics:
            accuracy = screening_metrics["accuracy"]
            if accuracy < 0.8:
                recommendations.append(
                    f"Screening accuracy ({accuracy:.1%}) is below target (80%). "
                    "Consider retraining with more diverse data or adjusting model parameters."
                )
        
        # Latency recommendations
        if "mean_latency" in latency_metrics:
            mean_latency = latency_metrics["mean_latency"]
            if mean_latency > 2.0:  # 2 seconds threshold
                recommendations.append(
                    f"Mean inference latency ({mean_latency:.2f}s) exceeds target (2.0s). "
                    "Consider model optimization or caching strategies."
                )
        
        # Consistency recommendations
        if "overall" in consistency_metrics and "average_std" in consistency_metrics["overall"]:
            avg_std = consistency_metrics["overall"]["average_std"]
            if avg_std > 0.2:  # High variability
                recommendations.append(
                    f"High score variability (std: {avg_std:.3f}) across roles. "
                    "Consider role-specific model fine-tuning."
                )
        
        # General recommendations
        if not recommendations:
            recommendations.append("All metrics are within acceptable ranges. System performing well.")
        
        return recommendations
    
    def _get_model_recommendation(self, improvements: Dict[str, Dict[str, float]]) -> str:
        """Get recommendation based on model comparison"""
        significant_improvements = [
            metric for metric, improvement in improvements.items()
            if improvement.get("percentage_improvement", 0) > 5  # 5% improvement threshold
        ]
        
        if len(significant_improvements) >= 2:
            return "Advanced model shows significant improvements. Recommend deployment."
        elif len(significant_improvements) == 1:
            return "Advanced model shows some improvements. Consider A/B testing."
        else:
            return "Advanced model shows minimal improvements. Baseline may be sufficient."
    
    def get_evaluation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent evaluation history"""
        return self.evaluation_history[-limit:] if self.evaluation_history else []
    
    def export_metrics(self, format: str = "json") -> Dict[str, Any]:
        """Export metrics in specified format"""
        if format == "json":
            return {
                "evaluation_history": self.evaluation_history,
                "total_evaluations": len(self.evaluation_history),
                "exported_at": datetime.now().isoformat()
            }
        else:
            raise ValueError(f"Unsupported export format: {format}")