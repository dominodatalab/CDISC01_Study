"""
NetApp Volume Setup Script for Domino Data Lab

This script automates the setup of NetApp volumes for a Domino project.
It:
1. Discovers available NetApp filesystems automatically
2. Creates required NetApp volumes for production and QC workflows
3. Attaches shared volumes from related SDTM projects
4. Creates necessary artifact directories for outputs

NetApp volume names are globally unique and prefixed with the project name
to avoid naming conflicts across the Domino deployment.

Author: Domino Data Lab
Version: 2.0
"""

from domino import Domino
import os
import requests
from re import sub

# ==============================================================================
# ENVIRONMENT CONFIGURATION
# ==============================================================================

# Domino authentication and project configuration
DOMINO_USER_API_KEY = os.environ['DOMINO_USER_API_KEY']
DOMINO_API_HOST = os.environ['DOMINO_REMOTE_FILE_SYSTEM_HOSTPORT']
DOMINO_PROJECT_ID = os.environ['DOMINO_PROJECT_ID']
DOMINO_PROJECT_OWNER = os.environ['DOMINO_PROJECT_OWNER']
DOMINO_PROJECT_NAME = os.environ['DOMINO_PROJECT_NAME']

# Initialize Domino client
domino = Domino(f"{DOMINO_PROJECT_OWNER}/{DOMINO_PROJECT_NAME}")

# NetApp Volumes API base path
NETAPP_BASE_PATH = "remotefs/v1"

# Default capacity for volumes (100GB in bytes)
DEFAULT_VOLUME_CAPACITY = 100 * 1024 * 1024 * 1024

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def submit_api_call(method, endpoint, data=None):
    """
    Submit a REST API call to Domino with proper authentication.
    
    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        endpoint (str): API endpoint path (relative to DOMINO_API_HOST)
        data (dict, optional): JSON payload for POST/PUT requests
    
    Returns:
        Response content as JSON dict, text string, or raw response object
    """
    headers = {
        'X-Domino-Api-Key': DOMINO_USER_API_KEY, 
        'Content-Type': 'application/json',
        'accept': 'application/json',
    }
    url = f'{DOMINO_API_HOST}/{endpoint}'
    
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
        base_name (str): Base name for the volume (e.g., "METADATA", "ADAM")
    
    Returns:
        str: Globally unique volume name (e.g., "CDISC03_JC_METADATA")
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
        filesystems_response = submit_api_call('GET', f'{NETAPP_BASE_PATH}/filesystems')
        
        # Validate response
        if not isinstance(filesystems_response, dict):
            print(f"ERROR: Expected dict response, got {type(filesystems_response)}")
            return None
        
        if 'data' not in filesystems_response:
            print(f"ERROR: Response missing 'data' field")
            return None
        
        filesystems = filesystems_response['data']
        
        if len(filesystems) == 0:
            print("ERROR: No filesystems found in the deployment")
            return None
        
        print(f"Found {len(filesystems)} filesystem(s):")
        for fs in filesystems:
            default_marker = " [DEFAULT]" if fs.get('isDataPlaneDefault', False) else ""
            print(f"  - {fs['name']} (ID: {fs['id']}, Data Plane: {fs.get('dataPlaneName', 'unknown')}){default_marker}")
        
        # Try to find the default filesystem for the data plane
        for fs in filesystems:
            if fs.get('isDataPlaneDefault', False):
                print(f"\n✓ Using default filesystem: {fs['name']} (ID: {fs['id']})")
                return fs['id']
        
        # No default found, use the first one
        fs = filesystems[0]
        print(f"\nWARNING: No default filesystem found, using first available: {fs['name']} (ID: {fs['id']})")
        return fs['id']
        
    except Exception as e:
        print(f"ERROR: Failed to discover filesystem: {e}")
        import traceback
        traceback.print_exc()
        return None


# ==============================================================================
# CREATE REQUIRED NETAPP VOLUMES
# ==============================================================================

# Define required volumes and their purposes
# These are project-specific volumes created for this ADAM/RE project
REQUIRED_VOLUMES = {
    "METADATA": "Internal metadata for the TFLs. Pulled from the MDR and converted to sas7bdat",
    "COMPARE": "PROC COMPARE datasets for QC",
    "ADAM": "ADAM is created using SDTM data for production",
    "ADAMQC": "ADAMQC is created using SDTM data for qc"
}

