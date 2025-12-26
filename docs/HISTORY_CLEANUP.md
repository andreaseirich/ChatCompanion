# Git History Cleanup Guide

**Date**: 2025-01-27  
**Purpose**: Guide for cleaning Git history if sensitive files were previously committed.

---

## Current Status

The following internal files were found in Git history:
- `master_prompt.txt` - Internal Cursor AI master prompt
- `docs/CHECKPOINTS.md` - Internal project tracking
- `docs/QUALITY_GATES.md` - Internal quality checks
- `docs/BENCHMARKS.md` - Internal benchmark analysis
- `docs/DEVPOST_CHECKLIST.md` - Internal submission checklist
- `docs/REPO_AUDIT.md` - Previous audit document

These files have been removed from the current repository and are now in `.gitignore`, but they may still exist in Git history.

---

## When to Clean History

**Clean history if**:
- Internal prompts contain sensitive development strategies or proprietary information
- Internal documents contain personal notes or private planning details
- Files contain information that should never be publicly visible

**History cleanup is NOT necessary if**:
- Files only contain general development notes
- Information is not sensitive or proprietary
- Repository is private or access is controlled

---

## How to Clean Git History

### Option 1: Using git filter-repo (Recommended)

**Prerequisites**:
```bash
pip install git-filter-repo
```

**Remove specific files from entire history**:
```bash
# Create a backup first!
git clone --mirror <repository-url> backup-repo.git

# Remove files from entire history
git filter-repo --path master_prompt.txt --invert-paths
git filter-repo --path docs/CHECKPOINTS.md --invert-paths
git filter-repo --path docs/QUALITY_GATES.md --invert-paths
git filter-repo --path docs/BENCHMARKS.md --invert-paths
git filter-repo --path docs/DEVPOST_CHECKLIST.md --invert-paths
git filter-repo --path docs/REPO_AUDIT.md --invert-paths

# Or remove all at once
git filter-repo \
  --path master_prompt.txt \
  --path docs/CHECKPOINTS.md \
  --path docs/QUALITY_GATES.md \
  --path docs/BENCHMARKS.md \
  --path docs/DEVPOST_CHECKLIST.md \
  --path docs/REPO_AUDIT.md \
  --invert-paths
```

**Force push to remote** (⚠️ **WARNING**: This rewrites history):
```bash
git push origin --force --all
git push origin --force --tags
```

### Option 2: Using BFG Repo-Cleaner

**Prerequisites**:
- Download BFG from https://rtyley.github.io/bfg-repo-cleaner/

**Remove files**:
```bash
# Create a backup first!
git clone --mirror <repository-url> backup-repo.git

# Remove files
java -jar bfg.jar --delete-files master_prompt.txt
java -jar bfg.jar --delete-files docs/CHECKPOINTS.md
# ... repeat for other files

# Clean up
cd backup-repo.git
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

---

## Important Warnings

⚠️ **History Rewriting is Destructive**:
- All commit hashes will change
- Collaborators must re-clone the repository
- Any forks or clones will have diverged history
- This cannot be undone easily

⚠️ **Before Cleaning History**:
1. **Backup the repository**: `git clone --mirror <repo-url> backup.git`
2. **Notify all collaborators**: They must re-clone after cleanup
3. **Check if repository is public**: Public repos may have been cloned by others
4. **Consider if cleanup is necessary**: If files aren't truly sensitive, cleanup may not be needed

---

## Verification

After cleanup, verify files are removed:
```bash
# Check if files still exist in history
git log --all --full-history --oneline -- "master_prompt.txt"
# Should return no results

# Verify current state
git ls-files | grep -E "(master_prompt|CHECKPOINTS|QUALITY_GATES|BENCHMARKS|DEVPOST_CHECKLIST|REPO_AUDIT)"
# Should return no results
```

---

## Current Repository Status

✅ **Files are excluded from future commits**:
- All internal files are in `.gitignore`
- Repository hygiene checker prevents accidental commits
- GitHub Actions workflow runs hygiene checks automatically

✅ **Files are removed from working tree**:
- All internal files moved to `.local/` (gitignored)
- Current repository state is clean

⚠️ **Files may still exist in Git history**:
- Previous commits may contain these files
- History cleanup is optional and depends on sensitivity assessment

---

## Decision Matrix

| Scenario | Action |
|----------|--------|
| Repository is private, files not sensitive | ✅ No cleanup needed |
| Repository is public, files contain proprietary info | ⚠️ Clean history recommended |
| Repository is public, files are general dev notes | ✅ No cleanup needed (already removed) |
| Repository will be made public, files are sensitive | ⚠️ Clean history before making public |

---

**Note**: This document is for reference only. History cleanup should be performed carefully and only if necessary.

