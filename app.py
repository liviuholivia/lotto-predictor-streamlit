import streamlit as st
import pandas as pd
from collections import Counter
import random

def build_and_predict(df, selected_day):
    df['תאריך'] = pd.to_datetime(df['תאריך'], format='%d/%m/%Y')
    df['weekday'] = df['תאריך'].dt.day_name()

    reverse_day_map = {"שלישי": "Tuesday", "חמישי": "Thursday", "שבת": "Saturday"}
    selected_day_eng = reverse_day_map[selected_day]

    df_filtered = df[df['weekday'] == selected_day_eng].head(50)  # מתמקד ב-50 ההגרלות האחרונות

    numbers = []
    strong_nums = df_filtered['המספר החזק/נוסף'].values.tolist()

    for col in ['1', '2', '3', '4', '5', '6']:
        numbers.extend(df_filtered[col].values.tolist())

    lotto_counts = Counter(numbers)
    strong_counts = Counter(strong_nums)

    hot = [num for num, _ in lotto_counts.most_common(15) if num <= 37]
    cold = [num for num, _ in lotto_counts.most_common()[-15:] if num <= 37]
    medium = [num for num in range(1, 38) if num not in hot and num not in cold]

    # זיהוי זוגות עוקבים חזקים
    consecutive_pairs = Counter()
    rows = df_filtered[['1', '2', '3', '4', '5', '6']].values.tolist()
    for row in rows:
        row_sorted = sorted(row)
        for i in range(len(row_sorted)-1):
            if row_sorted[i+1] - row_sorted[i] == 1:
                consecutive_pairs[(row_sorted[i], row_sorted[i+1])] += 1

    frequent_pairs = [pair for pair, count in consecutive_pairs.items() if count >= 2]

    # בחירת מספרים חזקים שחזרו הרבה פעמים
    hot_strong = [num for num, count in strong_counts.most_common(5) if num <= 7 and count > 2]

    def is_balanced(numbers_list):
        low = sum(1 for n in numbers_list if n <= 19)
        high = sum(1 for n in numbers_list if n > 19)
        even = sum(1 for n in numbers_list if n % 2 == 0)
        odd = sum(1 for n in numbers_list if n % 2 != 0)
        return (2 <= low <= 4) and (2 <= high <= 4) and (2 <= even <= 4) and (2 <= odd <= 4)

    predictions = []
    while len(predictions) < 14:
        prediction_pool = (
            random.sample(hot, 3) +
            random.sample(medium, 1) +
            random.sample(cold, 1)
        )
        # הוספת זוג עוקב מתוך הזוגות החזקים אם אפשר
        if frequent_pairs:
            chosen_pair = random.choice(frequent_pairs)
            prediction_pool.extend(chosen_pair)

        prediction = list(set(prediction_pool))
        while len(prediction) < 6:
            prediction.append(random.choice(medium))
        prediction = prediction[:6]
        prediction.sort(reverse=True)

        if is_balanced(prediction):
            strong_pick = random.choices(hot_strong + [random.randint(1, 7)], weights=[6]*len(hot_strong) + [2])[0]
            predictions.append((prediction, strong_pick))

    return predictions

st.set_page_config(page_title='אלגוריתם לוטו סופר-חכם - ליביו הוליביה', layout='centered')

st.markdown("""<style>
body {
    background: linear-gradient(135deg, #000000, #1a1a1a);
    color: gold;
}
.stButton > button {
    background-color: gold;
    color: black;
    border-radius: 8px;
    border: 1px solid gold;
    font-weight: bold;
    transition: 0.3s;
}
.stButton > button:hover {
    background-color: #ffcc00;
    color: black;
    transform: scale(1.05);
}
.prediction-card {
    background-color: rgba(51, 51, 51, 0.9);
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 12px;
    color: gold;
    font-weight: bold;
    border: 1px solid gold;
    box-shadow: 0px 0px 25px rgba(255, 215, 0, 0.4);
}
#logo-img {
    max-width: 150px;
    display: block;
    margin: auto;
}
</style>""", unsafe_allow_html=True)

st.image('logo.png', use_container_width=False, width=150)
st.title('🎯 אלגוריתם לוטו חכם במיוחד – מבוסס עומק, דפוסי רצף, זוגות עוקבים ומספרים יציבים')

uploaded_file = st.file_uploader('📂 העלה קובץ CSV של תוצאות לוטו:')
selected_day = st.selectbox('📅 בחר את יום ההגרלה:', ['שלישי', 'חמישי', 'שבת'])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='windows-1255')
        if st.button('✨ צור תחזיות משודרגות'):
            predictions = build_and_predict(df, selected_day)
            for i, (nums, strong) in enumerate(predictions):
                display_line = " ,".join(map(str, nums[::-1]))
                st.markdown(f'<div class="prediction-card">תוצאה {i+1}: {display_line} | <span style="color:#FFD700;">מספר חזק: {strong}</span></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"שגיאה בטעינת הקובץ: {e}")

st.markdown('<div style="text-align:center; color:gold; font-weight:bold;">נבנה על ידי ליביו הוליביה</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:gold; margin-top:10px;">התחזיות מבוססות על ניתוח סטטיסטי, מספרים חמים, קרים, זוגות עוקבים, מספרים שחוזרים במרווחים קבועים ומספרים יציבים.</div>', unsafe_allow_html=True)
