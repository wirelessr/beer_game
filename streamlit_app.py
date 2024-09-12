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
            client = init_connection()
            db = MongoDB(client)
            st.session_state.game = GameRepo(game, db)
            st.session_state.game.newGame()

    if st.button("End Game", disabled=("game" not in st.session_state)):
        st.session_state.game.endGame()
        del st.session_state["game"]


if st.session_state.check_state("game"):
    gameRepo = st.session_state.game
    week = gameRepo.getDashboard()["week"]

    st.title(f"Week {week}")

    st.markdown('''Game Flow
1. Refresh
2. Adjust order number
3. Place Order
4. Wait shop player
5. Wait retailer player
6. Wait factory player
7. Next Week

⬇️ Start here
''')

    left, mid1, mid2, right = st.columns(4)
    left.button("Refresh")
    order = mid1.number_input(
        "Order",
        value=None,
        step=1,
        label_visibility="collapsed",
        placeholder="Order"
    )
    ordered = mid2.button("Place Order", disabled=(not order))
    if ordered:
        st.session_state.game.dispatch(order)
    if right.button("Next Week"):
        st.session_state.game.nextWeek()

    players = gameRepo.reloadPlayerStat()
    n_players = len(players)
    st.text(f"{n_players} players")

    cols = st.tabs(list(players.keys()) or ["No Player"])
    if n_players > 0:
        players = [(p, roles) for p, roles in players.items()]

        for idx, col in enumerate(cols):
            with col:
                p, roles = players[idx]

                PLAYERS = Template('''- $player
    - Shop: $shop $shop_purchased
    - Retailer: $retailer $retailer_purchased
    - Factory: $factory $factory_purchased
    - Cost: $total_cost
''')

                st.markdown(PLAYERS.substitute(
                    player=p,
                    shop='✅' if roles["shop"]["enabled"] else '❎',
                    retailer='✅' if roles["retailer"]["enabled"] else '❎',
                    factory='✅' if roles["factory"]["enabled"] else '❎',
                    shop_purchased='🔒' if roles["shop"]["purchased"] else '💸',
                    retailer_purchased='🔒' \
                          if roles["retailer"]["purchased"] else '💸',
                    factory_purchased='🔒' \
                        if roles["factory"]["purchased"] else '💸',
                    total_cost=sum([roles[r]["cost"] for r in roles])
                ))

                st.write(roles)
