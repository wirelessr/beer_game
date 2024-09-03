from string import Template
import streamlit as st

from beer_game.player_repo import PlayerRepo

st.set_page_config(page_title="Beer Player", page_icon="📈")

if "selectbox" not in st.session_state:
    def selectbox(k, ops):
        if not st.session_state.check_state(k):
            st.session_state[k] = st.selectbox(
                k,
                ops,
                index=None
            )
        else:
            st.selectbox(
                k,
                [],
                index=None,
                placeholder=st.session_state[k],
                disabled=True
            )

    st.session_state.selectbox = selectbox

st.markdown('''Game Flow
1. Refresh
2. Adjust order number
3. Place Order

⬇️ Start here
''')



with st.sidebar:
    st.session_state.selectbox("player_role", ("shop", "retailer", "factory"))
    st.session_state.text_input("player_key", True)

    enabled = (
        st.session_state.player_key == st.secrets["player"]["key"]
    )

    st.session_state.text_input("player_game")
    st.session_state.text_input("player_id")

    role = st.session_state.player_role
    game = st.session_state.player_game
    player = st.session_state.player_id

    if st.button("Join Game", disabled=(not player or not game or not role)):
        st.write(f"{game} joined")
        st.session_state.player = PlayerRepo(
            game,
            player,
            role,
            st.session_state.db
        )
        st.session_state.player.register()

    st.divider()
    st.session_state.selectbox("lang", ("zh", "en"))


def display_stat(stat):
    STAT = Template('''# $role 's Week $week
| Order | Inventoy | Out of Stock | Cost |
|------|-------| ----- | ----- |
|$order | $inventory | $out_of_stock | $cost |
''')
    return STAT.substitute(stat | {'role': st.session_state.role.capitalize()})


def tell_story(stat, lang='zh'):
    STORY_I18N = {
        'zh': '''你本週到貨 $delivery 加上原有庫存 $inventory_this_week 共可賣 $can_sell

本週進單 $order 加上積壓貨單 $out_of_stock_this_week 共需賣 $should_sell

因此，賣出 $sell 並使庫存為 $inventory

最終，總成本是 $cost''',
        'en': '''You have $delivery new arrivals this week plus $inventory_this_week original inventory, totaling $can_sell available for sale

This week's orders $order plus backlogged orders $out_of_stock_this_week sum up to $should_sell that need to be sold

Therefore, you sell $sell and your inventory becomes $inventory

Finally, the total cost is $cost'''
    }
    STORY = Template(STORY_I18N.get(lang) or STORY_I18N['zh'])
    return STORY.substitute(stat)

if st.session_state.check_state("player"):
    left, mid1, mid2, _ = st.columns(4)

    left.button("Refresh")
    order = mid1.number_input(
        "Order",
        value=None,
        step=1,
        label_visibility="collapsed",
        placeholder="Order"
    )
    if mid2.button("Place Order", disabled=(not order)):
        st.session_state.player.purchase(order)
        st.write(f"{order} order placed")

    stat = st.session_state.player.reloadStat()
    st.markdown(display_stat(stat))
    st.write(tell_story(stat))