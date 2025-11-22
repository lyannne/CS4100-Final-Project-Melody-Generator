"""Organize raw mood MIDI files into per-emotion folders.

This script expects a source folder (by default `data/raw/all_moods`) that
contains MIDI files named with the pattern:

	XMIDI_<Emotion>_<Genre>_<ID_len_8>.midi

It will create folders under `data/raw` for each emotion and move the files
into the matching folder. Files that don't match the expected pattern or whose
emotion is not in the known list are moved into `data/raw/unknown`.

Usage (from repository root):
	python -m src.mood_data_pipeline --organize

See the --help output for options like --source and --dest.
"""

import re
import shutil
from pathlib import Path
import argparse


DEFAULT_EMOTIONS = [
	"exciting", "warm", "happy", "romantic", "funny",
	"sad", "angry", "lazy", "quiet", "fear", "magnificent",
]


def organize_midi_by_emotion(all_moods_dir: str = "data/raw/all_moods", raw_base: str = "data/raw",
							 emotions: list = None):
	"""Move MIDI files from `all_moods_dir` into emotion folders under `raw_base`.

	Returns a dict of counts per emotion.
	"""
	if emotions is None:
		emotions = DEFAULT_EMOTIONS
	emotions = [e.lower() for e in emotions]

	all_moods_path = Path(all_moods_dir)
	base_path = Path(raw_base)

	if not all_moods_path.exists():
		print(f"Source folder {all_moods_path} does not exist. Nothing to organize.")
		return {}

	# Ensure target emotion folders exist
	for emo in emotions + ["unknown"]:
		target = base_path / emo
		if not target.exists():
			target.mkdir(parents=True, exist_ok=True)

	pattern = re.compile(r"^XMIDI_([^_]+)_", re.IGNORECASE)
	counts = {emo: 0 for emo in emotions}
	counts["unknown"] = 0

	midi_files = [p for p in all_moods_path.iterdir() if p.is_file() and p.suffix.lower() in {".mid", ".midi"}]
	print(f"Found {len(midi_files)} MIDI files in {all_moods_path}")

	for p in midi_files:
		m = pattern.match(p.name)
		if m:
			emo = m.group(1).lower()
			if emo in emotions:
				dest_dir = base_path / emo
			else:
				dest_dir = base_path / "unknown"
				emo = "unknown"
		else:
			dest_dir = base_path / "unknown"
			emo = "unknown"

		dest = dest_dir / p.name
		try:
			shutil.move(str(p), str(dest))
		except Exception as e:
			print(f"Failed to move {p} -> {dest}: {e}")
			continue
		counts[emo] = counts.get(emo, 0) + 1

	print("Organization complete. Summary:")
	for emo, c in counts.items():
		print(f"  {emo}: {c} files")

	# If the source folder is now empty, remove it
	try:
		# If there are no entries left in the directory, remove it
		if not any(all_moods_path.iterdir()):
			all_moods_path.rmdir()
			print(f"Removed empty source folder {all_moods_path}")
		else:
			print(f"Source folder {all_moods_path} is not empty; not removed.")
	except Exception as e:
		print(f"Could not remove source folder {all_moods_path}: {e}")

	return counts


def main():
	parser = argparse.ArgumentParser(description="Organize raw mood MIDI files into per-emotion folders.")
	parser.add_argument("--organize", action="store_true", help="Run organization (moves files).")
	parser.add_argument("--source", default="data/raw/all_moods", help="Source folder containing raw all_moods MIDI files")
	parser.add_argument("--dest", default="data/raw", help="Destination raw base folder where emotion folders will be created")
	args = parser.parse_args()

	if args.organize:
		organize_midi_by_emotion(all_moods_dir=args.source, raw_base=args.dest)


if __name__ == "__main__":
	main()

