import os
import re
import json
import base64
import argparse
from pathlib import Path

from dotenv import load_dotenv
from mistralai import Mistral
from pypdf import PdfReader
from tqdm import tqdm
import tenacity


def get_client(env_file: Path | None = None):
    """Load Mistral API key from environment and construct a client."""
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable is not set.")
    return Mistral(api_key=api_key)


def parse_pages(page_ranges: str | None, pdf_path: Path) -> list[int] | None:
    """Convert human page ranges like 1-3,7-9 into Mistral's zero-based pages."""
    if not page_ranges:
        return None

    total_pages = len(PdfReader(str(pdf_path)).pages)
    pages = set()
    for part in page_ranges.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text) if start_text else 1
            end = int(end_text) if end_text else total_pages
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid page range {part!r} for {total_pages} pages.")
            pages.update(range(start - 1, end))
        else:
            page = int(part)
            if page < 1 or page > total_pages:
                raise ValueError(f"Invalid page {page} for {total_pages} pages.")
            pages.add(page - 1)

    return sorted(pages)


@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=2, max=30),
    stop=tenacity.stop_after_attempt(5),
)
def ocr_pdf(client: Mistral, pdf_b64: str, pages=None, include_images: bool = True):
    """Send base64 PDF to Mistral OCR and request images alongside OCR result."""
    return client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{pdf_b64}",
        },
        pages=pages,
        include_image_base64=include_images,
    )


def run(pdf_path: Path, out_root: Path, page_ranges=None, env_file: Path | None = None):
    """End-to-end: encode PDF, call OCR, and save markdown/json/images per page."""
    client = get_client(env_file)

    pdf_b64 = base64.b64encode(pdf_path.read_bytes()).decode()
    pages = parse_pages(page_ranges, pdf_path)
    scope = "whole PDF" if pages is None else f"{len(pages)} selected page(s)"
    print(f"Processing {pdf_path.name} with Mistral OCR ({scope})...")
    response = ocr_pdf(client, pdf_b64, pages)

    out_dir = out_root / pdf_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    md_dir = out_dir / "markdown"
    md_dir.mkdir(exist_ok=True)
    json_dir = out_dir / "json"
    json_dir.mkdir(exist_ok=True)
    img_dir = out_dir / "images"
    img_dir.mkdir(exist_ok=True)

    for p in tqdm(response.pages, desc=f"{pdf_path.name}"):
        # 1) Extract images and build mapping from image id -> relative path from markdown dir
        img_map = {}
        for img in getattr(p, "images", []) or []:
            img_id = getattr(img, "id", None)
            img_b64 = getattr(img, "image_base64", None)
            if not (img_id and img_b64):
                continue

            # If image_base64 is a data URI, strip the prefix
            if "," in img_b64:
                img_b64 = img_b64.split(",", 1)[1]

            img_bytes = base64.b64decode(img_b64)

            img_filename = f"{img_id}"
            img_path = img_dir / img_filename
            with open(img_path, "wb") as out_f:
                out_f.write(img_bytes)

            rel_path = os.path.relpath(img_path, md_dir)
            img_map[img_id] = rel_path

        # 2) Rewrite Markdown image links to point to saved images
        md = getattr(p, "markdown", "")

        def repl(match):
            alt, img_id = match.groups()
            return f"![{alt}]({img_map.get(img_id, img_id)})"

        md_fixed = re.sub(r"!\[([^\]]*)\]\((img-[^\)]+)\)", repl, md)

        # 3) Save Markdown
        md_path = md_dir / f"{pdf_path.stem}_page_{p.index + 1:02d}.md"
        md_path.write_text(md_fixed, encoding="utf-8")

        # 4) Save JSON metadata for the page
        json_path = json_dir / f"{pdf_path.stem}_page_{p.index + 1:02d}_response.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"pages": [p.model_dump()]}, f, indent=2, ensure_ascii=False)

    print(f"Done: {pdf_path.name} ({len(response.pages)} pages)")


def main():
    parser = argparse.ArgumentParser(description="Bulk OCR via Mistral")
    parser.add_argument("pdfs", nargs="+", help="PDF file(s) to process")
    parser.add_argument(
        "--out", default="mistral_responses", help="Output root directory"
    )
    parser.add_argument("--pages", help="Page ranges, e.g. 1-3,7- or 5")
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional .env file containing MISTRAL_API_KEY",
    )
    args = parser.parse_args()

    out_root = Path(args.out)
    out_root.mkdir(exist_ok=True)

    for pdf in map(Path, args.pdfs):
        run(pdf, out_root, args.pages, args.env_file)


if __name__ == "__main__":
    main()
