import socket
import subprocess

# Get the hostname
hostname = socket.gethostname()

# Run nslookup on the hostname and capture the output
try:
    nslookup_output = subprocess.check_output(['nslookup', hostname], universal_newlines=True)
    
    # Find the line containing "Name"
    for line in nslookup_output.splitlines():
        if "Name" in line:
            # Split the line to extract the second field and cut after the first dot
            name = line.split()[1]
            dnsname = name.split('.', 1)[1]  # Split after the first dot
            
            # Print the final DNS name
            print(f'DNS Name: {dnsname}')
            break
except subprocess.CalledProcessError as e:
    print(f"Error running nslookup: {e}")

