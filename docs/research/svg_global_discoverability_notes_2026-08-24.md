# Global SVG Discoverability Research — Raw Notes

**Tanggal:** 24 Agustus 2026
**Status:** Catatan riset berjalan; belum menjadi perubahan algoritma dan belum menentukan produk final.

## Adobe Stock

Adobe’s current vector metadata guidance says titles should clearly and relevantly describe the vector, keywords should be specific and inclusive, and categories should be accurate. If an uploaded vector lacks a title or embedded keywords, the Contributor Portal can suggest a title and up to 25 keywords; contributors are expected to review, edit, remove, or reorder them. Adobe states that the first 10 keywords are prioritized in search results. This supports an algorithm that ranks candidate metadata by literal visual relevance and buyer job, then requires human review; it does not support stuffing every related query into a listing.

Source: [Adobe Stock — Keywords and metadata to submit vectors](https://helpx.adobe.com/stock/contributor/content-policies-guidelines/metadata/keywords-metadata-submitting-vectors.html), last updated June 11, 2026, accessed August 24, 2026.

## Shutterstock

Shutterstock’s current contextual metadata standard says descriptions/titles, keywords, categories, and optional location information drive search and discovery. Titles/descriptions must be factual and relevant. Keywords must describe the submitted content, with a minimum of 7 and maximum of 50. Categories must be relevant, with one required and a second optional. Shutterstock also states that non-relevant metadata can cause rejection and that titles/keywords should be free of errors, spam, trademarks, and product names.

Shutterstock’s separate anti-spam guidance defines keyword spamming as overusing repeated or irrelevant terms. It gives examples where repeating the same word stem across many keyword phrases is not allowed, while a small set of relevant descriptive terms is allowed. It also says titles should be descriptive phrases rather than repeated keyword lists.

Sources: [Shutterstock — Content Publishing Standards: Contextual Metadata](https://submit.shutterstock.com/help/en/articles/10617427-content-publishing-standards-contextual-metadata), February 26, 2026, accessed August 24, 2026; [Shutterstock — How keyword and title spamming are defined](https://submit.shutterstock.com/help/en/articles/10617485-how-are-keyword-and-title-spamming-defined), July 18, 2025, accessed August 24, 2026.

## Algorithm implications

The safe market-intelligence layer should score candidate opportunities using separate dimensions: buyer-job clarity, demand signal, competition proxy, visual distinctiveness, legal/brand safety, format fit, and metadata confidence. It should not treat search position as controllable or promise top placement. It should produce a ranked decision with evidence URLs, confidence, and explicit caveats.

Metadata generation should use a literal visual inventory first, then a bounded set of buyer-job terms that are genuinely supported by the asset. The engine should deduplicate stems, reject irrelevant or trademark terms, prioritize the strongest terms first, and keep platform-specific limits separate. The same asset may require a platform-specific metadata projection; it should not blindly copy one keyword list across Adobe Stock, Shutterstock, Etsy, Freepik, or other marketplaces.

## Product-value implications

A single generic folder-upload icon can be useful but is easy to replace. To move its internal buyer-likelihood above 50% for a targeted buyer, the product likely needs a stronger reason to buy than “one ordinary glyph”: a distinctive but restrained visual system, a clearly useful state/variant relationship, an exact niche context, or packaging into a coherent set. A single icon should not be turned into a misleading bundle or duplicated variations merely to increase search coverage.

The next research phase must compare global platform buyer jobs and determine whether the best value path is a single high-utility icon, a tightly scoped micro-set, or another SVG category such as packaging/cut-ready files, editorial elements, or repeat patterns. No new generation is authorized by these notes.

## Freepik contributor guidance

Freepik’s contributor guidance says vector titles should describe the content in one English sentence, avoid undescriptive or unnecessary information, and not mention the file type. It recommends accurate, specific, user-oriented tags ordered by relevance, with a suggested sweet spot of 15–20 tags out of a maximum of 50. Freepik explicitly warns against irrelevant tags, mixing concepts, obvious file-type tags, and repeated keywords/spam. The examples distinguish what is visibly depicted from possible use cases that are not shown.

Source: [Freepik Contributor — Pro Tips on Adding Keywords to Vectors](https://contributor.freepik.com/blog/pro-tips-adding-keywords-vectors/), February 19, 2020, accessed August 24, 2026.

## Creative Market product-page guidance

Creative Market’s current product-description guidance says a title should be short, clear, specific, and focused on what the product is rather than how it feels. It discourages unnecessary punctuation, promotional language, and repeated shop/product terms. Product descriptions should explain what makes the product unique, how it can be used, its features and benefits, and compatibility; the article warns against keyword stuffing and repetition. It recommends relevant specific tags that match the actual product, a mix of common and niche tags, and clear preview images that show the product in context. Creative Market also provides AI-labeling guidance and says AI-generated products should be marked accordingly.

Source: [Creative Market — Creating High-Quality Product Description Pages](https://support.creativemarket.com/hc/en-us/articles/43335464121499-Creating-High-Quality-Product-Description-Pages-PDPs), accessed August 24, 2026.

## Etsy search guidance

Etsy’s official search guide separates query matching from ranking. Query matching considers the holistic listing, including title, tags, attributes, descriptions, first photo, and reviews. Ranking then considers factors such as relevancy, shop quality, listing quality, customer service quality, language/translation, listing engagement/conversion, recency, and shopper-specific behavior. Etsy says exact or relevant matches can improve the possibility of appearing in results, but it does not guarantee top placement. Etsy also says ads affect designated ad spaces, not organic search ordering, and that repeatedly creating or renewing listings only to obtain a temporary recency boost is not an effective strategy. Conversion and customer experience matter after the click.

Source: [Etsy Seller Handbook — How Etsy Search Works](https://www.etsy.com/seller-handbook/article/how-etsy-search-works/375461474487), August 26, 2025, accessed August 24, 2026.

## Cross-marketplace algorithm rule

The global algorithm should not search for a universal “top ranking” hack. It should build platform-specific projections from one canonical visual truth: Adobe can prioritize its first 10 keywords; Shutterstock requires relevant contextual metadata and rejects repetition/spam; Freepik favors specific English tags ordered by relevance and suggests 15–20; Creative Market values concise titles, useful descriptions, compatibility, and 5–10 relevant tags; Etsy uses holistic matching and ranking with conversion/customer-quality signals. These limits and concepts must remain separate in code.

The safe objective is to maximize **qualified discovery and buyer confidence**, not raw impressions. A product that ranks but does not communicate value can reduce conversion and is not a success. Therefore the product-value score, preview/thumbnail clarity, description/use-case fit, and platform-specific metadata score should be measured separately from search visibility.

## Product-value signal from marketplace listings

Creative Market’s live Icons category presented more than 79,000 products and surfaced paid products ranging from small themed sets to large UI libraries, including examples such as 240 vector objects, 1,500–7,000 icon bundles, and focused UI icon libraries. The page explicitly positions icons for web design, infographics, logos, and social media, and exposes filters for vector, raster, layered, and responsive properties. This is a supply signal and product-positioning signal, not proof of sales.

A live Etsy listing provides a stronger but still narrow transaction proxy: a 1,500-icon bundle offered individual SVG files, 58 themed sets, broad application contexts such as web marketing, apps, websites, presentations, promotional materials, and infographics, and displayed 984 shop sales and 15 favourites at the time accessed. It does not prove that the asset itself sold or that the same demand transfers to Adobe Stock. It does show the buyer value proposition of **coverage, consistency, separate files, and immediate reuse** more clearly than a single generic icon.

Sources: [Creative Market — Icons category](https://creativemarket.com/icons), accessed August 24, 2026; [Etsy — 1500 SVG Line with color Icons Pack](https://www.etsy.com/au/listing/1596482687/1500-svg-line-with-color-icons-pack), accessed August 24, 2026.

## Revised product-value hypothesis

To target an internal purchase-likelihood above 50% for a well-defined buyer, StockForge should not merely beautify the single folder-upload glyph. It should consider a **small, coherent micro-set** with a clear file-management workflow: upload, download, folder, file, cloud storage, sync, and archive, all sharing a single visual system. The set must be a deliberate product with separate editable SVGs, clean naming, transparent backgrounds, consistent dimensions/stroke logic, a useful preview sheet, and platform-appropriate packaging. This is a materially different product hypothesis from the single icon and must be evaluated as option 2, not smuggled into option 1 through duplicate variations.

The next buyer test should compare: (A) the current single icon; (B) a coherent six-to-eight-icon micro-set; and (C) a more distinctive niche-specific set such as file-management states for a particular workflow. The comparison should use buyer-job clarity, perceived usefulness, perceived uniqueness, file usability, preview trust, and willingness-to-buy—not search impressions alone.
