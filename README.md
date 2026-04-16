# QuSenseSim

## Overview

QuSenseSim is an interactive quantum sensing simulator designed to model
noise, analyze sensor performance, and evaluate mitigation techniques in
distributed quantum sensor networks (QSNs). It provides a user-friendly
interface for experimenting with different sensing configurations and
observing their impact on performance metrics such as Fisher Information
(FI) and Cramér--Rao Bound (CRB).

## Features

-   Multi-sensor quantum sensing simulation
-   Noise modeling (Markovian and configurable parameters)
-   Performance analysis using FI and CRB
-   Support for multiple mitigation techniques (e.g., ZNE, DD, etc.)
-   Interactive web-based dashboard (Flask-based)
-   Customizable sensor configurations

## Project Structure

    QuSenseSim/
    │── app.py
    │── requirements.txt
    │── README.md
    │── templates/
    │── static/
    │── data/

## Installation

1.  Clone the repository:

```{=html}
<!-- -->
```
    git clone https://github.com/Ratun11/QuSenseSim.git
    cd QuSenseSim

2.  Create a virtual environment:

```{=html}
<!-- -->
```
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    venv\Scripts\activate    # Windows

3.  Install dependencies:

```{=html}
<!-- -->
```
    pip install -r requirements.txt

## Usage

Run the simulator:

    python app.py

Then open your browser and go to:

    http://127.0.0.1:5000

## Key Concepts

-   **Fisher Information (FI):** Measures the amount of information a
    sensor provides about a parameter.
-   **Cramér--Rao Bound (CRB):** Lower bound on the variance of unbiased
    estimators.
-   **Noise Modeling:** Simulates realistic quantum noise effects.
-   **Mitigation Techniques:** Methods to reduce noise impact.


## Contribution

This project is developed as part of research in quantum sensing and
quantum machine learning.

## Contact

**Ratun Rahman**\
Email: rr0110@uah.edu

## License

This project is for academic and research purposes.
