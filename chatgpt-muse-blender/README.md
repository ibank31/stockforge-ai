# ChatGPT ↔ Muse: Blender 3D Collaboration

Shared workspace for collaborating on accurate 3D models of real-world objects.

## How This Works

**Muse** (me) writes modeling tasks here. **ChatGPT** reads them via these public URLs.
**Iqbal** relays ChatGPT's responses back to Muse. Renders are pushed here for ChatGPT to review.

## Workflow

1. Muse creates `tasks/NNN-<object>.md` with full spec
2. Iqbal shares the file URL with ChatGPT → ChatGPT reviews
3. Iqbal pastes ChatGPT's review to Muse
4. Muse models + renders → pushes to `renders/NNN/`
5. Iqbal shares render URLs with ChatGPT → ChatGPT proposes corrections
6. Repeat until accurate

## Directory Structure

```
tasks/      # Task specifications (one .md per object)
renders/    # Render previews per task
reviews/    # ChatGPT reviews (pasted by Iqbal via Muse)
```

## Active Tasks

| ID | Object | Status |
|----|--------|--------|
| 001 | Ballpoint pen | Awaiting ChatGPT review |
