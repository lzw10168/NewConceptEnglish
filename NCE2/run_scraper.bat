@echo off
echo ===== New Concept English Scraper =====
echo Activating virtual environment...
call .\nce-env\Scripts\activate

echo Installing/updating dependencies...
pip install -r requirements.txt

echo Running scraper...
python main.py

echo Done! Press any key to exit.
pause 
