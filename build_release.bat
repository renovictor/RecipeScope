@echo off
setlocal
for /f "tokens=*" %%i in ('python -c "from version import get_executable_name; print(get_executable_name())"') do set EXE_NAME=%%i
pyinstaller --noconfirm --clean RecipeScope.spec
if not exist "dist\%EXE_NAME%" (
  echo Build output mismatch. Expected dist\%EXE_NAME%
  exit /b 1
)
echo Build complete: dist\%EXE_NAME%
endlocal
