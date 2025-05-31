### 1. Create Virtual Environment
python3.11 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

### 2. Install Libraries
pip install -r requirements.txt

### 3. Run the FastAPI Server
uvicorn app.main:app --reload

### 4. Go to http://127.0.0.1:8000/docs 
