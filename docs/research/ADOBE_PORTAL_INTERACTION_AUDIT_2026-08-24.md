# Adobe Contributor Portal Interaction Audit

**Date:** 2026-08-24

## Verified authenticated portal state

The authenticated Contributor dashboard redirects to the uploaded-files interface at `/en/uploads?upload=1`. The account currently has no portfolio items.

## Verified upload controls

The uploaded-files page exposes the following relevant controls:

| Portal control | Observed purpose | Workflow use |
|---|---|---|
| `Browse` | Opens file selector for upload | User selects a batch of prepared JPEG masters. |
| Upload drop zone | Accepts drag-and-drop files | Optional desktop alternative; not required for Android workflow. |
| `Upload CSV` | Uploads metadata CSV for uploaded files | User selects the prepared StockForge CSV after JPEG upload. |
| `Submit 0 files` | Submission action; disabled with no files | Must remain explicit user-confirmed action. |
| `New` | Lists uploaded files awaiting metadata/submission | Verification screen for batch preparation. |

The upload page shows content types including `IMAGES (JPEG FILES)` and a dedicated `Upload CSV` control. This confirms the official batch approach can reduce metadata work to a prepared master-file selection plus a prepared CSV selection, followed by review and explicit submit confirmation.

## Guardrails

No files were uploaded, metadata was changed, or submit action was performed during this audit. The Contributor Portal is authenticated but provides no contributor upload API; it must remain a portal-mediated workflow.

## CSV modal re-check

On 2026-08-24, the authenticated `Upload CSV` modal was opened against an actual uploaded JPEG. The portal modal states that column names must match the English sample, rows represent recently uploaded assets, and values other than Filename are optional. In the live modal, title limit is displayed as 200 characters, keywords as maximum 49, and the modal shows a larger 20,000-row / 20 MB limit than the previously extracted Help Center page. The live modal is the relevant behavioral contract for portal interaction. The uploaded file currently has original filename `192ff467-92c8-4bed-b352-e9bc03a75696.jpg`; a matching CSV row must use this exact filename.

## First controlled submission attempt: operational findings

The Adobe portal's CSV file input advertised `accept="text/csv"`. On the user's Android device, the native picker displayed the generated CSV but made it unavailable for selection, despite the `.csv` extension and valid contents. The browser-side input accepted the same UTF-8 CSV when uploaded from a compatible file source, and Adobe confirmed that the data was applied to the matching uploaded asset.

The portal automatically placed the asset into its submission selection after metadata save. StockForge must explicitly check the `Include in submission` state before any submit confirmation and deselect it whenever the user has not authorized submission.

The disabled Submit control exposed the portal state `submissionEligibilityDisabledReason: PAYMENT_PROVIDER_NOT_CONFIGURED`. The account had validated tax information but no payout provider. After the user configured PayPal, the portal enabled `Submit 1 file`.

On 2026-08-24, with explicit user confirmation, one reviewed GenAI asset (`192ff467-92c8-4bed-b352-e9bc03a75696.jpg`) was selected and the enabled Submit control was activated. The portal redirected to the post-submission reminder/review paths. The currently rendered In Review list had not populated yet at the time of immediate verification; it should be treated as a post-submission pending-state observation, not as approval or rejection.
