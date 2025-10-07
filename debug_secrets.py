import os

print("--- Python Secret Debugger ---")

# Try to get the environment variables
asana_pat = os.getenv('ASANA_PAT')
project_gid = os.getenv('PROJECT_GID')

# Check and print the value of ASANA_PAT
if asana_pat:
    print(f"ASANA_PAT is present. Length: {len(asana_pat)}")
else:
    print("ASANA_PAT is NOT FOUND or is EMPTY.")

# Check and print the value of PROJECT_GID
if project_gid:
    print(f"PROJECT_GID is present. Value: {project_gid}")
else:
    print("PROJECT_GID is NOT FOUND or is EMPTY.")

print("--- Debugging complete ---")
