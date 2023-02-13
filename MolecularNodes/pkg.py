import subprocess
import sys
import os
import site
from importlib.metadata import version
import bpy
import re
import requests
import platform


PYPI_MIRROR = {
    # the original.
    '':'', 
    # two mirrors in China Mainland to help those victims of GFW.
    'BFSU':'https://mirrors.bfsu.edu.cn/pypi/web/simple',
    'TUNA':'https://pypi.tuna.tsinghua.edu.cn/simple'
    # append more if necessary.
}


def verify_user_sitepackages(package_location):
    if os.path.exists(package_location) and package_location not in sys.path:
        sys.path.append(package_location)


def verify(): 
    verify_user_sitepackages(site.getusersitepackages())


def run_pip(cmd,mirror='',timeout=600):
    # path to python.exe
    python_exe = os.path.realpath(sys.executable)
    cmd_list=[python_exe, "-m"] + cmd.split(' ')
    if mirror and mirror.startswith('https'):
        cmd_list+=['-i', mirror]
    try:
        subprocess.call(cmd_list, timeout=timeout)
    except subprocess.CalledProcessError as e:
        print(e)
        return

def get_pyrosetta_url(username, password):
    # Store the base URL in a variable
    base_url = "https://graylab.jhu.edu/download/PyRosetta4/archive/release/PyRosetta4.Release"
    print(f'Using License: {username}:{password}')

    # Get the Python version
    python_version = "".join(str(i) for i in platform.python_version_tuple()[:2])

    # Get the OS architecture
    system = platform.system()
    machine = platform.machine()
    if system == "Darwin":
        # Check if the machine is running Apple Silicon
        if "arm" in machine:
            os_arch = "m1"
        else:
            os_arch = "mac"
    elif system == "Linux":
        if machine == "x86_64":
            # Check if the Linux distribution is Ubuntu
            with open("/etc/lsb-release") as f:
                if "Ubuntu" in f.read():
                    os_arch = "ubuntu"
                else:
                    os_arch = "linux"
        elif machine == "aarch64":
            os_arch = "aarch64"
        else:
            raise ValueError("Unknown machine architecture.")
    else:
        raise ValueError("Unknown machine architecture.")

    # Build the URL using the base URL, Python version, and OS architecture
    url = f"{base_url}.python{python_version}.{os_arch}.wheel/latest.html"

    # Send a GET request to the URL and store the response
    response = requests.get(url, auth=(username, password))
    print(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Use a regular expression to extract the link from the response text
        match = re.search('<meta http-equiv="REFRESH" content="1; url=(.*?)">', response.text)
        # Check if a match was found
        if match:
            # Extract the link from the match
            refresh_url = match.group(1)
            # Build the full URL using the refresh URL and base URL . The lisence is explictly passed to url for pip. NOT SAFE.
            full_url = f"{base_url}.python{python_version}.{os_arch}.wheel/{refresh_url}".replace('//', f'//{username}:{password}@')
            # Print the full URL
            print(full_url)
            return(full_url)
        else:
            # Print an error message
            raise ChildProcessError("Error: Could not extract link from response text.")
    else:
        # Print an error message
        raise ConnectionError("Error: Could not retrieve text from URL.")



def install(mirror='',pyrosetta_user=None,pyrosetta_password=None):


    #subprocess.call([python_exe, "-m", "ensurepip"])
    run_pip('ensurepip')
    #subprocess.call([python_exe, "-m", "pip", "install","--upgrade", "pip"], timeout=600)
    run_pip('pip install --upgrade pip', mirror=PYPI_MIRROR[mirror])

    #install required packages
    #subprocess.call([python_exe, "-m", "pip", "install", "biotite==0.35.0"], timeout=600)
    run_pip('pip install biotite==0.36.1', mirror=PYPI_MIRROR[mirror])
    #subprocess.call([python_exe, "-m", "pip", "install", "MDAnalysis==2.2.0"], timeout=600)
    run_pip('pip install MDAnalysis==2.2.0', mirror=PYPI_MIRROR[mirror])
        

    pyrosetta_url=get_pyrosetta_url(username=pyrosetta_user, password=pyrosetta_password)
    #subprocess.call([python_exe, "-m", "pip", "install", pyrosetta_url], timeout=600)
    run_pip(f'pip install {pyrosetta_url}', timeout=3600)

def available():
    verify()
    all_packages_available = True
    for module in ['biotite', 'MDAnalysis', 'pyrosetta']:
        try:
            version(module)
        except:
            all_packages_available = False
    return all_packages_available



    