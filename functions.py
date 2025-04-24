import openai
import re
import streamlit as st
# Initialize OpenAI Client
# with open('open_ai_key.txt', 'r', encoding='utf-8') as file:
#     openai_key = file.readline().strip()
# client = openai.OpenAI(api_key=openai_key)
openai_key = st.secrets["OPENAI_API_KEY"]
client = openai.OpenAI(api_key=openai_key)


# --- Parse Character Card text into dict ---
def parse_card_text(card_text):
    card = {}
    lines = card_text.strip().split("\n")
    abilities = []
    for line in lines:
        if line.startswith("Name:"):
            card['Name'] = line.replace("Name:", "").strip()
        elif line.startswith("Appearance:"):
            card['Appearance'] = line.replace("Appearance:", "").strip()
        elif line.startswith("HP:"):
            card['HP'] = line.replace("HP:", "").strip()
        elif line.startswith("Attack:"):
            card['Attack'] = line.replace("Attack:", "").strip()
        elif line.startswith("Defense:"):
            card['Defense'] = line.replace("Defense:", "").strip()
        elif line.startswith("Energy:"):
            card['Energy'] = line.replace("Energy:", "").strip()
        elif line.startswith("- Ability"):
            abilities.append(line.replace("-", "").strip())
        elif line.startswith("Ultimate Ability:"):
            card['Ultimate Ability'] = line.replace("Ultimate Ability:", "").strip()
    card['Special Abilities'] = abilities
    return card

# --- Generate Character Card ---
def generate_card_from_description(description):
    prompt = f"""
    Generate a detailed character card based on this description:

    - Name
    - Appearance
    - HP (6-15)
    - Attack (1-6)
    - Defense (1-6)
    - Energy (1-6)
    - Special Abilities (2 abilities)
    - Ultimate Ability (1 powerful skill)

    Description: "{description}"

    Output format:

    Name: 
    Appearance:
    HP:
    Attack:
    Defense:
    Energy:
    Special Abilities:
    - Ability 1:
    - Ability 2:
    Ultimate Ability:
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content


# --- Generate Image from Appearance ---
def generate_image_from_appearance(appearance_text):
    response = client.images.generate(
        model="dall-e-3",
        prompt=appearance_text,
        size="1024x1024",  # 标准分辨率
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    return image_url
# --- Judge a battle round ---
def judge_battle(player_a_action, player_b_action, player_a_card, player_b_card):
    prompt = f"""
    You are the battle judge in a fantasy combat game...

    ### Player A Character:
    Name: {player_a_card['Name']}
    HP: {player_a_card['HP']}
    Attack: {player_a_card['Attack']}
    Defense: {player_a_card['Defense']}
    Energy: {player_a_card['Energy']}
    Special Abilities: {', '.join(player_a_card['Special Abilities'])}

    ### Player B Character:
    Name: {player_b_card['Name']}
    HP: {player_b_card['HP']}
    Attack: {player_b_card['Attack']}
    Defense: {player_b_card['Defense']}
    Energy: {player_b_card['Energy']}
    Special Abilities: {', '.join(player_b_card['Special Abilities'])}

    ### Actions this turn:
    - Player A Action: "{player_a_action}"
    - Player B Action: "{player_b_action}"

    ### Output Format:

    Outcome:
    - Player A: [Result], Visual Effect: [Attack/Shield/Weak]
    - Player B: [Result], Visual Effect: [Attack/Shield/Weak]

    Updated Stats:
    - Player A HP: 
    - Player B HP: 
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content

# --- Update HP based on GPT output ---
def update_player_stats_from_gpt_output(gpt_output, player_a_card, player_b_card):
    hp_pattern = r"Updated Stats:\s*- Player A HP: (\d+)\s*- Player B HP: (\d+)"
    match = re.search(hp_pattern, gpt_output)
    if match:
        player_a_card['HP'] = match.group(1)
        player_b_card['HP'] = match.group(2)
    return player_a_card, player_b_card

# --- Final Round Judgement ---
def judge_final_round(player_a_ultimate_action, player_b_ultimate_action, player_a_card, player_b_card):
    prompt = f"""
    This is the FINAL ROUND of a fantasy combat game. Each player will use their most powerful ultimate skill...

    ### Player A Character:
    Name: {player_a_card['Name']}
    Attack: {player_a_card['Attack']}
    Defense: {player_a_card['Defense']}
    Energy: {player_a_card['Energy']}
    Ultimate Ability: {player_a_card['Ultimate Ability']}

    ### Player B Character:
    Name: {player_b_card['Name']}
    Attack: {player_b_card['Attack']}
    Defense: {player_b_card['Defense']}
    Energy: {player_b_card['Energy']}
    Ultimate Ability: {player_b_card['Ultimate Ability']}

    ### Final Actions:
    - Player A Ultimate: "{player_a_ultimate_action}"
    - Player B Ultimate: "{player_b_ultimate_action}"

    ### Output Format:

    Final Outcome:
    - Player A: Visual Effect: [Attack/Shield/Weak]
    - Player B: Visual Effect: [Attack/Shield/Weak]

    Cinematic Description:
    [What happened in this epic final round...]

    Winner: [Player A / Player B]
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content
