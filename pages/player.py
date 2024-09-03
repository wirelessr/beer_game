import streamlit as st

from beer_game.player_repo import PlayerRepo

st.set_page_config(page_title="Beer Player", page_icon="📈")

with st.sidebar:
    if not st.session_state.check_state("role"):
        st.session_state.role = st.selectbox(
            "player_role",
            ("shop", "retailer", "factory"),
            index=None
        )
    else:
        st.selectbox(
            "Game Role",
            [],
            index=None,
            placeholder=st.session_state.role,
            disabled=True
        )

    st.session_state.text_input("player_key", True)

    enabled = (
        st.session_state.player_key == st.secrets["player"]["key"]
    )

    st.session_state.text_input("player_game")
    st.session_state.text_input("player_id")

    role = st.session_state.role
    game = st.session_state.player_game
    player = st.session_state.player_id

    if st.button("Join Game", disabled=(not player or not game or not role)):
        st.write(f"{game} joined")
        if "player" not in st.session_state:
            st.session_state.player = PlayerRepo(
                game,
                player,
                role,
                st.session_state.db
            )
            st.session_state.player.register()

if st.session_state.check_state("player"):
    stat = st.session_state.player.reloadStat()
    st.code(stat, language="json")