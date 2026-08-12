# Day 14 — Reflection

## Evaluation Report & Failure Analysis

Dùng kết quả thật trong `artifacts/benchmark_results.json` và kiểm tra lại
answer/context trace trong `artifacts/actual_answers.json` trước khi kết luận.

---

## 1. Benchmark Results Summary

**Overall pass rate:** 85.0%

| Metric | Average | Min | Max | Nhận xét |
|---|---:|---:|---:|---|
| Context Recall | 0.92 | 0.0 | 1.0 | Retrieval hoạt động khá tốt, nhưng thỉnh thoảng sót context chứa exception. |
| Context Precision | 0.88 | 0.0 | 1.0 | Top K thường chứa đúng chunk, nhưng rank chưa tối ưu. |
| Faithfulness | 0.85 | 0.0 | 1.0 | Model đôi khi suy diễn thêm thông tin không có trong context. |
| Relevance | 0.95 | 0.0 | 1.0 | Câu trả lời nhìn chung rất sát với câu hỏi. |
| Completeness | 0.80 | 0.0 | 1.0 | Hay bị sót các điều kiện ngoại lệ (exceptions) ở các câu hỏi Medium/Hard. |
| Overall Score | 0.87 | 0.0 | 1.0 | Đạt mức Good, cần cải thiện khả năng bám sát rule phức tạp. |

**Score interpretation**

- Metrics/cases ở mức Good (0.8–1.0): 17/20
- Metrics/cases ở mức Needs Work (0.6–0.8): 1/20
- Metrics/cases ở mức Significant Issues (<0.6): 2/20

**Failure type distribution**

| Failure Type | Count | Percentage |
|---|---:|---:|
| hallucination | 1 | 33% |
| irrelevant | 1 | 33% |
| incomplete | 1 | 33% |
| off_topic | 0 | 0% |
| refusal | 0 | 0% |

**Chẩn đoán tổng quan:** Vấn đề chính nằm ở retrieval, generation hay cả hai?
Dùng ít nhất hai metrics để bảo vệ kết luận.

> *Câu trả lời:*
> Vấn đề nằm ở cả hai, nhưng Generation (LLM Reasoning) là chủ yếu. Context Recall (0.92) khá cao chứng tỏ bằng chứng hầu như được cung cấp đủ. Tuy nhiên Completeness (0.80) thấp hơn, cho thấy LLM có xu hướng tóm tắt quá mức và bỏ sót các tiểu tiết quan trọng (ví dụ như ngoại lệ của chính sách). Ngoài ra, Faithfulness thỉnh thoảng rớt xuống 0 do hallucination khi luật quá phức tạp.

---

## 2. Top 3 Worst Failures — 5 Whys

Phân loại failure trước khi đề xuất fix. Với mỗi case, kiểm tra cả gold evidence
và retrieved chunks; không suy luận chỉ từ một score.

### Failure 1

**ID và question:**

> *Điền:*

**Expected answer:**

> *Điền:*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:** Retriever lấy đúng/thiếu/thừa chunks nào?

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | |
| Why 1 | Tại sao symptom xảy ra? | |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | |
| Why 5 | Root cause có thể hành động được là gì? | |

**Root cause từ `find_root_cause()`:**

> *Paste output:*

**Bạn đồng ý hay không? Dẫn evidence từ trace:**

> *Câu trả lời:*

**Proposed fix cụ thể:**

> *Câu trả lời:*

### Failure 2

**ID và question:**

> *Điền:*

**Expected answer:**

> *Điền:*

**Actual answer:**

> *Điền:*

**Scores:** Context Recall: ____ | Context Precision: ____ | Faithfulness: ____ |
Relevance: ____ | Completeness: ____ | Overall: ____

**Evidence inspection:**

> *Câu trả lời:*

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | |
| Why 1 | Tại sao symptom xảy ra? | |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | |
| Why 5 | Root cause có thể hành động được là gì? | |

**Root cause và proposed fix:**

> *Câu trả lời:*

### Failure 3

**ID và question:**

> *Điền:* H04 - My PulsePhone X has liquid damage but is still within the 24-month period. Is it covered by the warranty?

**Expected answer:**

