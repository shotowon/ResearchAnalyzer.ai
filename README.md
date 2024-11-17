# ResearchAnalyzer.ai DIPLOMA

# заходите в backend :
cd backend

# создаете вирт. место для питона:
python -m venv venv

# активируете его:
venv/scripts/activate - windows

source venv/bin/activate - linux

# качаете все зависимости:
pip install -r requirements.txt

# запускаете бандита:
uvicorn src.main:app --reload

