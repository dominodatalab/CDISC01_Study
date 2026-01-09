"""
NetApp Volume Setup Script for Domino Data Lab

This script automates the setup of NetApp volumes for a Domino project.
It:
1. Discovers available NetApp filesystems automatically
2. Creates required NetApp volumes for production and development workflows
3. Attaches shared volumes from related SDTM projects
4. Creates necessary artifact directories for outputs

NetApp volume names are globally unique and prefixed with the project name
to avoid naming conflicts across the Domino deployment.

Author: Domino Data Lab
Version: 3.0
"""

from domino import Domino
import os
import requests
from re import sub

# ==============================================================================
# ENVIRONMENT CONFIGURATION
# ==============================================================================

# Domino project configuration
DOMINO_PROJECT_ID = os.environ["DOMINO_PROJECT_ID"]
DOMINO_PROJECT_OWNER = os.environ["DOMINO_PROJECT_OWNER"]
DOMINO_PROJECT_NAME = os.environ["DOMINO_PROJECT_NAME"]
DOMINO_USER_NAME = os.environ["DOMINO_USER_NAME"]

# API endpoints
DOMINO_API_PROXY = os.environ["DOMINO_API_PROXY"]
DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT = os.environ["DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT"]

# Initialize Domino client
domino = Domino(f"{DOMINO_PROJECT_OWNER}/{DOMINO_PROJECT_NAME}")

# NetApp Volumes API base path (relative to remote file system host)
NETAPP_BASE_PATH = "remotefs/v1"

# Default capacity for volumes (100GB in bytes)
DEFAULT_VOLUME_CAPACITY = 100 * 1024 * 1024 * 1024

# ==============================================================================
# AUTHENTICATION
# ==============================================================================


