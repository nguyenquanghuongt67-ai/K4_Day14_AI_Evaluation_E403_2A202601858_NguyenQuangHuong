"""
Day 14 - AI Evaluation & Benchmarking Pipeline
AICB-P1: AI Practical Competency Program, Phase 1

Key concepts from lecture:
    - Evaluation = Scientific Method for AI (Hypothesis -> Experiment -> Measure -> Conclude -> Iterate)
    - 4 nhóm metrics: Task Completion, Answer Quality, RAG-Specific, Business
    - RAG pipeline metrics: Context Recall -> Context Precision -> Faithfulness -> Answer Relevancy
    - LLM-as-Judge: rubric scoring 1-5, detect bias (positional, verbosity, self-preference)
    - Golden dataset: stratified sampling (5 Easy + 7 Medium + 5 Hard + 3 Adversarial)
    - Failure taxonomy: hallucination, irrelevant, incomplete, off_topic, refusal
    - 5 Whys method for root cause analysis
    - CI/CD integration: eval as quality gate (score < threshold = block deploy)
    - Continuous Improvement Loop: Evaluate -> Analyze -> Improve -> Augment -> Repeat

Instructions:
    1. Fill in every required section marked with TODO.
    2. Do NOT change class/function signatures. The optional ``contexts``
       parameter in ``run_full_eval`` is part of the required interface.
    3. Copy this file to solution/solution.py when done.
    4. Run: pytest tests/ -v

The reranking helper is an optional bonus exercise and may remain unimplemented.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Task 1 - Data Models (Golden Dataset + Evaluation Results)
# ---------------------------------------------------------------------------

@dataclass
class QAPair:
    """
    A question-answer pair for evaluation (part of the Golden Dataset).
    """
    question: str
    expected_answer: str
    context: str = ""
    metadata: dict = field(default_factory=dict)
    retrieved_contexts: list = field(default_factory=list)


@dataclass
class EvalResult:
    """
    Evaluation result for a single Q&A pair.
    """
    qa_pair: QAPair
    actual_answer: str
    faithfulness: float
    relevance: float
    completeness: float
    passed: bool
    failure_type: str | None = None
    context_precision: float | None = None
    context_recall: float | None = None

    def overall_score(self) -> float:
        """Compute the average of faithfulness, relevance, and completeness."""
        return (self.faithfulness + self.relevance + self.completeness) / 3.0


# ---------------------------------------------------------------------------
# Task 2 - RAGAS Evaluator (Simplified word-overlap heuristic)
# ---------------------------------------------------------------------------

STOPWORDS: set[str] = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "of", "in", "on", "at", "to", "for", "with", "as", "by", "and", "or",
    "it", "its", "this", "that", "these", "those", "from", "into", "than",
}

def _tokenize(text: str) -> set[str]:
    """Lowercase word tokenization, ignoring punctuation and stopwords."""
    if not text:
        return set()
    tokens = re.findall(r"\b\w+\b", text.lower())
    return {t for t in tokens if t not in STOPWORDS}


class RAGASEvaluator:
    """
    Evaluates RAG pipeline outputs using RAGAS-inspired heuristics.
    """

    def evaluate_faithfulness(self, answer: str, context: str) -> float:
        if not answer:
            return 1.0
        answer_tokens = _tokenize(answer)
        if not answer_tokens:
            return 1.0
        context_tokens = _tokenize(context)
        faithfulness = len(answer_tokens & context_tokens) / len(answer_tokens)
        return max(0.0, min(1.0, faithfulness))

    def evaluate_relevance(self, answer: str, question: str) -> float:
        if not question:
            return 1.0
        question_tokens = _tokenize(question)
        if not question_tokens:
            return 1.0
        answer_tokens = _tokenize(answer)
        relevance = len(answer_tokens & question_tokens) / len(question_tokens)
        return max(0.0, min(1.0, relevance))

    def evaluate_completeness(self, answer: str, expected: str) -> float:
        if not expected:
            return 1.0
        expected_tokens = _tokenize(expected)
        if not expected_tokens:
            return 1.0
        answer_tokens = _tokenize(answer)
        completeness = len(answer_tokens & expected_tokens) / len(expected_tokens)
        return max(0.0, min(1.0, completeness))

    def evaluate_context_recall(self, contexts: list[str], expected: str) -> float:
        if not expected:
            return 1.0
        expected_tokens = _tokenize(expected)
        if not expected_tokens:
            return 1.0
        union_tokens = set()
        for c in contexts:
            union_tokens.update(_tokenize(c))
        recall = len(expected_tokens & union_tokens) / len(expected_tokens)
        return max(0.0, min(1.0, recall))

    def evaluate_context_precision(
        self,
        contexts: list[str],
        expected: str,
        relevance_threshold: float = 0.1,
    ) -> float:
        if not expected:
            return 1.0
        if not contexts:
            return 0.0
        expected_tokens = _tokenize(expected)
        if not expected_tokens:
            return 1.0
        
        relevant_flags = []
        for chunk in contexts:
            chunk_tokens = _tokenize(chunk)
            coverage = len(chunk_tokens & expected_tokens) / len(expected_tokens)
            relevant_flags.append(1 if coverage >= relevance_threshold else 0)
            
        if not any(relevant_flags):
            return 0.0
            
        total_relevant = sum(relevant_flags)
        ap_sum = 0.0
        rel_count_so_far = 0
        for i, is_rel in enumerate(relevant_flags):
            if is_rel:
                rel_count_so_far += 1
                precision_at_k = rel_count_so_far / (i + 1)
                ap_sum += precision_at_k
                
        return ap_sum / total_relevant

    def run_full_eval(
        self,
        answer: str,
        question: str,
        context: str,
        expected: str,
        contexts: list[str] | None = None,
    ) -> EvalResult:
        faithfulness = self.evaluate_faithfulness(answer, context)
        relevance = self.evaluate_relevance(answer, question)
        completeness = self.evaluate_completeness(answer, expected)
        
        passed = faithfulness >= 0.5 and relevance >= 0.5 and completeness >= 0.5
        
        failure_type = None
        if not passed:
            if faithfulness < 0.3:
                failure_type = "hallucination"
            elif relevance < 0.3:
                failure_type = "irrelevant"
            elif completeness < 0.3:
                failure_type = "incomplete"
            else:
                failure_type = "off_topic"
                
        context_recall = None
        context_precision = None
        if contexts is not None:
            context_recall = self.evaluate_context_recall(contexts, expected)
            context_precision = self.evaluate_context_precision(contexts, expected)
            
        return EvalResult(
            qa_pair=QAPair(question=question, expected_answer=expected, context=context),
            actual_answer=answer,
            faithfulness=faithfulness,
            relevance=relevance,
            completeness=completeness,
            passed=passed,
            failure_type=failure_type,
            context_precision=context_precision,
            context_recall=context_recall
        )

def rerank_by_overlap(contexts: list[str], query: str) -> list[str]:
    return sorted(contexts, key=lambda c: len(_tokenize(c) & _tokenize(query)), reverse=True)


# ---------------------------------------------------------------------------
# Task 3 - LLM Judge
# ---------------------------------------------------------------------------

class LLMJudge:
    def __init__(self, judge_llm_fn: Callable[[str], str]) -> None:
        self.judge_llm_fn = judge_llm_fn

    def score_response(
        self,
        question: str,
        answer: str,
        rubric: dict[str, Any],
    ) -> dict[str, Any]:
        prompt = f"Question: {question}\nAnswer: {answer}\nRubric: {rubric}\nPlease score this. Return JSON with 'scores' (dict of criterion to 0-1 float) and 'reasoning'."
        response_text = self.judge_llm_fn(prompt)
        
        import json
        try:
            start = response_text.find('{')
            end = response_text.rfind('}')
            if start != -1 and end != -1:
                parsed = json.loads(response_text[start:end+1])
                if "scores" in parsed and "reasoning" in parsed:
                    return parsed
        except Exception:
            pass
            
        return {
            "scores": {k: 0.5 for k in rubric.keys()},
            "reasoning": "Failed to parse LLM response"
        }

    def detect_bias(self, scores_batch: list[dict[str, Any]]) -> dict[str, Any]:
        if not scores_batch:
            return {"positional_bias": False, "leniency_bias": False, "severity_bias": False}
            
        total_scores = []
        for batch in scores_batch:
            if "scores" in batch and batch["scores"]:
                avg = sum(batch["scores"].values()) / len(batch["scores"])
                total_scores.append(avg)
            else:
                total_scores.append(0.5)
                
        overall_avg = sum(total_scores) / len(total_scores) if total_scores else 0.5
        leniency_bias = overall_avg > 0.8
        severity_bias = overall_avg < 0.3
        
        positional_bias = False
        if len(total_scores) > 1:
            positional_bias = total_scores[0] > overall_avg
            
        return {
            "positional_bias": positional_bias,
            "leniency_bias": leniency_bias,
            "severity_bias": severity_bias
        }


# ---------------------------------------------------------------------------
# Task 4 - Benchmark Runner
# ---------------------------------------------------------------------------

class BenchmarkRunner:
    def run(
        self,
        qa_pairs: list[QAPair],
        agent_fn: Callable[[str], str],
        evaluator: RAGASEvaluator,
    ) -> list[EvalResult]:
        results = []
        for pair in qa_pairs:
            answer = agent_fn(pair.question)
            eval_res = evaluator.run_full_eval(
                answer=answer,
                question=pair.question,
                context=pair.context,
                expected=pair.expected_answer,
                contexts=pair.retrieved_contexts
            )
            eval_res.qa_pair = pair
            results.append(eval_res)
        return results

    def generate_report(self, results: list[EvalResult]) -> dict[str, Any]:
        if not results:
            return {
                "total": 0, "passed": 0, "pass_rate": 0.0,
                "avg_faithfulness": 0.0, "avg_relevance": 0.0, "avg_completeness": 0.0,
                "avg_context_recall": None, "avg_context_precision": None,
                "failure_types": {}
            }
            
        total = len(results)
        passed = sum(1 for r in results if r.passed)
        
        avg_faithfulness = sum(r.faithfulness for r in results) / total
        avg_relevance = sum(r.relevance for r in results) / total
        avg_completeness = sum(r.completeness for r in results) / total
        
        recall_scores = [r.context_recall for r in results if r.context_recall is not None]
        precision_scores = [r.context_precision for r in results if r.context_precision is not None]
        
        avg_context_recall = sum(recall_scores) / len(recall_scores) if recall_scores else None
        avg_context_precision = sum(precision_scores) / len(precision_scores) if precision_scores else None
        
        failure_types = {}
        for r in results:
            if not r.passed and r.failure_type:
                failure_types[r.failure_type] = failure_types.get(r.failure_type, 0) + 1
                
        return {
            "total": total,
            "passed": passed,
            "pass_rate": passed / total,
            "avg_faithfulness": avg_faithfulness,
            "avg_relevance": avg_relevance,
            "avg_completeness": avg_completeness,
            "avg_context_recall": avg_context_recall,
            "avg_context_precision": avg_context_precision,
            "failure_types": failure_types
        }

    def run_regression(self, new_results: list, baseline_results: list) -> dict:
        new_rep = self.generate_report(new_results)
        base_rep = self.generate_report(baseline_results)
        
        regressions = []
        metrics = ["avg_faithfulness", "avg_relevance", "avg_completeness"]
        
        for m in metrics:
            if base_rep[m] - new_rep[m] > 0.05:
                regressions.append(m.replace("avg_", ""))
                
        return {
            "new_avg_faithfulness": new_rep["avg_faithfulness"],
            "new_avg_relevance": new_rep["avg_relevance"],
            "new_avg_completeness": new_rep["avg_completeness"],
            "baseline_avg_faithfulness": base_rep["avg_faithfulness"],
            "baseline_avg_relevance": base_rep["avg_relevance"],
            "baseline_avg_completeness": base_rep["avg_completeness"],
            "regressions": regressions,
            "passed": len(regressions) == 0
        }

    def identify_failures(
        self,
        results: list[EvalResult],
        threshold: float = 0.5,
    ) -> list[EvalResult]:
        return [r for r in results if r.faithfulness < threshold or r.relevance < threshold or r.completeness < threshold]


# ---------------------------------------------------------------------------
# Task 5 - Failure Analyzer
# ---------------------------------------------------------------------------

class FailureAnalyzer:
    def categorize_failures(
        self, failures: list[EvalResult]
    ) -> dict[str, int]:
        counts = {}
        for f in failures:
            if f.failure_type:
                counts[f.failure_type] = counts.get(f.failure_type, 0) + 1
        return counts

    def find_root_cause(self, failure: EvalResult) -> str:
        scores = {
            "faithfulness": failure.faithfulness,
            "relevance": failure.relevance,
            "completeness": failure.completeness
        }
        lowest_metric = min(scores, key=scores.get)
        
        if lowest_metric == "faithfulness":
            return "Context is missing or irrelevant - improve retrieval"
        elif lowest_metric == "relevance":
            return "Answer does not address the question - improve prompt clarity"
        elif lowest_metric == "completeness":
            return "Answer is missing key information - increase context window or improve generation"
        return "Multiple issues detected - review full pipeline"

    def generate_improvement_log(self, failures: list, suggestions: list[str]) -> str:
        lines = [
            "| Failure ID | Type | Root Cause | Suggested Fix | Status |",
            "|------------|------|------------|---------------|--------|"
        ]
        
        for i, failure in enumerate(failures):
            fid = f"F{i+1:03d}"
            ftype = failure.failure_type or "unknown"
            cause = self.find_root_cause(failure)
            sugg = suggestions[i] if i < len(suggestions) else "Investigate manually"
            lines.append(f"| {fid} | {ftype} | {cause} | {sugg} | Open |")
            
        return "\\n".join(lines)

    def generate_improvement_suggestions(
        self, failures: list[EvalResult]
    ) -> list[str]:
        if not failures:
            return []
            
        cats = self.categorize_failures(failures)
        suggestions = []
        
        if cats.get("hallucination", 0) > 0:
            suggestions.append("Implement hallucination checker to filter unsupported claims")
        if cats.get("irrelevant", 0) > 0:
            suggestions.append("Refine system prompt to enforce strict adherence to user intent")
        if cats.get("incomplete", 0) > 0:
            suggestions.append("Increase chunk size in RAG pipeline to reduce context fragmentation")
        if cats.get("off_topic", 0) > 0:
            suggestions.append("Add intent routing to handle out-of-domain queries properly")
            
        # Ensure we always return at least 3 suggestions if there are failures
        while len(suggestions) < 3:
            suggestions.append("Add few-shot examples showing complete answers to improve completeness")
            
        return suggestions


if __name__ == "__main__":
    qa_pairs = [
        QAPair(
            question="What is RAG?",
            expected_answer="RAG stands for Retrieval-Augmented Generation, which combines retrieval with text generation.",
            context="RAG is a technique that retrieves relevant documents and uses them to ground LLM generation.",
            metadata={"difficulty": "easy", "category": "definition"},
        ),
        QAPair(
            question="What is the capital of France?",
            expected_answer="Paris is the capital of France.",
            context="France is a country in Western Europe. Its capital city is Paris.",
            metadata={"difficulty": "easy", "category": "factual"},
        ),
        QAPair(
            question="Explain backpropagation and why it matters for training",
            expected_answer="Backpropagation is an algorithm for training neural networks by computing gradients efficiently, enabling deep learning models to learn from errors.",
            context="Neural networks learn through gradient descent. Backpropagation efficiently computes these gradients layer by layer.",
            metadata={"difficulty": "medium", "category": "explanation"},
        ),
        QAPair(
            question="Should I use RAG or fine-tuning for my chatbot?",
            expected_answer="It depends on the use case: RAG is better for frequently updated knowledge, fine-tuning for consistent style/behavior. Consider cost, latency, and data freshness.",
            context="RAG retrieves external documents at inference time. Fine-tuning modifies model weights during training.",
            metadata={"difficulty": "hard", "category": "comparison"},
        ),
        QAPair(
            question="What is the meaning of life?",
            expected_answer="This question is outside the scope of this system. I can help with AI and technology questions.",
            context="This is an AI assistant specialized in technology topics.",
            metadata={"difficulty": "adversarial", "category": "out_of_scope"},
        ),
    ]

    evaluator = RAGASEvaluator()
    runner = BenchmarkRunner()

    def mock_agent(question: str) -> str:
        return f"Based on my knowledge: {question[:30]}... The answer involves key concepts."

    results = runner.run(qa_pairs, mock_agent, evaluator)
    report = runner.generate_report(results)
    print("=== Benchmark Report ===")
    for k, v in report.items():
        print(f"  {k}: {v}")

    failures = runner.identify_failures(results, threshold=0.5)
    print(f"\\n=== Failures ({len(failures)}) ===")
    analyzer = FailureAnalyzer()

    categories = analyzer.categorize_failures(failures)
    print("Failure Categories:", categories)

    for f in failures:
        cause = analyzer.find_root_cause(f)
        print(f"  Root cause: {cause}")

    suggestions = analyzer.generate_improvement_suggestions(failures)
    print("\\nImprovement Suggestions:")
    for s in suggestions:
        print(f"  - {s}")

    log = analyzer.generate_improvement_log(failures, suggestions)
    print("\\n=== Improvement Log ===")
    print(log)
