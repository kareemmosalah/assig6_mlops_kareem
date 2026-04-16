# Assignment 6 – Gatekeeper CI/CD Pipeline

## Overview

This assignment re-engineers the GitHub Actions workflow to implement **strict conditional execution** using a "Gatekeeper" pattern, preventing expensive GPU jobs from running on broken or unauthorized code branches.

---

## Files

| File | Purpose |
|------|---------|
| `pipeline.yaml` | The main workflow file (copy to `.github/workflows/`) |
| `train_model.py` | Dummy training script simulating GPU work |
| `requirements.txt` | Python dependencies for the training job |
| `README.md` | This file |

---

## Pipeline Architecture

```
PUSH to any branch
       │
       ▼
┌─────────────┐
│  lint job   │  ← Always runs (lightweight, cheap)
│  (flake8)   │
└──────┬──────┘
       │ passes?
       ▼
  Gatekeeper checks ALL 3 conditions:
  ┌─────────────────────────────────────────────────┐
  │  1. lint job passed?            (needs: lint)   │
  │  2. branch == main?             (github.ref)    │
  │  3. commit has [run-train]?     (commit message)│
  └───────────────────┬─────────────────────────────┘
         ALL YES       │           ANY NO
            ▼          │              ▼
     ┌────────────┐    │       ┌──────────────┐
     │ train job  │    │       │ train job    │
     │  RUNS ✅   │    │       │  SKIPPED ⏭  │
     └─────┬──────┘    │       └──────────────┘
           │
    ┌──────┴──────┐
    │  Success?   │
    │  No → upload│  if: failure()
    │  error_logs │  → uploads error_logs.txt artifact
    └──────┬──────┘
           │ always()
           ▼
   "Cleaning up temporary cloud volumes..."
```

---

## The Three Gatekeeper Conditions

### 1. Linter Must Pass (`needs: lint`)
The `train` job declares `needs: lint`, which means GitHub Actions will only attempt to schedule it after the `lint` job completes successfully. If flake8 fails, the train job is **skipped automatically**.

### 2. Branch Must Be `main` (`github.ref == 'refs/heads/main'`)
The `if:` condition on the train job checks the ref. Any push from a feature branch (`dev`, `hotfix`, etc.) will cause the train job to be **skipped**.

### 3. Commit Message Must Contain `[run-train]`
Developers must **opt-in** to expensive training runs by including `[run-train]` in their commit message. Without it, the job is **skipped** — saving GPU compute costs.

---

## Failure Handling

```yaml
- name: Upload error logs on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: error-logs
    path: error_logs.txt
```

If training crashes, the pipeline captures stdout/stderr into `error_logs.txt` and uploads it as a GitHub Actions Artifact. Developers can download it directly from the Actions UI without re-running the expensive GPU job.

---

## Cleanup Step (always runs)

```yaml
- name: Cleanup cloud volumes
  if: always()
  run: echo "Cleaning up temporary cloud volumes..."
```

This step executes **regardless of success or failure**, ensuring cloud volumes and temporary resources are always released.

---

## How to Run / Test

### Step 1 – Deploy the workflow
```bash
cp assig6_mlops/pipeline.yaml .github/workflows/pipeline.yaml
git add .github/workflows/pipeline.yaml assig6_mlops/
```

### Step 2 – Test a SKIPPED train job (no `[run-train]` in message)
```bash
git commit -m "refactor: clean up code"
git push origin main
# → lint runs ✅, train is SKIPPED ⏭ (no [run-train] tag)
```

### Step 3 – Test a RUNNING train job
```bash
git commit -m "feat: improve model accuracy [run-train]"
git push origin main
# → lint runs ✅, train RUNS 🚀
```

### Step 4 – Test branch protection
```bash
git checkout -b dev
git commit -m "wip: experiment [run-train]"
git push origin dev
# → lint runs ✅, train is SKIPPED ⏭ (not on main)
```

### Step 5 – Screenshot requirement
For the screenshot showing a **Skipped** train job:
1. Go to your GitHub repo → **Actions** tab
2. Find the run triggered by a commit **without** `[run-train]`
3. Click on it → you'll see `lint: ✅` and `train: ⏭ skipped`
4. Take a screenshot of that view
