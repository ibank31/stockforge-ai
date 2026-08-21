# Real-World Test #002

## Generation

- Resolution: 1024x1024
- Steps: 8
- GPU function time: 37.533 seconds
- Result: generated successfully

## Findings

### Passed

- Strong construction-survey concept
- Useful left-subject / right-copy-space composition
- Construction environment broadly believable
- No obvious duplicate person or catastrophic anatomy failure in the supplied review image

### Failed / review

1. **Visual stereotype:** despite explicit negative prose, the image added a blue holographic/digital-twin overlay.
2. **Semantic equipment risk:** the generated surveying instrument should not be described as a specific terrestrial laser scanner unless visually verified.
3. **Resolution:** 1024x1024 is about 1.05 MP and is not Adobe Stock submission-ready; final output needs a separate resolution/finalization path meeting the current Adobe requirements.
4. **Differentiation:** construction scanning/BIM imagery has substantial marketplace supply; the concept needs a more specific buyer workflow rather than a generic "digital twin" visual trope.

## Engineering change

The generator now applies a compact photographic realism prefix and a dedicated negative-conditioning policy. The key change is that anti-stereotype constraints are sent through the actual negative conditioning channel rather than being left only inside the user prompt.

The positive policy also reframes BIM/digital-twin/software context as invisible workflow context. This is intended to reduce the model's tendency to turn business context into holographic graphics.

This is an empirical heuristic from Test #002, not an Adobe acceptance rule. Test #003 must verify whether the change actually reduces holographic overlays without degrading useful construction detail.
