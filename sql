# Import necessary modules
import os

def environ_build():
    # Read the CUJO configuration file
    cujo_file = '/opt/autosys/cujo/cujo.cfg'
    try:
        with open(cujo_file, 'r') as file:
            cujo_lines = file.readlines()
    except FileNotFoundError:
        raise Exception("WatchdogX configuration file not found")

    cujo = [line.strip() for line in cujo_lines if not line.startswith('#')]

    # Initialize variables
    sqllldr = {}
    region = {}
    local_kdb = {}
    global_kdb = {}

    # Process each line in the CUJO config file
    for cujoline in cujo:
        cujokey, cujoval = cujoline.split('=', 1)  # Splitting key and value based on "="
        cujokey, cujoval = cujokey.strip(), cujoval.strip()

        # Get Default SQLLDR path
        if cujokey == "SQLLDR":
            sqllldr['SQLLDR'] = cujoval

        # Get Default Region
        if cujokey == "REGION":
            region['REGION'] = cujoval

        # Get Default kDB (Local and Global)
        if cujokey == "LOCALKDB":
            local_kdb['Local'] = cujoval.split(',')[0]

        if cujokey == "GLOBALKDB":
            global_kdb['Global'] = cujoval.split(',')[0]

    # Error handling if REGION or Automation DB values are missing
    if 'REGION' not in region or 'Local' not in local_kdb or 'Global' not in global_kdb:
        raise Exception(f"Incorrect REGION and/or Automation DB values set.\n"
                        f"REGION={region.get('REGION', 'NOT SET')}\n"
                        f"Default LOCAL KDB={local_kdb.get('Local', 'NOT SET')}\n"
                        f"Default GLOBAL KDB={global_kdb.get('Global', 'NOT SET')}")
    
    # Print or return the configuration
    print(f"SQLLDR Path: {sqllldr.get('SQLLDR', 'NOT SET')}")
    print(f"Region: {region.get('REGION', 'NOT SET')}")
    print(f"Local KDB: {local_kdb.get('Local', 'NOT SET')}")
    print(f"Global KDB: {global_kdb.get('Global', 'NOT SET')}")

# Call the function to test it
environ_build()
