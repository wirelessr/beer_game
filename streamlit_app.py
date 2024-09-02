import streamlit as st
from string import Template
import pymongo
from pymongo.server_api import ServerApi

from beer_game.game_repo import GameRepo
from beer_game.mongodb_adapter import MongoDB

st.set_page_config(
    page_title="Beer Game",
    page_icon="🍺",
)

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(
        st.secrets["mongo"]["uri"],
        server_api=ServerApi('1')
        )

client = init_connection()

if "db" not in st.session_state:
    st.session_state.db = MongoDB(client)
enabled = False
game = None
gameRepo = None


text = 'world'
PLAYERS = Template('''# Player
- $player
    - Shop: $shop
    - Retailer: $retailer
    - Factory: $factory
''')

with st.sidebar:
    st.title("Game Master")

    enabled = (
        st.text_input("Key", type="password") == st.secrets["admin"]["key"]
    )

    game = st.text_input("Game ID", disabled=not enabled)
    if st.button("New Game", disabled=(not enabled or game == "")):
        st.write(f"{game} started")
        if "game" not in st.session_state:
            st.session_state.game = GameRepo(game, st.session_state.db)
            st.session_state.game.newGame()

    if st.button("End Game", disabled=("game" not in st.session_state)):
        del st.session_state["game"]

if "game" in st.session_state:
    gameRepo = st.session_state.game
    players = gameRepo.retrievePlayer()
    st.text(f"{len(players)} players")

    for p, roles in players.items():
        st.markdown(PLAYERS.substitute(
            player=p,
            shop='✅' if roles["shop"] else '❎',
            retailer='✅' if roles["retailer"] else '❎',
            factory='✅' if roles["factory"] else '❎',
        ))