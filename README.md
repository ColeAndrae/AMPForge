<img width="1641" height="680" alt="image" src="https://github.com/user-attachments/assets/d90cac75-74de-4b37-9a01-9d93b2eb1c84" />

AMPForge - Antimicrobial Peptide Generator
AMPForge is an AI-powered web application that generates novel antimicrobial peptide (AMP) sequences and predicts their 3D structures. The application uses a Variational Autoencoder (VAE) to create new peptide sequences and the ESMFold model to predict their structural conformation.

Features
AI-Powered Sequence Generation: Create unique antimicrobial peptide sequences using a VAE model trained on known AMPs.

3D Structure Prediction: Visualize the predicted 3D structure of the generated peptide using the powerful ESMFold model.

Interactive Visualization: Explore the protein structure directly in your browser with an interactive 3D viewer.

Real-time Metrics: Instantly view key properties of the generated peptide, such as length, net charge, and hydrophobicity.

Technologies Used
Streamlit: For building the interactive web application interface.

PyTorch: The deep learning framework used to build and train the VAE model.

Requests: A Python library for making HTTP requests to external APIs (e.g., ESMFold).

stmol: A Streamlit component to embed py3Dmol for interactive 3D molecular visualization.

uv: A fast and modern package installer for Python, used for dependency management.

Getting Started
Prerequisites
To run this application locally, you will need:

Python 3.10 or higher

Installation
Clone the repository:

Bash

git clone https://github.com/ColeAndrae/ampforge.git
cd ampforge
Create a virtual environment and activate it:

Bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
Install the required dependencies using uv (or pip if uv is not available):

Bash

pip install -r requirements.txt
Running the App
Once the dependencies are installed, you can start the Streamlit application from the terminal:

Bash

streamlit run main.py
The app will open automatically in your default web browser.

Contributing
Contributions are welcome! If you find a bug or have an idea for a new feature, please open an issue or submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments
The Streamlit community for the amazing framework.

The creators of the ESMFold model for the powerful protein structure prediction.
