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

text = 'world'
PLAYERS = Template('''# Player
- $player
    - Shop: $shop
    - Retailer: $retailer
    - Factory: $factory
''')

if "check_state" not in st.session_state:
    st.session_state.check_state = lambda k: k in st.session_state \
        and st.session_state[k]

if "text_input" not in st.session_state:
    def text_input(k, pwd=False):
        if not st.session_state.check_state(k):
            st.session_state[k] = st.text_input(
                k,
                type="password" if pwd else "default"
            )
        else:
            st.text_input(
                k,
                type="password" if pwd else "default",
                value=st.session_state[k],
                disabled=True
            )

    st.session_state.text_input = text_input

with st.sidebar:
    st.title("Game Master")

    st.session_state.text_input("admin_key", True)

    enabled = (
        st.session_state.admin_key == st.secrets["admin"]["key"]
    )

    st.session_state.text_input("game_id", False)

    game = st.session_state.game_id

    if st.button("New Game", disabled=(not enabled or not game)):
        st.write(f"{game} started")
        if "game" not in st.session_state:
            st.session_state.game = GameRepo(game, st.session_state.db)
            st.session_state.game.newGame()

    if st.button("End Game", disabled=("game" not in st.session_state)):
        del st.session_state["game"]


if st.session_state.check_state("game"):
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