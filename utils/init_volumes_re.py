"""
NetApp Volume Setup Script for Domino Data Lab

This script automates the setup of NetApp volumes for a Domino project,
replacing the legacy dataset-based approach. It:
1. Creates required NetApp volumes for production and QC workflows
2. Attaches shared volumes from related SDTM projects
3. Creates necessary artifact directories for outputs

NetApp volume names are globally unique and prefixed with the project name
to avoid naming conflicts across the Domino deployment.

Author: Domino Data Lab
Version: 1.0
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
DOMINO_API_HOST = os.environ['DOMINO_API_HOST']
DOMINO_PROJECT_ID = os.environ['DOMINO_PROJECT_ID']
DOMINO_PROJECT_OWNER = os.environ['DOMINO_PROJECT_OWNER']
DOMINO_PROJECT_NAME = os.environ['DOMINO_PROJECT_NAME']

# Initialize Domino client
domino = Domino(f"{DOMINO_PROJECT_OWNER}/{DOMINO_PROJECT_NAME}")

# NetApp Volumes API base path
NETAPP_BASE_PATH = "remotefs/v1"

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
            print(f"Response: {response.text[:500]}")  # Print first 500 chars
        
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


def get_default_filesystem():
    """
    Get the default filesystem for the current data plane.
    
    Returns:
        dict: Filesystem object with id, name, and other properties
        None: If no default filesystem is found
    """
    try:
        filesystems_response = submit_api_call('GET', f'{NETAPP_BASE_PATH}/filesystems')
        
        # Debug: print response type and content
        print(f"DEBUG: Filesystems response type: {type(filesystems_response)}")
        print(f"DEBUG: Filesystems response: {filesystems_response}")
        
        # Check if response is a dict with data
        if not isinstance(filesystems_response, dict):
            print(f"ERROR: Expected dict response, got {type(filesystems_response)}")
            return None
        
        if 'data' not in filesystems_response:
            print(f"ERROR: Response missing 'data' field. Response keys: {filesystems_response.keys()}")
            return None
        
        # Look for default filesystem
        for filesystem in filesystems_response['data']:
            if filesystem.get('isDataPlaneDefault', False):
                return filesystem
        
        # If no default found, return the first filesystem
        if len(filesystems_response['data']) > 0:
            print("WARNING: No default filesystem found, using first available filesystem")
            return filesystems_response['data'][0]
        
        print("ERROR: No filesystems available")
        return None
        
    except Exception as e:
        print(f"ERROR: Failed to get default filesystem: {e}")
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

# Default capacity for volumes (100GB in bytes)
DEFAULT_VOLUME_CAPACITY = 100 * 1024 * 1024 * 1024

print("=" * 80)
print("CREATING REQUIRED NETAPP VOLUMES")
print("=" * 80)

# Get the default filesystem for volume creation
default_filesystem = get_default_filesystem()

if not default_filesystem:
    print("ERROR: Cannot create volumes without a filesystem. Exiting.")
    exit(1)

filesystem_id = default_filesystem['id']
print(f"Using filesystem: {default_filesystem['name']} (ID: {filesystem_id})")

# Get list of existing volumes for this project
try:
    existing_volumes_response = submit_api_call(
        'GET',
        f'{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}'
    )
    
    # Extract volume names from response
    CURRENT_VOLUMES = set()
    if existing_volumes_response and 'data' in existing_volumes_response:
        for volume in existing_volumes_response['data']:
            CURRENT_VOLUMES.add(volume['name'])
    
    print(f"Found {len(CURRENT_VOLUMES)} existing volumes in project")
    
except Exception as e:
    print(f"ERROR: Failed to list existing volumes: {e}")
    CURRENT_VOLUMES = set()

# Create any required volumes that don't already exist
for volume_key, volume_description in REQUIRED_VOLUMES.items():
    volume_name = generate_volume_name(volume_key)
    
    # Check if volume already exists
    if volume_name in CURRENT_VOLUMES:
        print(f"✓ Volume already exists: {volume_name}")
        continue
    
    print(f"Creating NetApp volume: {volume_name}")
    
    try:
        # Create volume with appropriate grants
        # VolumeOwner role grants full access to the creator
        create_response = submit_api_call(
            'POST',
            f'{NETAPP_BASE_PATH}/volumes',
            {
                "name": volume_name,
                "description": volume_description,
                "filesystemId": filesystem_id,
                "capacity": DEFAULT_VOLUME_CAPACITY,
                "projectId": DOMINO_PROJECT_ID,
                "grants": []  # Project attachment handles access
            }
        )
        
        if create_response and 'id' in create_response:
            print(f"✓ Successfully created volume: {volume_name} (ID: {create_response['id']})")
        else:
            print(f"✗ Failed to create volume {volume_name}: {create_response}")
            
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
print(f"Looking for SDTM project: {SDTM_PROJECT_NAME}")

# Get SDTM project ID from project list
try:
    projects_response = submit_api_call(
        "GET",
        "api/projects/beta/projects?limit=999"
    )
    
    SDTM_PROJECT_ID = None
    if projects_response and 'projects' in projects_response:
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
            if sdtm_volumes_response and 'data' in sdtm_volumes_response:
                for volume in sdtm_volumes_response['data']:
                    volume_name = volume['name']
                    # Handle globally unique naming - extract base name
                    # Assumes naming convention: {PROJECT_NAME}_{BASE_NAME}
                    if volume_name.startswith(f"{SDTM_PROJECT_NAME}_"):
                        base_name = volume_name.replace(f"{SDTM_PROJECT_NAME}_", "", 1)
                    else:
                        base_name = volume_name
                    
                    SDTM_VOLUMES[base_name] = volume
            
            print(f"Found {len(SDTM_VOLUMES)} volumes in SDTM project")
            
            # Get currently attached volumes in this project
            try:
                current_project_volumes = submit_api_call(
                    'GET',
                    f'{NETAPP_BASE_PATH}/volumes?project_id={DOMINO_PROJECT_ID}'
                )
                
                CURRENT_ATTACHED = set()
                if current_project_volumes and 'data' in current_project_volumes:
                    for volume in current_project_volumes['data']:
                        # Check if this volume has the SDTM project in its projects list
                        if 'projects' in volume:
                            for proj in volume['projects']:
                                if proj.get('projectId') == SDTM_PROJECT_ID:
                                    volume_name = volume['name']
                                    # Extract base name
                                    if volume_name.startswith(f"{SDTM_PROJECT_NAME}_"):
                                        base_name = volume_name.replace(f"{SDTM_PROJECT_NAME}_", "", 1)
                                    else:
                                        base_name = volume_name
                                    CURRENT_ATTACHED.add(base_name)
                
                print(f"Currently have {len(CURRENT_ATTACHED)} volumes attached from SDTM project")
                
            except Exception as e:
                print(f"WARNING: Could not determine currently attached volumes: {e}")
                CURRENT_ATTACHED = set()
            
            # Attach each required volume that isn't already attached
            for required_volume in REQUIRED_ATTACHED_VOLUMES:
                if required_volume in CURRENT_ATTACHED:
                    print(f"✓ Volume already attached: {required_volume}")
                    continue
                
                if required_volume not in SDTM_VOLUMES:
                    print(f"✗ ERROR: Could not find required volume '{required_volume}' "
                          f"in {SDTM_PROJECT_NAME} volumes: {list(SDTM_VOLUMES.keys())}")
                    continue
                
                volume_to_attach = SDTM_VOLUMES[required_volume]
                volume_id = volume_to_attach['id']
                
                print(f"Attaching volume: {volume_to_attach['name']} (ID: {volume_id})")
                
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
        print(f"✓ Created: {directory_path} - {description}")
    except Exception as e:
        print(f"✗ ERROR: Failed to create {directory_path}: {e}")

print("\n" + "=" * 80)
print("NETAPP VOLUME SETUP COMPLETE")
print("=" * 80)