# Build commands

## Prerequisites
Create a Python 3.7 virtual environment and install requirements.txt.

`activate .\venv`

## PyInstaller
`pyinstaller analytics_pilot.spec`

## PyUpdater

### First time
- Copy `keypack.pyu`
- `pyupdater init`
- `pyupdater keys -i` 
- `pyupdater settings --plugin s3`
  - Bucket name: analytics-pilot-app
  - Bucket region: eu-central-1

### Update version
- Update version in `src\__init__.py`
- Set environment variables PYU_AWS_ID et PYU_AWS_SECRET
- `pyupdater build win.spec --app-version=0.0`
- `pyupdater pkg --process --sign`
- `pyupdater upload --service s3`
