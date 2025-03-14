'Schooled' is a Python command-line prototype Learning Management System featuring secure software development principles.

FEATURES
-------------------
-------------------
- Role-based access control:
  - Admins can update user details and course content;
  - Teachers can upload course content and mark student answers;
  - Students can upload answers.

- Security toggling;

- Secure, encrypted password storage;

- Encrypted data transfer;

- Restriction of the number of log in attempts;

- Locking out for unapproved practices;

- Restricted file type uploads;

- Restricting file size uploads.


REQUIREMENTS
-------------------
-------------------
anyio==4.4.0
argon2-cffi==23.1.0
argon2-cffi-bindings==21.2.0
arrow==1.3.0
asgiref==3.7.2
astroid==3.2.4
asttokens==2.4.1
async-lru==2.0.4
attrs==23.2.0
Babel==2.15.0
beautifulsoup4==4.12.3
bleach==6.1.0
blinker==1.8.2
certifi==2024.6.2
cffi==1.16.0
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
comm==0.2.2
debugpy==1.8.2
decorator==5.1.1
defusedxml==0.7.1
dill==0.3.8
Django==5.0.3
executing==2.0.1
fastjsonschema==2.20.0
flake8==7.1.1
Flask==3.0.3
fqdn==1.5.1
h11==0.14.0
httpcore==1.0.5
httpx==0.27.0
idna==3.7
ipykernel==6.29.5
ipython==8.26.0
isoduration==20.11.0
isort==5.13.2
itsdangerous==2.2.0
jedi==0.19.1
Jinja2==3.1.4
json5==0.9.25
jsonpointer==3.0.0
jsonschema==4.22.0
jsonschema-specifications==2023.12.1
jupyter-events==0.10.0
jupyter-lsp==2.2.5
jupyter_client==8.6.2
jupyter_core==5.7.2
jupyter_server==2.14.1
jupyter_server_terminals==0.5.3
jupyterlab==4.2.3
jupyterlab_pygments==0.3.0
jupyterlab_server==2.27.2
MarkupSafe==2.1.5
matplotlib-inline==0.1.7
mccabe==0.7.0
mistune==3.0.2
nbclient==0.10.0
nbconvert==7.16.4
nbformat==5.10.4
nest-asyncio==1.6.0
notebook_shim==0.2.4
overrides==7.7.0
packaging==24.1
pandocfilters==1.5.1
parso==0.8.4
platformdirs==4.2.2
prometheus_client==0.20.0
prompt_toolkit==3.0.47
psutil==6.0.0
pure-eval==0.2.2
pycodestyle==2.12.1
pycparser==2.22
pyflakes==3.2.0
Pygments==2.18.0
pylint==3.2.6
python-dateutil==2.9.0
python-json-logger==2.0.7
pywin32==306
pywinpty==2.0.13
PyYAML==6.0.1
pyzmq==26.0.3
referencing==0.35.1
requests==2.32.3
rfc3339-validator==0.1.4
rfc3986-validator==0.1.1
rpds-py==0.18.1
Send2Trash==1.8.3
six==1.16.0
sniffio==1.3.1
soupsieve==2.5
sqlparse==0.4.4
stack-data==0.6.3
tabulate==0.9.0
terminado==0.18.1
tinycss2==1.3.0
tomlkit==0.13.2
tornado==6.4.1
traitlets==5.14.3
types-python-dateutil==2.9.0.20240316
typing_extensions==4.12.2
tzdata==2024.1
uri-template==1.3.0
urllib3==2.2.2
wcwidth==0.2.13
webcolors==24.6.0
webencodings==0.5.1
websocket-client==1.8.0
Werkzeug==3.0.4
windows-curses==2.3.2


USAGE INSTRUCTIONS
-------------------
-------------------
- Set up a virtual environment;
- Activate the virtual environment;
- Install requirements from the requirements.txt file;
- Run app.py from terminal.
- Run main.py from Powershell to view first menu – uncomment final line to see app run in Secure mode and test Brute Force attack.
- Navigate menus using letter choices.

*Encryption key should be stored in venv/Scripts/activate.bat file as shown below**
  *Encryption key to copy: venvpkwt6CJu5tFq1fRE_rdZiqakYemthvhdW_QlzkQUbjY=)* 

**Passwords for testing purposes**

- admin@school.co.uk: Monkey?Flask98
- student1@school.co.uk: LaptopBed87
- student2@school.co.uk: FalconWall45
- student3@school.co.uk: NeutronBarn75
- student4@school.co.uk: ParkJupiter42
- student5@school.co.uk: SwitchMarry15
- student6@school.co.uk: GloveJune14
- student7@school.co.uk: HeavenBoot65
- student8@school.co.uk: BigNine58
- student9@school.co.uk: GraveBicep74

- teacher1@school.co.uk: GirderRoulette65
- teacher2@school.co.uk: FranceTripe65
- teacher3@school.co.uk: LeggingsOstrich98
- teacher4@school.co.uk: PeopleFlag56

