
import streamlit as st
import pandas as pd
from collections import Counter
import random

def build_and_predict(df, selected_day):
    df['תאריך'] = pd.to_datetime(df['תאריך'], format='%d/%m/%Y')
    df['weekday'] = df['תאריך'].dt.day_name()

    reverse_day_map = {"שלישי": "Tuesday", "חמישי": "Thursday", "שבת": "Saturday"}
    selected_day_eng = reverse_day_map[selected_day]

    df_filtered = df[df['weekday'] == selected_day_eng]

    numbers = []
    strong_nums = df_filtered['המספר החזק/נוסף'].values.tolist()

    for col in ['1', '2', '3', '4', '5', '6']:
        numbers.extend(df_filtered[col].values.tolist())

    lotto_counts = Counter(numbers)
    strong_counts = Counter(strong_nums)

    hot = [num for num, _ in lotto_counts.most_common(20) if num <= 37]
    cold = [num for num, _ in lotto_counts.most_common()[-20:] if num <= 37]
    medium = [num for num in range(1, 38) if num not in hot and num not in cold]

    hot_strong = [num for num, _ in strong_counts.most_common(3) if num <= 7]

    pairs = Counter()
    for i in range(len(df_filtered) - 1):
        row_current = df_filtered.iloc[i]
        row_next = df_filtered.iloc[i + 1]
        current_numbers = row_current[['1', '2', '3', '4', '5', '6']].tolist()
        next_numbers = row_next[['1', '2', '3', '4', '5', '6']].tolist()
        for num in current_numbers:
            for next_num in next_numbers:
                pairs[(num, next_num)] += 1

    def get_followers(last_draw_numbers):
        followers = Counter()
        for num in last_draw_numbers:
            for key, val in pairs.items():
                if key[0] == num:
                    followers[key[1]] += val
        return [num for num, _ in followers.most_common(5)]

    last_draw = df_filtered.iloc[0][['1', '2', '3', '4', '5', '6']].tolist()
    followers = get_followers(last_draw)

    predictions = []
    for _ in range(14):
        prediction_pool = (
            random.sample(hot, 3) +
            random.sample(medium, 1) +
            random.sample(cold, 1) +
            random.sample(followers, 1)
        )
        prediction = sorted(set(prediction_pool))[:6]
        while len(prediction) < 6:
            prediction.append(random.choice(medium))
        strong_pick = random.choices(hot_strong + [random.randint(1, 7)], weights=[6, 6, 6, 2])[0]
        predictions.append((prediction, strong_pick))

    return predictions

st.set_page_config(page_title='אלגוריתם לוטו חכם - ליביו הוליביה', layout='centered')
st.title('🎯 אלגוריתם לוטו חכם במיוחד + מספר חזק')

uploaded_file = st.file_uploader('העלה קובץ CSV של תוצאות לוטו:')
selected_day = st.selectbox('בחר את יום ההגרלה:', ['שלישי', 'חמישי', 'שבת'])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, encoding='windows-1255')
    if st.button('צור תחזיות חכמות'):
        predictions = build_and_predict(df, selected_day)
        for i, (nums, strong) in enumerate(predictions):
            st.write(f'תוצאה {i+1}: {", ".join(map(str, nums))} | מספר חזק: {strong}')

st.markdown("""<hr>המערכת מבוססת על סטטיסטיקה, ניתוח דפוסי רצף, חום/קור, והתאמה ליום הגרלה.  
נבנה במיוחד עבור ליביו הוליביה בסטייל!""", unsafe_allow_html=True)
