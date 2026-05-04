@echo off
echo ============================================
echo   DL Mongoose - Build Script
echo ============================================
echo.

:: Step 1 - Install dependencies
echo [1/4] Installing Python dependencies...
pip install -r requirements.txt
pip install pyinstaller
echo Done.
echo.

:: Step 2 - Build EXE with PyInstaller
echo [2/4] Building EXE with PyInstaller...
pyinstaller dl_mongoose.spec --clean
echo Done.
echo.

:: Step 3 - Check build output
echo [3/4] Checking build output...
if exist "dist\DLMongoose\DLMongoose.exe" (
    echo SUCCESS: EXE found at dist\DLMongoose\DLMongoose.exe
) else (
    echo ERROR: EXE not found. Check PyInstaller output above.
    pause
    exit /b 1
)
echo.

:: Step 4 - Remind about Inno Setup
echo [4/4] Next step - Create installer:
echo   1. Download Inno Setup from https://jrsoftware.org/isinfo.php
echo   2. Open installer.iss in Inno Setup Compiler
echo   3. Click Build - Compile
echo   4. Find your installer in installer_output folder
echo.
echo ============================================
echo   Build Complete!
echo ============================================
pause
