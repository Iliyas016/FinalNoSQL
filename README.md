
#  EventPro: Event Ticketing System

A lightweight, full-stack application for managing event discovery and ticket sales. This project uses **FastAPI** for the backend and **MongoDB** for high-performance data storage.

---

##  Quick Setup

1. **Install Dependencies**
   Run the following command in your terminal:
   ```bash
   pip install fastapi uvicorn motor python-jose



2. **Database**
Ensure **MongoDB** is running locally on `localhost:27017`.


3. **Run the Backend**
Start the FastAPI server:
```bash
uvicorn main:app --reload

```


4. **Launch the Frontend**
Open `frontend/index.html` directly in your web browser.

---

## Access Credentials

* **Administrator:**
* Login: `admin`
* Password: `123`
* Capabilities: Create/Delete events, view revenue analytics.*


* **User:**
* Create your own account via the **Register** page.
* Capabilities: Browse events, post reviews, purchase tickets.*



---

## System Architecture

1. **Frontend:** HTML, JavaScript & Bootstrap 5.
2. **Backend:** Asynchronous REST API using FastAPI.
3. **Database:** MongoDB.

---

## Database Logic

* **Atomic Updates:** Uses `$inc` to ensure ticket counts remain accurate during simultaneous purchases.
* **Embedded Data:** Reviews are stored directly inside the event document using `$push` for faster loading.
* **Indexing:** Optimized with a **Compound Index** on `category` and `date` to ensure lightning-fast event filtering.

---

## Project Files

* `main.py`: Contains all API routes and database logic.
* `frontend/index.html`: The user interface and client-side logic.
* `requirements.txt`: List of Python packages needed.

