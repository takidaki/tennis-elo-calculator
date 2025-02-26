import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

# Function to fetch and parse Elo ratings
def fetch_elo_ratings(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all tables in the HTML
    tables = soup.find_all('table')
    
    # Use the second table (index 1) if it exists
    df = pd.read_html(str(tables[1]))[0] if len(tables) > 1 else pd.DataFrame()  # Read the second table into a DataFrame
    return df

# Function to calculate win probability
def calculate_win_probability(elo_a, elo_b):
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

# Streamlit app
st.set_page_config(page_title="Tennis Elo Win Probability Calculator", layout="wide", page_icon="https://example.com/path/to/tennis_ball_icon.png")  # Replace with actual image URL
st.title("Tennis Elo Calculator")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stSelectbox {
        margin-bottom: 20px;
    }
    .stButton {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .stButton:hover {
        background-color: #45a049;
    }
    .header {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    .card {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        background-color: #f9f9f9;
    }
    .card h3 {
        margin: 0;
        font-size: 20px;
        color: #333;
    }
    .card p {
        font-size: 18px;
        color: #555;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for user selection
option = st.sidebar.selectbox("Select Ratings:", ["ATP Ratings", "WTA Ratings"])

# Fetch Elo ratings based on user selection
if option == "ATP Ratings":
    url = "https://tennisabstract.com/reports/atp_elo_ratings.html"
    elo_data = fetch_elo_ratings(url)
elif option == "WTA Ratings":
    url = "https://tennisabstract.com/reports/wta_elo_ratings.html"
    elo_data = fetch_elo_ratings(url)

# Store the fetched data as a variable without displaying it
# st.dataframe(elo_data)  # Commented out to prevent displaying the table

# Display a message indicating the selected ratings
st.write(f"Current {option} Elo Ratings fetched successfully!")

# Create three columns for court surface selection and player selection
col1, col2, col3 = st.columns(3)

with col3:
    st.markdown("<div class='header'>Select Court Surface:</div>", unsafe_allow_html=True)
    court_surface = st.selectbox("Court Surface", ["Hard", "Clay", "Grass"], key="court_surface")

with col1:
    st.markdown("<div class='header'>Select Player 1:</div>", unsafe_allow_html=True)
    search_player1 = st.text_input("Search Player 1", "")
    
    # Filter the player list based on the search input, ensuring we only check strings
    filtered_players1 = [
        player for player in elo_data['Player'].tolist() 
        if isinstance(player, str) and search_player1.lower() in player.lower()
    ]
    
    # Use selectbox with filtered player list
    player1 = st.selectbox("Player 1", filtered_players1, key="player1")
    
    if player1:
        player1_elo = elo_data.loc[elo_data['Player'] == player1, 
            f"hElo" if court_surface == "Hard" else "cElo" if court_surface == "Clay" else "gElo"].values[0]
        st.write(f"Elo Rating: **{player1_elo}**")

with col2:
    st.markdown("<div class='header'>Select Player 2:</div>", unsafe_allow_html=True)
    search_player2 = st.text_input("Search Player 2", "")
    
    # Filter the player list based on the search input, ensuring we only check strings
    filtered_players2 = [
        player for player in elo_data['Player'].tolist() 
        if isinstance(player, str) and search_player2.lower() in player.lower()
    ]
    
    # Use selectbox with filtered player list
    player2 = st.selectbox("Player 2", filtered_players2, key="player2")
    
    if player2:
        player2_elo = elo_data.loc[elo_data['Player'] == player2, 
            f"hElo" if court_surface == "Hard" else "cElo" if court_surface == "Clay" else "gElo"].values[0]
        st.write(f"Elo Rating: **{player2_elo}**")

# Add a dropdown menu for margin selection with range 0-14
margin = st.selectbox("Select Margin (%):", list(range(15)), key="margin")  # Updated range from 0 to 14

# Calculate and display win probability based on selected players and their Elo ratings
if player1 and player2:
    win_prob_player1 = calculate_win_probability(player1_elo, player2_elo)
    win_prob_player2 = calculate_win_probability(player2_elo, player1_elo)
    
    # Adjust odds based on the selected margin
    margin_decimal = margin / 100
    win_odds_player1 = (1 / win_prob_player1) * (1 - margin_decimal)
    win_odds_player2 = (1 / win_prob_player2) * (1 - margin_decimal)

    st.write("**Win Probability:**")
    
    # Determine which player has a higher probability and set colors accordingly
    if win_prob_player1 > win_prob_player2:
        st.markdown(f"<p style='color: green;'><strong>{player1}</strong> has a {win_prob_player1:.2%} chance of winning against <strong style='color: black;'>{player2}</strong>.</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: red;'><strong>{player2}</strong> has a {win_prob_player2:.2%} chance of winning against <strong style='color: black;'>{player1}</strong>.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p style='color: red;'><strong>{player1}</strong> has a {win_prob_player1:.2%} chance of winning against <strong style='color: black;'>{player2}</strong>.</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: green;'><strong>{player2}</strong> has a {win_prob_player2:.2%} chance of winning against <strong style='color: black;'>{player1}</strong>.</p>", unsafe_allow_html=True)

# Custom CSS for interactive card styling
st.markdown(
    """
    <style>
    .card {
        border: 1px solid #ccc;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        background-color: #f9f9f9;
        transition: transform 0.2s, box-shadow 0.2s; /* Smooth transition for hover effects */
    }
    .card:hover {
        transform: scale(1.05); /* Slightly enlarge the card on hover */
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); /* Add shadow on hover */
    }
    .card h3 {
        margin: 0;
        font-size: 20px;
        color: #333;
    }
    .card p {
        font-size: 18px;
        color: #555;
    }
    .court-image {
        width: 100%; /* Make the image responsive */
        height: auto; /* Maintain aspect ratio */
        border-radius: 5px; /* Optional: round the corners of the image */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define a function to get the court image URL based on the selected surface
def get_court_image_url(court_surface):
    if court_surface == "Hard":
        return "images/hard-court.jpg"  # Replace with actual URL
    elif court_surface == "Clay":
        return "images/clay-court.jpg"  # Replace with actual URL
    elif court_surface == "Grass":
        return "images/grass-court.jpg"  # Replace with actual URL
    return ""

# Display Match Odds in card format
st.write("**Match Odds:**")

col4, col5 = st.columns(2)

# Get the court image URL based on the selected surface
court_image_url = get_court_image_url(court_surface)

with col4:
    st.markdown(f"""
    <div class='card'>
        <img src='{court_image_url}' class='court-image' alt='Court Image'>
        <h3>{player1}</h3>
        <p>Odds: {win_odds_player1:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='card'>
        <img src='{court_image_url}' class='court-image' alt='Court Image'>
        <h3>{player2}</h3>
        <p>Odds: {win_odds_player2:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