print("=" * 80)
print("CREATING REQUIRED NETAPP VOLUMES")
print(f'{DOMINO_API_HOST}/{NETAPP_BASE_PATH}')
print(DOMINO_USER_API_KEY)
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
        'GET',
        f'{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}'
    )
    
    # Extract volume names from response
    CURRENT_VOLUMES = {}  # Map of names to full volume info
    if isinstance(existing_volumes_response, dict) and 'data' in existing_volumes_response:
        for volume in existing_volumes_response['data']:
            volume_name = volume['name']
            # Store both full name and volume info
            CURRENT_VOLUMES[volume_name] = volume
            
            # Also try to extract base name if it follows our naming convention
            if volume_name.startswith(f"{DOMINO_PROJECT_NAME}_"):
                base_name = volume_name.replace(f"{DOMINO_PROJECT_NAME}_", "", 1)
                CURRENT_VOLUMES[base_name] = volume
    
    print(f"\nFound {len(set(v['id'] for v in CURRENT_VOLUMES.values()))} existing volume(s) in project")
    
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
        # Create volume with project attachment
        # The grants array can be empty when projectId is specified
        create_response = submit_api_call(
            'POST',
            f'{NETAPP_BASE_PATH}/volumes',
            {
                "name": volume_name,
                "description": volume_description,
                "filesystemId": filesystem_id,
                "capacity": DEFAULT_VOLUME_CAPACITY,
                "projectId": DOMINO_PROJECT_ID,
                "grants": []  # Empty grants when project attachment is used
            }
        )
        
        if isinstance(create_response, dict) and 'id' in create_response:
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
REQUIRED_ATTACHED_VOLUMES = {
    "SDTMBLIND"
}

# Derive the SDTM project name from the current project name
# Convention: Replace "RE_*" pattern with "SDTM" to find source project
SDTM_PROJECT_NAME = sub(r"RE_\w+", "SDTM", DOMINO_PROJECT_NAME)
print(f"\nLooking for SDTM project: {SDTM_PROJECT_NAME}")

# Get SDTM project ID from project list
try:
    projects_response = submit_api_call(
        "GET",
        "api/projects/beta/projects?limit=999"
    )
    
    SDTM_PROJECT_ID = None
    if isinstance(projects_response, dict) and 'projects' in projects_response:
        for project in projects_response['projects']:
            if project['name'] == SDTM_PROJECT_NAME:
                SDTM_PROJECT_ID = project['id']
                break
    
    if not SDTM_PROJECT_ID:
        print(f"WARNING: Could not find SDTM project '{SDTM_PROJECT_NAME}'")
        print("Skipping volume attachment from SDTM project")
    else:
        print(f"✓ Found SDTM project (ID: {SDTM_PROJECT_ID})")
        
        # Get available volumes from the SDTM project
        try:
            sdtm_volumes_response = submit_api_call(
                'GET',
                f'{NETAPP_BASE_PATH}/volumes?project_id={SDTM_PROJECT_ID}'
            )
            
            # Build mapping of volume base names to volume objects
            SDTM_VOLUMES = {}
            if isinstance(sdtm_volumes_response, dict) and 'data' in sdtm_volumes_response:
                for volume in sdtm_volumes_response['data']:
                    volume_name = volume['name']
                    # Handle globally unique naming - extract base name
                    # Assumes naming convention: {PROJECT_NAME}_{BASE_NAME}
                    if volume_name.startswith(f"{SDTM_PROJECT_NAME}_"):
                        base_name = volume_name.replace(f"{SDTM_PROJECT_NAME}_", "", 1)
                    else:
                        base_name = volume_name
                    
                    SDTM_VOLUMES[base_name] = volume
            
            print(f"Found {len(SDTM_VOLUMES)} volume(s) in SDTM project")
            
            # Get currently attached volumes to avoid duplicates
            current_project_volumes = submit_api_call(
                'GET',
                f'{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}'
            )
            
            CURRENT_ATTACHED_IDS = set()
            if isinstance(current_project_volumes, dict) and 'data' in current_project_volumes:
                for volume in current_project_volumes['data']:
                    CURRENT_ATTACHED_IDS.add(volume['id'])
            
            # Attach each required volume that isn't already attached
            for required_volume in REQUIRED_ATTACHED_VOLUMES:
                if required_volume not in SDTM_VOLUMES:
                    print(f"\n✗ ERROR: Could not find required volume '{required_volume}' "
                          f"in {SDTM_PROJECT_NAME}")
                    print(f"  Available volumes: {list(SDTM_VOLUMES.keys())}")
                    continue
                
                volume_to_attach = SDTM_VOLUMES[required_volume]
                volume_id = volume_to_attach['id']
                
                # Check if already attached
                if volume_id in CURRENT_ATTACHED_IDS:
                    print(f"\n✓ Volume already attached: {volume_to_attach['name']}")
                    continue
                
                print(f"\nAttaching volume: {volume_to_attach['name']}")
                print(f"  Volume ID: {volume_id}")
                
                try:
                    attach_response = submit_api_call(
                        "POST",
                        f'{NETAPP_BASE_PATH}/rpc/attach-volume-to-project',
                        {
                            "volumeId": volume_id,
                            "projectId": DOMINO_PROJECT_ID
                        }
                    )
                    print(f"✓ Successfully attached volume: {volume_to_attach['name']}")
                    
                except Exception as e:
                    print(f"✗ ERROR: Failed to attach volume {volume_to_attach['name']}: {e}")
        
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
    ("/mnt/artifacts/sas_logs", "SAS execution logs for debugging and audit trail")
]

for directory_path, description in directories:
    try:
        os.makedirs(directory_path, exist_ok=True)
        print(f"✓ Created: {directory_path}")
        print(f"  Purpose: {description}")
    except Exception as e:
        print(f"✗ ERROR: Failed to create {directory_path}: {e}")

print("\n" + "=" * 80)
print("NETAPP VOLUME SETUP COMPLETE")
print("=" * 80)