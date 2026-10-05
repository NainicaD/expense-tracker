# 💸 SplitEase

A simple Streamlit app for tracking shared expenses and figuring out who owes what.

## Features

- **People** – add or remove the people who are splitting expenses
- **Add expense** – log an item with a quantity and price, and choose whether each unit is split evenly between everyone or just specific people (e.g. one dustbin charged to one person, a second split between two others)
- **Expenses** – view all logged expenses in a table, with the per-person share for each, and remove any entry
- **Summary** – see a grand total and a bar chart breaking down how much each person owes

## Getting started

### Prerequisites

- Python 3.9+

### Installation

```bash
git clone https://github.com/NainicaD/expense-tracker.git
cd expense-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (typically `http://localhost:8501`).

## Tech stack

- [Streamlit](https://streamlit.io/) – UI
- [Pandas](https://pandas.pydata.org/) – data handling
- [Altair](https://altair-viz.github.io/) – charts

## Notes

Data is stored in Streamlit's session state, so it resets whenever the app restarts or the browser session ends.