> *Điền:* No, the warranty excludes liquid exposure, so it is not covered.

**Actual answer:**

> *Điền:* I am sorry, I couldn't find information about liquid damage. However, your PulsePhone X has a 24-month limited warranty.

**Scores:** Context Recall: 0.0 | Context Precision: 0.0 | Faithfulness: 1.0 |
Relevance: 0.0 | Completeness: 0.0 | Overall: 0.33

**Evidence inspection:**

> *Câu trả lời:* Retriever KHÔNG lấy được chunk chứa câu "The warranty excludes loss, theft... liquid exposure...".

| Level | Question | Answer |
|---|---|---|
| Symptom | Vấn đề quan sát được là gì? | Model báo không tìm thấy thông tin và không trả lời đúng câu hỏi. |
| Why 1 | Tại sao symptom xảy ra? | Chunk chứa list các exceptions của warranty không được retrieve vào top K. |
| Why 2 | Tại sao nguyên nhân trên xảy ra? | Thuật toán vector similarity ưu tiên các chunk nói về "PulsePhone X" và "24-month warranty" hơn là chunk liệt kê exclusion (vì nó không chứa tên điện thoại). |
| Why 3 | Tại sao vấn đề đó chưa được ngăn chặn? | Semantic search thuần túy thường gặp khó khăn với các keyword như "liquid damage" nếu văn bản dùng "liquid exposure". |
| Why 4 | Tại sao cơ chế hiện tại chưa phát hiện hoặc xử lý được? | Hệ thống chỉ dùng ChromaDB embeddings cơ bản mà không có BM25 (lexical) hoặc Reranker. |
| Why 5 | Root cause có thể hành động được là gì? | Retriever strategy (chỉ dùng Dense Retrieval) không đủ mạnh để xử lý keyword mismatch và policy details. |

**Root cause và proposed fix:**

> *Câu trả lời:* Root cause: Retrieval Failure (Missing context). Fix: Implement Hybrid Search (BM25 + Vector) and a Cross-Encoder Reranker to improve retrieval of specific policy exclusions.

---

## 3. Failure Clustering

Một root cause có thể tạo ra nhiều failures. Nhóm theo nguyên nhân có thể sửa,
không chỉ nhóm theo tên metric.

| Cluster | Root Cause | Failure IDs | Priority |
|---|---|---|---|
| 1 | | | High/Medium/Low |
| 2 | | | |
| 3 | | | |

**Nếu chỉ được sửa một cluster, bạn chọn cluster nào và vì sao?**

> *Câu trả lời:*

---

## 4. Improvement Log

Paste output của `generate_improvement_log()`:

```text
[paste Markdown table here]
```

**Ba improvement suggestions ưu tiên**

1. ____
2. ____
3. ____

Với mỗi suggestion, nêu metric dự kiến thay đổi và cách đo lại.

| Suggestion | Target metric | Verification method |
|---|---|---|
| | | |
| | | |
| | | |

---

## 5. Regression Testing Strategy

**Câu 1: Khi nào chạy `run_regression()` trong production workflow?**

> *Câu trả lời:*

**Câu 2: Threshold drop 0.05 có phù hợp OrbitTech Customer Support không? Vì sao?**

> *Câu trả lời:*

**Câu 3: Metric/failure nào phải block deployment, metric nào chỉ alert?**

> *Câu trả lời:*

**Câu 4: Điền evaluation stages vào flow.**

```text
Code/prompt/retrieval change → [________] → [________] → [________] → Deploy
```

> *Giải thích:*

---

## 6. Continuous Improvement Loop

```text
Evaluate → Analyze → Improve → Augment benchmark → Repeat
```

| Priority | Action | Metric dự kiến cải thiện | Expected impact |
|---:|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |

**Hai hoặc ba failure cases nào cần thêm vào benchmark ở vòng tiếp theo?**

> *Câu trả lời:*

---

## 7. Final Reflection

**Điều gì trong kết quả benchmark trái với dự đoán ban đầu của bạn?**

> *Câu trả lời:*

**Word-overlap heuristics trong lab có giới hạn gì? Nếu đưa hệ thống vào
production, bạn sẽ thay hoặc bổ sung metric nào?**

> *Câu trả lời:*
