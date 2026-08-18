"""Scale profiles for DOM-79203 Flows Artifact Export.

Source of truth: the file-size report attached to DOM-79203
(`file_sizes_top10_stress testing.txt`). Folder file counts and aggregate
sizes are taken from that report and rounded up for the `full` profile.

The `reduced` profile keeps the same folder mix (many tiny files, a few
multi-GB files) at roughly 500 files / 20 GB with one 11 GB file, which is
the shape the CI-runnable scenario uses.
"""

from __future__ import annotations

from dataclasses import dataclass

GIB = 1024**3
MIB = 1024**2

# (folder, file_count, size_gib, default_extension) from the DOM-79203 report
FOLDER_SPEC = (
    ("derived_data", 65, 28.82, "sas7bdat"),
    ("analysis_data", 62, 43.94, "sas7bdat"),
    ("crt", 495, 111.88, "sas7bdat"),
    ("pgm", 2126, 0.05, "sas"),
    ("util", 618, 2.17, "sas7bdat"),
    ("reports", 1816, 30.95, "rtf"),
)

# Largest single file in the report, rounded up.
LARGE_FILE_NAME = "supplb.sas7bdat"
LARGE_FILE_FOLDER = "crt"
LARGE_FILE_GIB = 11.0

SDTM_DOMAINS = (
    "ae",
    "cm",
    "dm",
    "ds",
    "ex",
    "lb",
    "mh",
    "qs",
    "relrec",
    "sc",
    "se",
    "suppae",
    "suppdm",
    "suppds",
    "supplb",
    "sv",
    "ta",
    "te",
    "ti",
    "ts",
    "tv",
    "vs",
)

FILES_PER_TASK = 10
LARGE_FILE_THRESHOLD_BYTES = GIB  # files at or above this size get their own task


@dataclass(frozen=True)
class ScaleFile:
    folder: str
    name: str
    size_bytes: int
    output_name: str

    @property
    def artifact_filename(self) -> str:
        return f"{self.folder}__{self.name}"


def _distribute(count: int, total_bytes: int, large_file_bytes: int = 0) -> list[int]:
    """Spread `total_bytes` across `count` files as evenly as possible.

    When `large_file_bytes` is set, that amount is reserved for file 0 and the
    remainder is spread across the rest. Every file is at least 1 byte.
    """
    if count < 1:
        return []
    if large_file_bytes and count >= 1:
        remaining = max(count - 1, 0)
        rest = max(total_bytes - large_file_bytes, remaining)
        sizes = [large_file_bytes]
        if remaining:
            sizes.extend(_distribute(remaining, rest))
        return sizes
    base, extra = divmod(max(total_bytes, count), count)
    return [base + (1 if i < extra else 0) for i in range(count)]


def _folder_files(folder: str, count: int, total_bytes: int, ext: str, large: bool) -> list[ScaleFile]:
    sizes = _distribute(count, total_bytes, large_file_bytes=int(LARGE_FILE_GIB * GIB) if large else 0)
    files: list[ScaleFile] = []
    for i, size in enumerate(sizes):
        if large and i == 0:
            name = LARGE_FILE_NAME
        else:
            name = f"{folder}_{i:04d}.{ext}"
        output_name = f"{folder}_{i:04d}"
        files.append(ScaleFile(folder=folder, name=name, size_bytes=size, output_name=output_name))
    return files


def profile_files(profile: str) -> list[ScaleFile]:
    """Return the extra artifact files for `reduced` or `full`."""
    if profile == "full":
        files: list[ScaleFile] = []
        for folder, count, size_gib, ext in FOLDER_SPEC:
            total_bytes = int(round(size_gib * GIB))
            files.extend(_folder_files(folder, count, total_bytes, ext, large=(folder == LARGE_FILE_FOLDER)))
        return files
    if profile == "reduced":
        # ~500 files / ~20 GiB, preserving folder mix and one 11 GiB file.
        target_files = 500
        report_files = sum(spec[1] for spec in FOLDER_SPEC)
        files: list[ScaleFile] = []
        allocated = 0
        for index, (folder, count, _size_gib, ext) in enumerate(FOLDER_SPEC):
            is_last = index == len(FOLDER_SPEC) - 1
            scaled = max(1, round(count * target_files / report_files))
            if is_last:
                scaled = max(1, target_files - allocated)
            allocated += scaled
            if folder == LARGE_FILE_FOLDER:
                rest_bytes = int(9 * GIB)  # 11 GiB large file + 9 GiB remainder ~= 20 GiB
                files.extend(_folder_files(folder, scaled, rest_bytes + int(LARGE_FILE_GIB * GIB), ext, large=True))
            else:
                # Tiny leftovers: pgm stays tiny; others share ~1 GiB collectively aside from crt.
                tiny = folder == "pgm"
                folder_bytes = scaled * 256 if tiny else max(scaled * MIB, MIB)
                files.extend(_folder_files(folder, scaled, folder_bytes, ext, large=False))
        return files
    raise ValueError(f"Unknown scale profile {profile!r}; expected 'reduced' or 'full'")


def profile_batches(profile: str) -> list[list[ScaleFile]]:
    """Group files into Flyte tasks. Multi-GB files run alone so volume size can match."""
    batches: list[list[ScaleFile]] = []
    current: list[ScaleFile] = []
    for scale_file in profile_files(profile):
        if scale_file.size_bytes >= LARGE_FILE_THRESHOLD_BYTES:
            if current:
                batches.append(current)
                current = []
            batches.append([scale_file])
            continue
        current.append(scale_file)
        if len(current) >= FILES_PER_TASK:
            batches.append(current)
            current = []
    if current:
        batches.append(current)
    return batches


def profile_totals(profile: str) -> tuple[int, int]:
    files = profile_files(profile)
    return len(files), sum(item.size_bytes for item in files)
