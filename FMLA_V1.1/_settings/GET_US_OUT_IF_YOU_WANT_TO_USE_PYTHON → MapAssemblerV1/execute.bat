@echo off

REM Define the required Python version
set REQUIRED_VERSION=3.12

REM Define the path for the virtual environment
set VENV_DIR=_settings\venv

REM Check if Python is installed and its version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i

REM Display the Python version for debugging
echo Detected Python version: %PYTHON_VERSION%

REM Extract the major and minor version numbers
for /f "tokens=2,3 delims=. " %%a in ("%PYTHON_VERSION%") do (
    set MAJOR_VERSION=%%a
    set MINOR_VERSION=%%b
)

REM Compare the versions correctly
if not "%MAJOR_VERSION%"=="3" (
    goto version_error
)
if not "%MINOR_VERSION%"=="12" (
    goto version_error
)

REM Check if the virtual environment already exists
if not exist %VENV_DIR% (
    REM Create the virtual environment
    python -m venv %VENV_DIR%
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        goto error
    )
)

REM Activate the virtual environment
call %VENV_DIR%\Scripts\activate.bat
echo Virtual environment started

REM Execute the Python script with Python 3.12
echo Launching map_assembler.py
python map_assembler.py
if %errorlevel% neq 0 (
    echo Python script execution failed.
    goto script_error
)

REM Deactivate the virtual environment
call deactivate
goto end

:version_error
echo Python 3.12 is not installed. Please download and install it from the following link:
echo [Download Python 3.12] (https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe)
pause
goto end

:script_error
echo The Python script encountered an error. Please check the script for issues.
pause
goto end

:error
echo An unexpected error occurred.
pause

:end
