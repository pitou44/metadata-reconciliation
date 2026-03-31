<div align="center">

# Automating Metadata Reconciliation for the GW Visual Resources Slide Collection Using Agentic AI

**Thomas Gailis**

*Faculty Mentor: Paul Reuther, Visual Resources Coordinator, Corcoran Art History Program*

</div>

---

## Research Problem & Significance

Over the past two decades, university art history programs have digitized their physical 35mm slide collections to create searchable digital repositories. At GW, the Visual Resources Center (VRC) in the Corcoran Art History Program has digitized over **100,000 slide images**. But digitization alone does not make a collection usable. The critical problem is **metadata reconciliation** — linking each image to the catalog record that contains its artist, title, date, medium and other descriptive information.

Each physical slide has a handwritten or typed alphanumeric code on its mount that acts as a key to a structured metadata database. Matching images to their codes should be straightforward, but it is not. The slides were scanned in bulk onto multi-slide PDF sheets, and the scan order does not match the image file order. Many PDFs are black and white, rendering slide contents as dark rectangles with no visual information. The only usable identifiers are the codes on the slide mounts, which must be read from noisy, degraded scans. For over a decade, teams of 2–3 student workers have manually matched roughly **10,000 images**. At that pace, finishing the remaining **50,000+ unmatched items** would take decades. This is not unique to GW — the Visual Resources Association has documented the widespread difficulty institutions face migrating legacy slide collections to usable digital formats, and researchers have identified incomplete metadata as a persistent barrier to collection accessibility (Baca et al., 2006; Bentkowska-Kafel et al., 2012).

Recent advances in vision-language models (Liu et al., 2023; Bai et al., 2023) and large language models for record linkage tasks (Narayan et al., 2022) suggest a computational approach is now viable, but coordinated AI systems have not yet been applied to cultural heritage metadata reconciliation. **This project fills that gap.**

---

## Methodology

### Stage 1 — PDF Segmentation & OCR
Each scanned PDF sheet (~150 slide mounts) is programmatically divided into individual bounding boxes. A vision-language model (VLM) performs OCR on each segment to extract the alphanumeric code. A VLM is used because conventional OCR software cannot reliably read the mix of handwritten and typed text on these degraded scans.

### Stage 2 — Code Validation
Extracted codes are checked against the metadata database. Since OCR frequently produces character-level errors, a fuzzy-matching routine tests plausible substitutions (`"0"` for `"O"`, `"1"` for `"l"`) to find valid entries. Artist attributions in image filenames provide additional validation.

### Stage 3 — Image Feature Extraction
A separate VLM generates structured natural-language descriptions of each image covering art style, subject matter, composition, and medium, saved as JSON records.

### Stage 4 — LLM-Based Matching
Extracted codes with their metadata and image descriptions are fed into a large language model, which cross-references all available information to produce image-to-code matches. The system returns only high-confidence matches, prioritizing **precision over recall**. Preliminary testing on a small subset suggests a match rate of **40–60%** at over **98% accuracy**.

---

## Implications & Limitations

This project targets a minimum of **20,000 successful matches** — more than double the output of a decade of manual work. The pipeline will be **open-sourced on GitHub** with full documentation, providing a replicable toolkit for other institutions. A Solution Architecture report will ensure GW faculty can maintain the system after the project period. Results will be presented at the **GW Undergraduate Research Showcase**.

The primary limitation is that the system intentionally returns only high-confidence matches, so some images will remain unmatched. OCR performance may also vary on severely degraded slides. This project processes institutional archival data under the faculty mentor's supervision, involves no human subjects, and requires no IRB review.
