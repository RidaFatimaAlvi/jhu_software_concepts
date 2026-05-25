Rida Fatima Alvi – Module 1 Flask Website

Project Overview
This project is a personal developer website built using Flask, HTML, CSS, and Jinja templates.
The website includes:
- An About page with a biography and image
- A Contact page with professional contact information
- A Publications page describing the Module 1 project

Technologies Used
- Python 3.12
- Flask
- HTML
- CSS
- Jinja Templates
- Flask Blueprints

Project Structure
module_1/
├── board/
│   ├── static/
│   │   ├── rida.jpg
│   │   └── style.css
│   ├── templates/
│   │   ├── _navigation.html
│   │   ├── base.html
│   │   └── pages/
│   │       ├── contact.html
│   │       ├── home.html
│   │       └── publications.html
│   ├── __init__.py
│   └── pages.py
├── README.txt
├── requirements.txt
└── run.py

How to Run the Website

1. Create and activate a virtual environment

Mac/Linux:
python3 -m venv venv
source venv/bin/activate

2. Install required packages

pip install -r requirements.txt

3. Run the Flask application

python run.py

4. Open the website in your browser

http://127.0.0.1:8080

Features
- Flask Blueprint architecture
- Jinja template inheritance
- Shared navigation bar using include templates
- Responsive left/right homepage layout
- Active tab highlighting
- Custom CSS styling

References
This project was developed using concepts adapted from the Real Python Flask tutorial:
https://realpython.com/flask-project/

AI-assisted debugging, styling, and Flask template guidance were provided through ChatGPT.

All code and design decisions were reviewed, modified, and implemented for the requirements of this assignment.