import argparse
import hashlib
import json
import math
import os
import wave
from pathlib import Path

from dotenv import load_dotenv
from sarvamai import SarvamAI
from sarvamai.play import save
import tenacity


def get_duration_seconds(audio_path: Path) -> float:
    with wave.open(str(audio_path), "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return frames / float(rate)


def public_asset_path(public_dir: Path, asset_path: Path) -> str:
    return asset_path.relative_to(public_dir).as_posix()


def scene_fingerprint(scene: dict, settings: dict) -> str:
    payload = {
        "narration": scene.get("narration", ""),
        "settings": settings,
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@tenacity.retry(
    wait=tenacity.wait_exponential(multiplier=2, max=30),
    stop=tenacity.stop_after_attempt(4),
)
def synthesize_scene(
    client: SarvamAI,
    text: str,
    language: str,
    speaker: str,
    model: str,
    sample_rate: int,
    pace: float,
):
    return client.text_to_speech.convert(
        text=text,
        target_language_code=language,
        speaker=speaker,
        model=model,
        speech_sample_rate=sample_rate,
        output_audio_codec="wav",
        pace=pace,
        enable_preprocessing=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Sarvam TTS audio files for a Remotion storyboard."
    )
    parser.add_argument("--storyboard", type=Path, default=Path("src/storyboard.json"))
    parser.add_argument(
        "--out-storyboard",
        type=Path,
        default=Path("src/storyboard.voiceover.json"),
    )
    parser.add_argument(
        "--public-dir",
        type=Path,
        default=Path("public"),
        help="Remotion public directory used by staticFile().",
    )
    parser.add_argument(
        "--out-audio",
        type=Path,
        default=Path("public/generated/nature_s41467-025-64132-4/audio"),
    )
    parser.add_argument("--env-file", type=Path, default=None)
    parser.add_argument("--language", default="en-IN")
    parser.add_argument("--speaker", default="anushka")
    parser.add_argument("--model", default="bulbul:v2")
    parser.add_argument("--sample-rate", type=int, default=22050)
    parser.add_argument("--pace", type=float, default=0.9)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument(
        "--hold-seconds",
        type=float,
        default=1.2,
        help="Extra visual time after each narration clip.",
    )
    args = parser.parse_args()

    if args.env_file:
        load_dotenv(args.env_file)
    else:
        load_dotenv()

    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key:
        raise ValueError("SARVAM_API_KEY is not set.")

    storyboard = json.loads(args.storyboard.read_text(encoding="utf-8"))
    args.out_audio.mkdir(parents=True, exist_ok=True)
    args.public_dir.mkdir(parents=True, exist_ok=True)

    client = SarvamAI(api_subscription_key=api_key)
    settings = {
        "language": args.language,
        "speaker": args.speaker,
        "model": args.model,
        "sample_rate": args.sample_rate,
        "pace": args.pace,
    }

    for index, scene in enumerate(storyboard["scenes"], start=1):
        narration = scene.get("narration", "").strip()
        if not narration:
            continue

        audio_path = args.out_audio / f"scene_{index:02d}.wav"
        metadata_path = args.out_audio / f"scene_{index:02d}.json"
        fingerprint = scene_fingerprint(scene, settings)
        can_reuse = False
        if audio_path.exists() and metadata_path.exists():
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            can_reuse = metadata.get("fingerprint") == fingerprint

        if not can_reuse:
            print(f"tts scene {index}: {scene['title']}")
            audio = synthesize_scene(
                client=client,
                text=narration,
                language=settings["language"],
                speaker=settings["speaker"],
                model=settings["model"],
                sample_rate=settings["sample_rate"],
                pace=settings["pace"],
            )
            save(audio, str(audio_path))
            metadata_path.write_text(
                json.dumps(
                    {
                        "fingerprint": fingerprint,
                        "title": scene["title"],
                        "audio": audio_path.name,
                        "settings": settings,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
        else:
            print(f"reuse scene {index}: {audio_path}")

        duration_seconds = get_duration_seconds(audio_path)
        scene["audio"] = public_asset_path(args.public_dir, audio_path)
        scene["audioDurationSeconds"] = round(duration_seconds, 3)
        scene["durationFrames"] = math.ceil(
            (duration_seconds + args.hold_seconds) * args.fps
        )

    args.out_storyboard.parent.mkdir(parents=True, exist_ok=True)
    args.out_storyboard.write_text(
        json.dumps(storyboard, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    total_frames = sum(scene["durationFrames"] for scene in storyboard["scenes"])
    print(f"wrote: {args.out_storyboard}")
    print(f"duration_seconds: {total_frames / args.fps:.1f}")


if __name__ == "__main__":
    main()
