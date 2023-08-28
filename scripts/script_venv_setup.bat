python -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install wheel build
python -m pip install -e ../qtapputils
python -m pip install spyder-kernels==2.4.*
pause
