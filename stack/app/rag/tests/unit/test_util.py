from typing import Tuple

import pytest

from stack.app.rag.util import check_content_is_useful, deduplicate_chunk


@pytest.mark.parametrize(
    "content,min_word_count,max_number_ratio,information_density_ratio,expected",
    [
        ("", 10, 0.5, 0.5, (False, "No words in content")),
        ("asdf asdf asdf", 10, 0.5, 0.5, (False, "word_count=3 < threshold=10")),
        (
            "This is a highly informative sentence that has lots of detail about some fact or another.",
            10,
            0.5,
            0.5,
            (True, "Document content passes checks."),
        ),
        (
            "3 Llama-2 (7B, 13B, and 70B), Llama-3 (8B and 70B), Gemma 2B, Mistral 7B, JudgeLM 7B, GPT-4 Turbo Table 1: The exam-taker models and judge models we use in our experiments. We consider a wide variety of judge models; to get a comprehensive overview of their (potential) biases, we consider exam-taker models of various sizes and types. Benchmark As our testbed, we use the TriviaQA dataset (Joshi et al., 2017), consisting of 95K question-answer pairs sourced from 14 trivia and quiz league websites. Each question in the train and validation set is annotated with a list of short answers containing a minimal set of facts and evidence documents collected from Wikipedia and the Web. For our experiments, we use the validation set of the unfiltered partition of the benchmark, using the short answers as reference answers. We use the training set for few-shot examples. Since experiments require manual annotation of the exam-taker model responses, we use a random sample of 400 questions from the dataset. Exam-taker models To understand the strengths and weaknesses of different judges, we benchmark pre-trained (base) and instruction-tuned (chat) exam-taker models across a wide variety of model sizes and examine the quality of the evaluations from different judge models. In particular, we consider Llama-2 (Touvron et al., 2023) in 7B, 13B, and 70B parameter sizes for both base and chat versions, Mistral 7B (Jiang et al., 2023) base and chat versions, and GPT-4 Turbo3 (Achiam et al., 2023) as the exam-taker models. The prompts for the exam-taker models contain five few-shot examples of (question, answer) pairs from the TriviaQA training set. The prompts for the instruction-tuned models additionally include a command signaling the model to answer the given question in a succinct manner similar to the provided examples. The prompts are provided in Appendix C. Judge models To get a comprehensive view of the strengths and weaknesses of judge models across different model sizes and architectures, we use instruction-tuned versions of Llama-2 (Touvron et al., 2023) in 7B, 13B, and 70B sizes, Llama-3 (AI@Meta, 2024) in 8B and 70B sizes, Mistral 7B (Jiang et al., 2023), GPT-4 Turbo (Achiam et al., 2023), Gemma 2B (Gemma Team et al., 2024), and JudgeLM 7B (Zhu et al., 2023) as judges. The judges are instructed to respond with only a single word, “correct” or “incorrect”. The prompts can be found in Appendix D. An overview of al exam-taker models and judge models is shown in Table 1. For ease of reading, the judge models are depicted in a different font than the exam-taker models. Baselines As baselines, we use two commonly used lexical evaluation techniques – exact match (EM) and contains match (contains). For EM, a response is considered correct if the response exactly matches one of the reference answers for the given question. For contains, an answer is considered correct if at least one of the reference answers is a sub-string of the response string. Both EM and contains match are computed in a case-insensitive manner.",
            10,
            0.5,
            0.5,
            (True, "Document content passes checks."),
        ),
        (
            "GPT-4 GPT-4 GPT-4 GPT-4 GPT-4 63.25 75.00 85.0 56.7 57.50 72.0 72.5 52.75 92.25",
            10,
            0.3,
            0.5,
            (False, "number_ratio=0.6428571428571429 > threshold=0.3"),
        ),
        (
            "10 80 100 0 100 40 60 1 No Agreement 80 10 100Percentage Agreement 20 1 100Cohen's Kappa 100 10 0 (a) (b)",
            10,
            0.3,
            0.5,
            (False, "number_ratio=0.6521739130434783 > threshold=0.3"),
        ),
        (
            "Mistral 7B Mistral 7B 123456789Rank Mistral 7B Mistral 7B 67.75 75.00 85.25 64.55 68.75 77.50 74.50 68.50 92.75",
            10,
            0.3,
            0.5,
            (False, "number_ratio=0.5 > threshold=0.3"),
        ),
    ],
)
def test_check_content_is_useful(
    content: str,
    min_word_count: int,
    max_number_ratio: float,
    information_density_ratio: float,
    expected: Tuple[bool, str],
) -> None:
    assert (
        check_content_is_useful(
            document_content=content,
            min_word_count=min_word_count,
            max_number_ratio=max_number_ratio,
            information_density_ratio=information_density_ratio,
        )
        == expected
    )


@pytest.mark.parametrize(
    "chunk,expected",
    [
        ("", ""),
        (
            """4 Results In this section we discuss our main results, primarily focusing on the relationship between evaluations by various judge models and human evaluations (§ 4.1), and how that impacts their usability (§ 4.2). To do so, we evaluate their alignment with human judgment and assess how differently they rank the nine exam-taker models compared to humans. In Section 5, we further analyse their precision and recall to further investigate the types of errors that can be made by various judge models. Details about compute requirements and others costs for experiments are given in Appendix G. 4 Results In this section we discuss our main results, primarily focusing on the relationship between evaluations by various judge models and human evaluations (§ 4.1), and how that impacts their usability (§ 4.2). To do so, we evaluate their alignment with human judgment and assess how differently they rank the nine exam-taker models compared to humans. In Section 5, we further analyse their precision and recall to further investigate the types of errors that can be made by various judge models. Details about compute requirements and others costs for experiments are given in Appendix G.""",
            """4 Results In this section we discuss our main results, primarily focusing on the relationship between evaluations by various judge models and human evaluations (§ 4.1), and how that impacts their usability (§ 4.2). To do so, we evaluate their alignment with human judgment and assess how differently they rank the nine exam-taker models compared to humans. In Section 5, we further analyse their precision and recall to further investigate the types of errors that can be made by various judge models. Details about compute requirements and others costs for experiments are given in Appendix G.""",
        ),
    ],
)
def test_deduplicate_chunk(chunk: str, expected: str) -> None:
    assert (
        deduplicate_chunk(
            chunk=chunk,
        )
        == expected
    )
