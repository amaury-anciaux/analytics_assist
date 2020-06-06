# Objective
Alteryx and Knime are great software products to design analytics workflows. However, there is so much freedom for users to create their workflows that it's easy to end up with workflows that are messy, difficult to read, undocumented and hiding errors.

Analytics Assist warns the user of divergence from best practices when they save their workflows. It is designed to be unobstrusive, running in the background and letting the user know of errors via a notification. The user can then open it to see more details.

Analytics Assist is a desktop application built using wxPython. It monitors a folder specified in the configuration, and on each file save, it reads the XML descriptions of the workflow, translates the key elements into a common data model and runs a series of rules to identify errors.

# Features
- Monitors a folder for workflow saves, but can also run a manual scan of a workflow.
- Reads both Alteryx and Knime workflows
- Separated modules for reading XML and evaluating rules
- Desktop UI built with wxPython (tested only on Windows)
- Starts automatically with computer (can be turned off in configuration)
- Uses Windows notifications

# Usage
You can run Analytics Assist from source code, by installing Python with the appropriate dependencies. You can also package the software using PyInstaller, and distribute it to other users. It uses PyUpdater for automated updates.

# Build commands

## Prerequisites
Create a Python 3.7 virtual environment and install dependencies in requirements.txt.

`activate .\venv`

## PyInstaller
`pyinstaller analytics_assist.spec`

## PyUpdater

### First time
See instructions in the PyUpdater documentation. Example:
- Copy `keypack.pyu`
- `pyupdater init`
- `pyupdater keys -i` 
- `pyupdater settings --plugin s3`
  - Bucket name: [your-bucket]
  - Bucket key: [empty]
  - Bucket region: [your-region]

### Update version (example with AWS S3)
- Update version in `src\__init__.py`
- Set environment variables PYU_AWS_ID et PYU_AWS_SECRET
- `pyupdater build win.spec --app-version=[version]`
- `pyupdater pkg --process --sign`
- `pyupdater upload --service s3`
