# Contributing to Smart Investment & Portfolio Analytics

Thank you for your interest in contributing! We welcome contributions to financial modeling, engine features, UI enhancements, and documentation.

## Development Workflow

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/itsayush-17/smart-investment-portfolio-analytics.git
   cd smart-investment-portfolio-analytics
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Run the local development server:
   ```bash
   python backend/server.py
   ```
   Open `http://127.0.0.1:8000` in your web browser.

4. Run the smoke test suite before opening a pull request:
   ```bash
   pytest backend/tests_smoke.py
   ```

## Pull Request Guidelines

- Keep changes focused and well-documented.
- Ensure all tests pass cleanly.
- Maintain code cleanliness and follow PEP 8 style standards for Python code.
