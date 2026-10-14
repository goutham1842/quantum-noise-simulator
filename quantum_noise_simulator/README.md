# Quantum Noise Simulator (Python + website)

pip install numpy flask
python main.py     # command-line demo: prints ideal vs noisy results, saves results/final_report.txt
python app.py      # website: open http://127.0.0.1:5000

| Your module                | File                                   |
|----------------------------|----------------------------------------|
| 1 User Interface           | static/index.html (calls /api/simulate)|
| 2 Circuit Builder          | circuit_builder.py, gates.py           |
| 3 Circuit Validation       | validation.py                          |
| 4 Ideal Simulator          | ideal_simulator.py (+ statevector.py)  |
| 5 Noise Manager            | noise_manager.py                       |
| 6 Noise Injection          | noise_injection.py                     |
| 7 Noisy Simulator          | noisy_simulator.py                     |
| Result Analyzer / charts   | analyzer.py (+ charts drawn by the page)|
| Pipeline controller        | simulator.py                           |
| Web server                 | app.py                                 |

## Deploy (frontend on Vercel, backend on Render)
Backend (Render, Web Service):  Build `pip install -r requirements.txt`   Start `gunicorn app:app --timeout 120`
Frontend (Vercel): Root Directory `static`, Framework "Other", no build command.
Then set `const API_BASE='https://YOUR-SERVICE.onrender.com'` at the top of the script in static/index.html and push.
