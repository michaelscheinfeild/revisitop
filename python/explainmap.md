# Explanation of `compute_ap` Function

This document explains how the `compute_ap` function works — it computes **Average Precision (AP)**, a standard metric for ranking and retrieval systems.

---

## 🧩 Function Purpose

```python
def compute_ap(ranks, nres):
    """
    Computes average precision for given ranked indexes.
    
    Arguments
    ---------
    ranks : zero-based ranks of positive images
    nres  : number of positive images
    
    Returns
    -------
    ap    : average precision
    """
```
The function computes **Average Precision (AP)** given:
- `ranks`: indices (zero-based) where the *relevant* images appear in the ranked list.  
  Example: `[0, 3, 5]` means positives appear at ranks 0, 3, and 5.
- `nres`: total number of relevant images (e.g. `3`).

---

## 🧮 Key Idea — Average Precision (AP)

Average Precision measures the **area under the precision–recall curve (PR curve)**:

\[
AP = \sum_{k=1}^{N} P(k) \cdot \Delta R(k)
\]

Where:
- \( P(k) \): precision at cutoff \( k \)
- \( \Delta R(k) \): change in recall when the \( k \)-th relevant item is found

This implementation approximates the area using **trapezoidal integration**.

---

## 🔍 Step-by-Step Explanation

### 1. Initialization
```python
nimgranks = len(ranks)
ap = 0
recall_step = 1. / nres
```
- `nimgranks`: number of relevant items found.
- `recall_step`: how much recall increases with each positive (uniform step of `1/nres`).

---

### 2. Loop Over Relevant Items
```python
for j in np.arange(nimgranks):
    rank = ranks[j]
```
Iterates over each relevant item’s position in the ranked list.

---

### 3. Compute Precision Before and After the Item
```python
if rank == 0:
    precision_0 = 1.
else:
    precision_0 = float(j) / rank

precision_1 = float(j + 1) / (rank + 1)
```
- `precision_0`: precision just before finding the (j+1)-th relevant image.
- `precision_1`: precision just after it.

---

### 4. Integrate Using the Trapezoidal Rule
```python
ap += (precision_0 + precision_1) * recall_step / 2.
```
Computes the area under the local segment of the precision–recall curve.

---

### 5. Return Result
```python
return ap
```
Returns the **average precision** between 0 and 1.

---

## ✅ Example

```python
ranks = [0, 2, 4]
nres = 3
```
| Relevant # | Rank | Precision | Recall |
|-------------|------|------------|--------|
| 1 | 0 | 1.00 | 1/3 |
| 2 | 2 | 2/3 | 2/3 |
| 3 | 4 | 3/5 | 1.0 |

The integrated area ≈ **0.86 (AP)**.

---

## 🧠 Summary

| Concept | Meaning |
|----------|----------|
| `ranks` | Zero-based indices of relevant images |
| `nres` | Number of relevant (positive) images |
| Integration | Trapezoidal rule over precision–recall curve |
| Output | Average Precision (0–1 range) |
