import streamlit as st
from functions import generate_card_from_description, parse_card_text,\
    judge_battle, update_player_stats_from_gpt_output, judge_final_round
from functions import generate_image_from_appearance

# --- UI 角色卡展示 ---
def display_character_card(card, player_name):
    st.markdown(f"### {player_name} - {card.get('Name', 'N/A')}")
    st.markdown(f"**HP:** {card.get('HP', 'N/A')}")
    st.markdown(
        f"**Attack:** {card.get('Attack', 'N/A')}  |  **Defense:** {card.get('Defense', 'N/A')}  |  **Energy:** {card.get('Energy', 'N/A')}")

    # 显示生成的角色图片
    image_url = card.get('Image')
    if image_url:
        st.image(image_url, caption=f"{player_name}'s Appearance", use_container_width=True)


# --- Streamlit App ---
st.title("⚔️ Fantasy Battle Arena")

# 初始化 session_state
if "player_a_card" not in st.session_state:
    st.session_state.player_a_card = {}
if "player_b_card" not in st.session_state:
    st.session_state.player_b_card = {}
if "battle_round" not in st.session_state:
    st.session_state.battle_round = 1
if "final_ready" not in st.session_state:
    st.session_state.final_ready = False

# --- Step 1: 创建角色 ---

# Step 1: Create Your Characters
if not (st.session_state.player_a_card and st.session_state.player_b_card):
    st.header("Step 1: Create Your Characters")
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.player_a_card:
            desc_a = st.text_area("Player A Description:")
            if st.button("Generate Player A Card"):
                card_a_raw = generate_card_from_description(desc_a)
                st.session_state.player_a_card = parse_card_text(card_a_raw)

                # --- 新增：生成图片 ---
                appearance_a = st.session_state.player_a_card.get('Appearance', '')
                image_url_a = generate_image_from_appearance(appearance_a)
                st.session_state.player_a_card['Image'] = image_url_a

                st.success("Player A Card Generated!")

    with col2:
        if not st.session_state.player_b_card:
            desc_b = st.text_area("Player B Description:")
            if st.button("Generate Player B Card"):
                card_b_raw = generate_card_from_description(desc_b)
                st.session_state.player_b_card = parse_card_text(card_b_raw)

                # --- 新增：生成图片 ---
                appearance_b = st.session_state.player_b_card.get('Appearance', '')
                image_url_b = generate_image_from_appearance(appearance_b)
                st.session_state.player_b_card['Image'] = image_url_b

                st.success("Player B Card Generated!")

# --- Step 2: 角色展示 + 战斗 ---
if st.session_state.player_a_card and st.session_state.player_b_card:
    st.markdown("---")
    st.header("Character Overview")
    col1, col2 = st.columns(2)
    with col1:
        display_character_card(st.session_state.player_a_card, "Player A")
    with col2:
        display_character_card(st.session_state.player_b_card, "Player B")

    # --- 普通战斗回合 ---
    if st.session_state.battle_round <= 2:
        st.markdown("---")
        st.header(f"Step 2: Battle Round {st.session_state.battle_round}")
        player_a_action = st.text_input(f"Player A Action (Round {st.session_state.battle_round}):", key=f"a_action_{st.session_state.battle_round}")
        player_b_action = st.text_input(f"Player B Action (Round {st.session_state.battle_round}):", key=f"b_action_{st.session_state.battle_round}")

        if st.button(f"Execute Round {st.session_state.battle_round}"):
            result = judge_battle(player_a_action, player_b_action, st.session_state.player_a_card, st.session_state.player_b_card)
            st.text_area(f"Round {st.session_state.battle_round} Result", result, height=300)
            st.session_state.player_a_card, st.session_state.player_b_card = update_player_stats_from_gpt_output(result, st.session_state.player_a_card, st.session_state.player_b_card)
            st.session_state.battle_round += 1

            if st.session_state.battle_round > 2:
                st.session_state.final_ready = True

# --- Step 3: 决胜轮 ---
if st.session_state.final_ready:
    st.markdown("---")
    st.header("Step 3: Final Round")
    final_action_a = st.text_input("Player A Ultimate:")
    final_action_b = st.text_input("Player B Ultimate:")

    if st.button("Execute Final Round"):
        final_result = judge_final_round(final_action_a, final_action_b, st.session_state.player_a_card, st.session_state.player_b_card)
        st.text_area("Final Battle Result", final_result, height=300)
