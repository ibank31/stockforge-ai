# Adobe Stock Contributor Upload Automation — Official Source Notes

**Research date:** 2026-08-24

## Official findings

Adobe's Contributor upload guidance states that contributors upload through the Contributor Portal, then add required metadata and releases before submitting for moderation. Photos require JPEG and at least 4 MP; GenAI must be selected during upload. The portal requires title, keywords, and categories. Source: [Contributor content upload guidelines](https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html).

Adobe supports a portal-mediated CSV workflow after corresponding assets have already been uploaded. A CSV can apply titles, keywords, categories, and releases to uploaded files, up to 5,000 rows. Filename matching must be exact, including extension and case. Source: [Upload a CSV file to Adobe Stock](https://helpx.adobe.com/stock/contributor/manage-your-portfolio/upload-csv-file.html).

Official Adobe Stock API documentation states that the API does **not** support Stock Contributor use cases: there is no contributor API to upload new Stock content, obtain contributor sales data, see top sellers, or get creation dates. These actions must occur in the Contributor Portal. The public Stock API is for enterprise/approved search, licensing, and related buyer workflows—not contributor upload. Source: [Adobe Stock API getting started](https://developer.adobe.com/stock/docs/getting-started/).

## Design consequence

StockForge can safely automate the deterministic offline portions: validate a review-approved master, create an Adobe-compatible metadata CSV with exact filename matching, save an upload manifest, and open/navigate the Contributor Portal. It can also assist with form field entry in a logged-in browser session after user authorization. It must not claim an official contributor upload API exists, and it must ask the user for confirmation immediately before submission/publish because that action sends content to the marketplace.

## Recommended controlled workflow

1. User marks a package as visually reviewed and marketplace-approved in StockForge.
2. Termux creates `adobe-upload/` containing the master JPEG, metadata CSV, per-asset declaration checklist, and manifest.
3. User invokes a portal-assist command that opens the Contributor Portal and uploads/prepares files; login and CAPTCHA remain user-controlled.
4. StockForge fills metadata only from the reviewed manifest/CSV and flags GenAI declaration/category for confirmation.
5. User confirms each final marketplace submit action explicitly. No automatic publish.

## Sources

1. https://helpx.adobe.com/stock/contributor/content-policies-guidelines/content-policies/content-upload-guidelines.html
2. https://helpx.adobe.com/stock/contributor/manage-your-portfolio/upload-csv-file.html
3. https://helpx.adobe.com/stock/contributor/manage-your-portfolio/edit-content.html
4. https://developer.adobe.com/stock/docs/getting-started/

## CSV schema and GenAI declaration findings

Adobe’s current CSV requirements specify a UTF-8 comma-separated `.csv` of at most 5,000 rows and 1 MB. The exact official template headers must be retained. Each row requires `Filename`, `Title`, and `Keywords`; `Category` and `Releases` are optional. Filename must match the uploaded file exactly and is limited to 30 characters; titles are limited to 70 characters; keyword lists are limited to 50 items and must be ordered by importance. Sources: [CSV requirements](https://helpx.adobe.com/stock/contributor/manage-your-portfolio/csv-requirements-content.html) and [Create a CSV file](https://helpx.adobe.com/stock/contributor/manage-your-portfolio/create-csv-file.html).

For GenAI content, Adobe requires the `Created using generative AI tools` checkbox at submit time. The `People and Property are fictional` checkbox is required only when fictional people or property appear; it can remain unchecked when no recognizable people/property are depicted. The checkbox state is not a listed CSV column, so StockForge must keep an explicit per-asset declaration manifest and require portal confirmation instead of pretending CSV applied it. Source: [Generative AI content guidelines](https://helpx.adobe.com/stock/contributor/submit-your-content/submit-generative-ai-content/generative-ai-content-guidelines.html).

## Automation boundary

The shortest safe workflow is: one Termux command creates a batch directory with renamed masters and official-schema CSV; the user opens the already-authenticated Adobe Uploaded Files page, chooses all JPEGs at once, chooses the CSV once, checks the GenAI declaration on the selected batch, and confirms the submit button. This avoids per-file metadata typing but does not falsely claim portal upload or final submission is API-automated.


## Android CSV selection compatibility investigation

Adobe's live portal input requested the strict MIME type `text/csv`. RFC 4180 formally registers `text/csv` for CSV files. Android's Storage Access Framework filters the system picker using the MIME type advertised by the calling app and the selected documents provider; a file can therefore be visible but unavailable when a provider reports an alias or generic MIME type rather than exactly `text/csv`.

The direct shared-storage CSV created by Termux was unavailable in the user's Android picker despite valid content and extension. The practical candidate workaround is to place the same exact CSV in a documents provider that advertises it as `text/csv`, such as a cloud-storage provider. This must be tested in the user's Android/Chrome picker. Changing CSV byte content alone cannot reliably override the MIME type reported by an Android documents provider.

Sources: Android Storage Access Framework documentation and RFC 4180.
