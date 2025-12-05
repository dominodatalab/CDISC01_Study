

"""
flow_artifacts_copy.py

1. Paste your Flyte code snippet (that includes "blobs = [ ... ]" and ends with "download_blobs(blobs)")
   into the FLYTE_SNIPPET variable below.
2. Set the OUTPUT_DIR variable to your desired directory.
3. Run: flow_artifacts_copy.py
"""

# ----------------------------- #
# Paste your Flyte snippet here #
# ----------------------------- #
FLYTE_SNIPPET = """
from flytekitplugins.domino.helpers import BlobDataLocation, download_blobs

blobs = [
    BlobDataLocation(
        "s3://ddl-sce57693-flyte-data//999b5d83-a1cc-4ed1-8d36-59880a4357ba/admh_dataset",
        local_dir="",
        local_filename="admh.sas7bdat",
        local_file_extension="",
    ),
    BlobDataLocation(
        "s3://ddl-sce57693-flyte-data//606afd05-9d19-4e29-883f-ca8c17c7f36e/advs_dataset",
        local_dir="",
        local_filename="advs.sas7bdat",
        local_file_extension="",
    ),
    BlobDataLocation(
        "s3://ddl-sce57693-flyte-data//30e4c638-08f2-44f4-9a2f-2f9fc699412d/adsl_dataset",
        local_dir="",
        local_filename="adsl.sas7bdat",
        local_file_extension="",
    ),
    BlobDataLocation(
        "s3://ddl-sce57693-flyte-data//af771702-6db5-4e60-b195-c208cf3c2035/adae_dataset",
        local_dir="",
        local_filename="adae.sas7bdat",
        local_file_extension="",
    ),
    BlobDataLocation(
        "s3://ddl-sce57693-flyte-data//e612131f-1e39-4d40-84ee-e63f122f2eaa/adcm_dataset",
        local_dir="",
        local_filename="adcm.sas7bdat",
        local_file_extension="",
    ),
    BlobDataLocation(
        "s3://ddl-sce57693-flyte-data//e6b49bd6-8988-45dc-91ac-29c100ab76fb/adlb_dataset",
        local_dir="",
        local_filename="adlb.sas7bdat",
        local_file_extension="",
    )
]
download_blobs(blobs)
"""

# --------------------------------------------------------------- #
# Set this to the directory you want all blobs to download into   #
# --------------------------------------------------------------- #
OUTPUT_DIR = "/mnt/data/scratch"
# e.g. OUTPUT_DIR = "/mnt/data/ADAM"

def main():
    # Remove or comment-out lines containing 'download_blobs(blobs)'
    snippet_without_first_download = []
    for line in FLYTE_SNIPPET.splitlines():
        if "download_blobs(blobs)" in line:
            line = f"# {line}"  # comment it out
        snippet_without_first_download.append(line)

    snippet_cleaned = "\n".join(snippet_without_first_download)

    # Then add the override and second download call
    updated_snippet = f"""
{snippet_cleaned}

for blob in blobs:
    blob.local_dir = r\"\"\"{OUTPUT_DIR}\"\"\"

download_blobs(blobs)
"""

    exec(updated_snippet, globals(), locals())

if __name__ == "__main__":
    main()