def get_access_token():
    """
    Get access token from Domino API proxy.

    Returns:
        str: Bearer token for API authentication
    """
    try:
        token_url = f"{DOMINO_API_PROXY}/access-token"
        response = requests.get(token_url)

        if response.status_code == 200:
            token = response.text.strip()
            print(f"✓ Successfully obtained access token")
            return token
        else:
            print(f"ERROR: Failed to get access token. Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return None

    except Exception as e:
        print(f"ERROR: Failed to get access token: {e}")
        return None


# Get authentication token at startup
ACCESS_TOKEN = get_access_token()

if not ACCESS_TOKEN:
    print("FATAL ERROR: Cannot proceed without access token")
    exit(1)

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================


def submit_api_call(method, endpoint, data=None, use_netapp_host=True):
    """
    Submit a REST API call to Domino with proper authentication.

    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        endpoint (str): API endpoint path (relative to host)
        data (dict, optional): JSON payload for POST/PUT requests
        use_netapp_host (bool): If True, use DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT,
                                otherwise use DOMINO_API_PROXY

    Returns:
        Response content as JSON dict, text string, or raw response object
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    # Choose the appropriate host
    if use_netapp_host:
        base_url = DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT
    else:
        base_url = DOMINO_API_PROXY

    url = f"{base_url}/{endpoint}"

    try:
        response = requests.request(method, url, headers=headers, json=data)

        # Check for HTTP errors
        if response.status_code >= 400:
            print(f"WARNING: HTTP {response.status_code} for {method} {endpoint}")
            print(f"Response: {response.text[:500]}")

        # Try to parse as JSON first
        try:
            return response.json()
        except ValueError:
            # If JSON parsing fails, return text
            return response.text

    except Exception as e:
        print(f"ERROR: Request failed for {method} {endpoint}: {e}")
        raise


def generate_volume_name(base_name):
    """
    Generate a globally unique NetApp volume name.

    NetApp volumes must be globally unique across the Domino deployment.
    This function prefixes the base name with the project name to ensure uniqueness.

    Args:
        base_name (str): Base name for the volume (e.g., "OUTPUT_DEV", "DATA_PROD")

    Returns:
        str: Globally unique volume name (e.g., "CDISC03_JC_OUTPUT_DEV")
    """
    return f"{DOMINO_PROJECT_NAME}_{base_name}"


def get_filesystem_id():
    """
    Discover and return the filesystem ID to use for volume creation.

    This function lists all available filesystems and returns:
    1. The default filesystem for the data plane (preferred)
    2. The first available filesystem (fallback)

    Returns:
        str: Filesystem ID to use
        None: If no filesystems are available
    """
    print("Discovering available filesystems...")

    try:
        # List all filesystems
        filesystems_response = submit_api_call("GET", f"{NETAPP_BASE_PATH}/filesystems")

        # Validate response
        if not isinstance(filesystems_response, dict):
            print(f"ERROR: Expected dict response, got {type(filesystems_response)}")
            return None

        if "data" not in filesystems_response:
            print(
                f"ERROR: Response missing 'data' field. Keys: {filesystems_response.keys()}"
            )
            return None

        filesystems = filesystems_response["data"]

        if len(filesystems) == 0:
            print("ERROR: No filesystems found in the deployment")
            return None

        print(f"Found {len(filesystems)} filesystem(s):")
        for fs in filesystems:
            default_marker = " [DEFAULT]" if fs.get("isDataPlaneDefault", False) else ""
            print(
                f"  - {fs['name']} (ID: {fs['id']}, Data Plane: {fs.get('dataPlaneName', 'unknown')}){default_marker}"
            )

        # Try to find the default filesystem for the data plane
        for fs in filesystems:
            if fs.get("isDataPlaneDefault", False):
                print(f"\n✓ Using default filesystem: {fs['name']} (ID: {fs['id']})")
                return fs["id"]

        # No default found, use the first one
        fs = filesystems[0]
        print(
            f"\nWARNING: No default filesystem found, using first available: {fs['name']} (ID: {fs['id']})"
        )
        return fs["id"]

    except Exception as e:
        print(f"ERROR: Failed to discover filesystem: {e}")
        import traceback

        traceback.print_exc()
        return None


def get_current_user_id():
    """
    Get the current user's ID from /users/self endpoint.

    Returns:
        str: User ID for grants/permissions
    """
    try:
        user_response = submit_api_call(
            "GET",
            "v4/users/self",
            use_netapp_host=False  # Use API proxy
        )

        if isinstance(user_response, dict) and "id" in user_response:
            user_id = user_response["id"]
            user_name = user_response.get("userName", "unknown")
            print(f"✓ Retrieved user ID: {user_id} (username: {user_name})")
            return user_id
        else:
            print("ERROR: Failed to get user ID from /users/self")
            print(f"Response: {user_response}")
            return None

    except Exception as e:
        print(f"ERROR: Failed to get current user ID: {e}")
        return None


# ==============================================================================
# GET CURRENT USER ID
# ==============================================================================

# Get current user ID for volume grants
DOMINO_USER_ID = get_current_user_id()

if not DOMINO_USER_ID:
    print("FATAL ERROR: Cannot proceed without user ID")
    exit(1)

print(f"✓ Authenticated as user: {DOMINO_USER_NAME}")
print(f"✓ Project: {DOMINO_PROJECT_NAME} (ID: {DOMINO_PROJECT_ID})")

# ==============================================================================
# CREATE REQUIRED NETAPP VOLUMES
# ==============================================================================

# Define required volumes and their purposes
# These are project-specific volumes created for this project
REQUIRED_VOLUMES = {
    "OUTPUT_DEV": "Development outputs for testing and validation",
    "OUTPUT_PROD": "Production outputs for final deliverables",
    "DATA_PROD": "Production data storage",
    "DATA_DEV": "Development data storage",
}

print("\n" + "=" * 80)
print("CREATING REQUIRED NETAPP VOLUMES")
print("=" * 80)

# Get filesystem ID
filesystem_id = get_filesystem_id()

if not filesystem_id:
    print("\nERROR: Cannot create volumes without a filesystem")
    print("\nPossible causes:")
    print("1. NetApp Volumes feature is not installed in this Domino deployment")
    print("2. NetApp Volumes feature is not enabled for your user")
    print("3. No filesystems have been configured")
    print("\nPlease contact your Domino administrator for assistance.")
    exit(1)

# Get list of existing volumes for this project
try:
    existing_volumes_response = submit_api_call(
        "GET", f"{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}"
    )

    # Extract volume names from response
    CURRENT_VOLUMES = {}  # Map of names to full volume info
    if (
        isinstance(existing_volumes_response, dict)
        and "data" in existing_volumes_response
    ):
        for volume in existing_volumes_response["data"]:
            volume_name = volume["name"]
            # Store both full name and volume info
            CURRENT_VOLUMES[volume_name] = volume

            # Also try to extract base name if it follows our naming convention
            if volume_name.startswith(f"{DOMINO_PROJECT_NAME}_"):
                base_name = volume_name.replace(f"{DOMINO_PROJECT_NAME}_", "", 1)
                CURRENT_VOLUMES[base_name] = volume

    unique_volumes = len(set(v["id"] for v in CURRENT_VOLUMES.values()))
    print(f"\nFound {unique_volumes} existing volume(s) in project")

except Exception as e:
    print(f"ERROR: Failed to list existing volumes: {e}")
    CURRENT_VOLUMES = {}

# Create any required volumes that don't already exist
for volume_key, volume_description in REQUIRED_VOLUMES.items():
    volume_name = generate_volume_name(volume_key)

    # Check if volume already exists
    if volume_name in CURRENT_VOLUMES or volume_key in CURRENT_VOLUMES:
        print(f"✓ Volume already exists: {volume_name}")
        continue

    print(f"\nCreating NetApp volume: {volume_name}")

    try:
        # Create volume with project attachment and owner grant
        # Volume roles (as defined in Swagger):
        #   - VolumeOwner: Full access, can manage permissions
        #   - VolumeEditor: Read/write access to volume content
        #   - VolumeReader: Read-only access to volume content
        #   - Service: Internal service access
        # The current user is added as VolumeOwner to have full control
        create_response = submit_api_call(
            "POST",
            f"{NETAPP_BASE_PATH}/volumes",
            {
                "name": volume_name,
                "description": volume_description,
                "filesystemId": filesystem_id,
                "capacity": DEFAULT_VOLUME_CAPACITY,
                "projectId": DOMINO_PROJECT_ID,
                "grants": [{"targetId": DOMINO_USER_ID, "targetRole": "VolumeOwner"}],
            },
        )

        if isinstance(create_response, dict) and "id" in create_response:
            print(f"✓ Successfully created volume: {volume_name}")
            print(f"  Volume ID: {create_response['id']}")
            print(f"  Capacity: {DEFAULT_VOLUME_CAPACITY / (1024**3):.0f} GB")
        else:
            print(f"✗ Failed to create volume {volume_name}")
            print(f"  Response: {create_response}")

    except Exception as e:
        print(f"✗ ERROR: Failed to create volume {volume_name}: {e}")


# ==============================================================================
# ATTACH SHARED NETAPP VOLUMES FROM SDTM PROJECT
# ==============================================================================

print("\n" + "=" * 80)
print("ATTACHING SHARED VOLUMES FROM SDTM PROJECT")
print("=" * 80)

# Define volumes that need to be imported/attached from the SDTM project
# These are the full volume names including the project prefix
REQUIRED_ATTACHED_VOLUMES = {"CDISC01_SDTMBLIND", "CDISC01_SDTMUNBLIND"}

# SDTM project name is fixed as CDISC01_SDTM
SDTM_PROJECT_NAME = "CDISC01_SDTM"
print(f"\nLooking for SDTM project: {SDTM_PROJECT_NAME}")

# Get SDTM project ID from project list
# Note: This uses the API proxy, not the remote file system host
try:
    projects_response = submit_api_call(
        "GET",
        "api/projects/beta/projects?limit=999",
        use_netapp_host=False,  # Use API proxy for project list
    )

    SDTM_PROJECT_ID = None
    if isinstance(projects_response, dict) and "projects" in projects_response:
        for project in projects_response["projects"]:
            if project["name"] == SDTM_PROJECT_NAME:
                SDTM_PROJECT_ID = project["id"]
                break

    if not SDTM_PROJECT_ID:
        print(f"WARNING: Could not find SDTM project '{SDTM_PROJECT_NAME}'")
        print("Skipping volume attachment from SDTM project")
    else:
        print(f"✓ Found SDTM project (ID: {SDTM_PROJECT_ID})")

        # Get available volumes from the SDTM project
        try:
            sdtm_volumes_response = submit_api_call(
                "GET", f"{NETAPP_BASE_PATH}/volumes?project_id={SDTM_PROJECT_ID}"
            )

            # Build mapping of volume names to volume objects
            SDTM_VOLUMES = {}
            if (
                isinstance(sdtm_volumes_response, dict)
                and "data" in sdtm_volumes_response
            ):
                for volume in sdtm_volumes_response["data"]:
                    volume_name = volume["name"]
                    # Store by full name to match the exact names we're looking for
                    SDTM_VOLUMES[volume_name] = volume

            print(f"Found {len(SDTM_VOLUMES)} volume(s) in SDTM project:")
            for vol_name in SDTM_VOLUMES.keys():
                print(f"  - {vol_name}")

            # Get currently attached volumes to avoid duplicates
            current_project_volumes = submit_api_call(
                "GET", f"{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}"
            )

            CURRENT_ATTACHED_IDS = set()
            if (
                isinstance(current_project_volumes, dict)
                and "data" in current_project_volumes
            ):
                for volume in current_project_volumes["data"]:
                    CURRENT_ATTACHED_IDS.add(volume["id"])

            # Attach each required volume that isn't already attached
            for required_volume_name in REQUIRED_ATTACHED_VOLUMES:
                if required_volume_name not in SDTM_VOLUMES:
                    print(
                        f"\n✗ ERROR: Could not find required volume '{required_volume_name}' "
                        f"in {SDTM_PROJECT_NAME}"
                    )
                    print(f"  Available volumes: {list(SDTM_VOLUMES.keys())}")
                    continue

                volume_to_attach = SDTM_VOLUMES[required_volume_name]
                volume_id = volume_to_attach["id"]

                # Check if already attached
                if volume_id in CURRENT_ATTACHED_IDS:
                    print(f"\n✓ Volume already attached: {volume_to_attach['name']}")
                    continue

                print(f"\nAttaching volume: {volume_to_attach['name']}")
                print(f"  Volume ID: {volume_id}")

                try:
                    attach_response = submit_api_call(
                        "POST",
                        f"{NETAPP_BASE_PATH}/rpc/attach-volume-to-project",
                        {"volumeId": volume_id, "projectId": DOMINO_PROJECT_ID},
                    )
                    print(f"✓ Successfully attached volume: {volume_to_attach['name']}")

                except Exception as e:
                    print(
                        f"✗ ERROR: Failed to attach volume {volume_to_attach['name']}: {e}"
                    )

        except Exception as e:
            print(f"ERROR: Failed to list SDTM project volumes: {e}")

except Exception as e:
    print(f"ERROR: Failed to get project list: {e}")


# ==============================================================================
# CREATE ARTIFACT DIRECTORIES
# ==============================================================================

print("\n" + "=" * 80)
print("CREATING ARTIFACT DIRECTORIES")
print("=" * 80)

# Create directory structure for workflow outputs
# These directories are used by SAS and R scripts for storing generated files

directories = [
    ("/mnt/artifacts/TFL", "Production TFLs (Tables, Figures, Listings)"),
    ("/mnt/artifacts/TFL_QC", "QC TFLs for validation"),
    ("/mnt/artifacts/sas_logs", "SAS execution logs for debugging and audit trail"),
]

for directory_path, description in directories:
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"✓ Created: {directory_path}")
        print(f"  Purpose: {description}")
    except Exception as e:
        print(f"✗ ERROR: Failed to create {directory_path}: {e}")

# ==============================================================================
# TRIGGER SUBDIRECTORY INITIALIZATION JOB
# ==============================================================================

print("\n" + "=" * 80)
print("LAUNCHING SUBDIRECTORY INITIALIZATION JOB")
print("=" * 80)

# Build volume mount configuration for all volumes
# This includes both newly created and attached volumes
try:
    # Get all volumes currently attached to this project
    all_volumes_response = submit_api_call(
        "GET", f"{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}"
    )

    volume_ids = []
    if isinstance(all_volumes_response, dict) and "data" in all_volumes_response:
        for volume in all_volumes_response["data"]:
            volume_name = volume["name"]
            volume_id = volume["id"]
            volume_ids.append(volume_id)
            print(f"  Will mount: {volume_name} (ID: {volume_id})")

    print(f"\nTotal volumes to mount: {len(volume_ids)}")

    if len(volume_ids) == 0:
        print(
            "WARNING: No volumes found to mount. Skipping subdirectory initialization."
        )
    else:
        # Launch Domino job to initialize subdirectories using REST API
        print("\nStarting Domino job to create subdirectories...")

        # Build job request payload according to NewJobV1 schema
        job_payload = {
            "projectId": DOMINO_PROJECT_ID,
            "commandToRun": "python /mnt/code/utils/init_subdirectories.py",
            "title": "Initialize NetApp Volume Subdirectories",
            "netAppVolumeIds": volume_ids,
        }

        # Start the job using REST API
        job_response = submit_api_call(
            "POST",
            "v4/jobs/start",
            data=job_payload,
            use_netapp_host=False,  # Use API proxy for job start
        )

        if isinstance(job_response, dict) and (
            "runId" in job_response or "id" in job_response
        ):
            run_id = job_response.get("runId") or job_response.get("id")
            print("✓ Successfully launched subdirectory initialization job")
            print(f"  Run ID: {run_id}")
            print("  This job will create the required subdirectory structures")
            print("  in all mounted NetApp volumes.")
        else:
            print("✗ Failed to launch subdirectory initialization job")
            print(f"  Response: {job_response}")

except Exception as e:
    print(f"ERROR: Failed to launch subdirectory initialization job: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("NETAPP VOLUME SETUP COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("1. Wait for the subdirectory initialization job to complete")
print("2. Check the job logs to verify all subdirectories were created")
print("3. Your NetApp volumes are now ready for use!")
