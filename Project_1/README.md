# Credibility Scoring Project

CS676 — Algorithms for Data Science

## Project Overview

This project develops a credibility-scoring system for online sources. The algorithm evaluates URLs using multiple credibility signals, including domain type, source reputation, page-level characteristics, DOI presence, and other indicators. An optional LLM-assisted layer using Claude provides an additional credibility assessment.

## Results

The improved rule-based algorithm achieved a mean absolute error (MAE) of 0.053 and 91.7% band accuracy on the evaluation set. With the optional LLM layer, MAE decreased to 0.047 while band accuracy remained 91.7%.
## Live Application

The Credibility Scoring Project is deployed on Streamlit Community Cloud:

https://credibility-scoring-project.streamlit.app

## Project Files

## Project Files

- `CS676_Project_1.mp4` — project demonstration video
- `credibility.py` — credibility-scoring algorithm
- `main.py` — Streamlit application
- `evaluate.py` — quantitative evaluation
- `test_credibility.py` — algorithm tests
- `project_1_report.pdf` — final project report
- `project_1_report.md` — report source
- `requirements.txt` — Python dependencies
