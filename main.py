import streamlit as st
import torch
import torch.nn as nn
import torch.nn.functional as F
import requests
import py3Dmol
import streamlit.components.v1 as components
from stmol import showmol

st.set_page_config(
    page_title="AMPForge - Antimicrobial Peptide Generator",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #ffffff, #cccccc, #888888);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .sequence-display {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #ffffff;
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        letter-spacing: 2px;
        word-break: break-all;
        color: #ffffff;
    }
    
    .metric-card {
        background-color: #1a1a1a;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
        border: 1px solid #ffffff;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ffffff, #cccccc);
        color: #000000;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 300px;
        margin: 0 auto;
        display: block;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255, 255, 255, 0.3);
        background: linear-gradient(45deg, #cccccc, #888888);
        color: #000000;
    }
    
    /* Center buttons */
    .stButton {
        display: flex;
        justify-content: center;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Creating Constants:

AMINO_ACIDS_REV = {
    0: 'N', 1: 'L', 2: 'V', 3: 'S', 4: 'G', 5: 'I', 6: 'E', 7: 'A',
    8: 'R', 9: 'K', 10: 'Y', 11: 'Q', 12: 'H', 13: 'C', 14: 'P', 15: 'F',
    16: 'T', 17: 'W', 18: 'D', 19: 'M', 20: '_'
}

# Creating VariationalAutoEncoder:

class VariationalAutoEncoder(nn.Module):
    def __init__(self, input_dim=1050, h_dim=100, z_dim=10):
        super().__init__()
        self.input_dim = input_dim
        self.h_dim = h_dim
        self.z_dim = z_dim

        # Creating Encoder:
        self.i_2h = nn.Linear(input_dim, h_dim)
        self.h_2mu = nn.Linear(h_dim, z_dim)
        self.h_2sigma = nn.Linear(h_dim, z_dim)

        # Creating Decoder:
        self.z_2h = nn.Linear(z_dim, h_dim)
        self.h_2i = nn.Linear(h_dim, input_dim)

    def encode(self, x):
        x = x.view(-1, self.input_dim)
        h = F.relu(self.i_2h(x))
        mu, sigma = self.h_2mu(h), self.h_2sigma(h)
        return mu, sigma

    def decode(self, z):
        z = z.view(-1, self.z_dim)
        h = F.relu(self.z_2h(z))
        return torch.sigmoid(self.h_2i(h))

    def forward(self, x):
        mu, sigma = self.encode(x)
        std = torch.exp(0.5 * sigma)
        eps = torch.randn_like(std)
        z = mu + sigma * eps
        x_reconstructed = self.decode(z)
        return x_reconstructed, mu, sigma

# Loading Model:

@st.cache_resource
def load_model():
    """Load the pre-trained VAE model"""
    model = VariationalAutoEncoder()

    try:
        model.load_state_dict(torch.load(
            'AMPForge_model.pth', map_location='cpu'))
        model.eval()
        print("Model loaded successfully!")
        return model
    except FileNotFoundError:
        st.error("Model file not found. Please check the file path.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

# Sequence Generation:

def generate_sequence(model):
    """Generate a new AMP sequence using the VAE"""
    with torch.inference_mode():

        noise = torch.randn((50, 21))

        x, mu, sigma = model(noise)
        x = x.view(50, 21)

        sequence = ""
        for i in range(50):
            acid = AMINO_ACIDS_REV.get(torch.argmax(x[i]).item())
            if acid == '_':
                break
            else:
                sequence += acid

    return sequence

# Sequence Visualization:

def get_protein_structure(sequence):
    """Get PDB structure from ESMAtlas API"""
    try:
        url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
        response = requests.post(url, data=sequence, timeout=30)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except:
        return None

def create_3d_visualization(pdb_string):
    """Create 3D molecular visualization"""
    view = py3Dmol.view(width=800, height=600)
    view.addModel(pdb_string, "pdb")
    view.setStyle({"cartoon": {"color": "spectrum"}})
    view.setBackgroundColor("#0e1117")
    view.zoomTo()
    return view

# Main App

def main():

    st.markdown('<h1 class="main-header">🧬 AMPForge</h1>',
                unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #ffffff; margin-bottom: 3rem;">AI-Powered Antimicrobial Peptide Generator</p>', unsafe_allow_html=True)

    if 'sequence' not in st.session_state:
        st.session_state.sequence = None
    if 'pdb_structure' not in st.session_state:
        st.session_state.pdb_structure = None

    model = load_model()
    
    if st.button("Generate New AMP Sequence", key="generate_btn"):
        with st.spinner("Generating novel antimicrobial peptide..."):
            st.session_state.sequence = generate_sequence(model)
            st.session_state.pdb_structure = None

    if st.session_state.sequence:
        st.markdown("---")

        st.markdown("### Generated Sequence")
        st.markdown(
            f'<div class="sequence-display">{st.session_state.sequence}</div>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #ffffff; margin: 0;">Length</h3>
                <p style="font-size: 1.5rem; margin: 0;">{len(st.session_state.sequence)}</p>
            </div>
            ''', unsafe_allow_html=True)

        with col2:
            charge = st.session_state.sequence.count('K') + st.session_state.sequence.count(
                'R') - st.session_state.sequence.count('D') - st.session_state.sequence.count('E')
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #ffffff; margin: 0;">Net Charge</h3>
                <p style="font-size: 1.5rem; margin: 0;">{charge:+d}</p>
            </div>
            ''', unsafe_allow_html=True)

        with col3:
            hydrophobic = sum([st.session_state.sequence.count(aa)
                              for aa in 'AILMFWYV'])
            hydrophobic_ratio = hydrophobic / \
                len(st.session_state.sequence) * 100
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #ffffff; margin: 0;">Hydrophobic</h3>
                <p style="font-size: 1.5rem; margin: 0;">{hydrophobic_ratio:.1f}%</p>
            </div>
            ''', unsafe_allow_html=True)

        with col4:
            cys_count = st.session_state.sequence.count('C')
            st.markdown(f'''
            <div class="metric-card">
                <h3 style="color: #ffffff; margin: 0;">Cysteines</h3>
                <p style="font-size: 1.5rem; margin: 0;">{cys_count}</p>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 3D Structure Prediction")

        if st.button("Generate 3D Structure", key="structure_btn"):
            with st.spinner("Predicting 3D structure with ESMFold..."):
                st.session_state.pdb_structure = get_protein_structure(
                    st.session_state.sequence)

        if st.session_state.pdb_structure:
            st.markdown("#### Interactive 3D Visualization")
            view = create_3d_visualization(st.session_state.pdb_structure)
            showmol(view, height=600, width=800)

        elif st.session_state.pdb_structure is not None:
            st.error("Unable to generate 3D structure. Please try again.")

    else:

        st.markdown("""
        <div style="text-align: center; padding: 3rem; background-color: #262730; border-radius: 15px; margin: 2rem 0;">
            <h3 style="color: #ffffff;">Welcome to AMPForge!</h3>
            <p style="color: #ffffff; font-size: 1.1rem;">Generate novel antimicrobial peptide sequences using advanced AI.</p>
            <p style="color: #ffffff;">Click the button above to create your first AMP sequence.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #ffffff; padding: 1rem;">
        <p> Powered by Variational Autoencoders & ESMFold | Built with Streamlit</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
