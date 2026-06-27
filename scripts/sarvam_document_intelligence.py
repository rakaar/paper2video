import argparse
import os
import time
import zipfile
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader, PdfWriter
from sarvamai import SarvamAI


MAX_PAGES_PER_JOB = 10


def split_pdf(pdf_path: Path, split_dir: Path) -> list[Path]:
    reader = PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    split_dir.mkdir(parents=True, exist_ok=True)

    if total_pages <= MAX_PAGES_PER_JOB:
        return [pdf_path]

    parts = []
    for start in range(0, total_pages, MAX_PAGES_PER_JOB):
        end = min(start + MAX_PAGES_PER_JOB, total_pages)
        writer = PdfWriter()
        for page_index in range(start, end):
            writer.add_page(reader.pages[page_index])

        part_path = split_dir / f"{pdf_path.stem}_pages_{start + 1:02d}_{end:02d}.pdf"
        with part_path.open("wb") as f:
            writer.write(f)
        parts.append(part_path)

    return parts


def run_job(client: SarvamAI, pdf_path: Path, out_root: Path, language: str, output_format: str) -> None:
    out_dir = out_root / pdf_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "sarvam_output.zip"

    job = client.document_intelligence.create_job(
        language=language,
        output_format=output_format,
    )
    print(f"job: {job.job_id} {pdf_path.name}")
    job.upload_file(str(pdf_path))
    job.start()
    final_status = job.wait_until_complete(poll_interval=5, timeout=600)
    print(f"final: {final_status.job_state}")
    print(f"metrics: {job.get_page_metrics()}")

    job.download_output(str(out_file))
    print(f"downloaded: {out_file}")

    try:
        with zipfile.ZipFile(out_file) as zf:
            zf.extractall(out_dir / "unzipped")
            print(f"unzipped: {out_dir / 'unzipped'}")
    except zipfile.BadZipFile:
        print("download was not a zip file")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Sarvam Document Intelligence on a PDF.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, default=Path("data/outputs/sarvam"))
    parser.add_argument("--split-dir", type=Path, default=Path("data/raw/splits"))
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--language", default="en-IN")
    parser.add_argument("--format", default="md", choices=["html", "md", "json"])
    args = parser.parse_args()

    if args.env_file:
        load_dotenv(args.env_file)
    else:
        load_dotenv()

    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is not set.")

    parts = split_pdf(args.pdf, args.split_dir)
    print(f"processing {len(parts)} file(s)")

    client = SarvamAI(api_subscription_key=api_key)
    for part in parts:
        started = time.time()
        run_job(client, part, args.out, args.language, args.format)
        print(f"elapsed_seconds: {time.time() - started:.1f}")


if __name__ == "__main__":
    main()
