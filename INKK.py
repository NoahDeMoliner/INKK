import streamlit as st
from collections import defaultdict
import pandas as pd
H1, H2 = st.columns([1,4])
with H1:
    st.title("INKK")
with H2:
    st.subheader('Evaluation System')


st.divider()

def parse_line(line: str):
    parts = line.strip().split()
    if len(parts) != 3: raise ValueError()
    s1, score_raw, s2 = parts
    if s1.isdigit() or s2.isdigit(): raise ValueError()
    if "-" not in score_raw: raise ValueError()
    raw1, raw2 = score_raw.split("-", 1)
    return [s1, int(raw1), int(raw2), s2]

def evaluate(matches, factor, start_pot):
    ratings = defaultdict(lambda: [0.0, float(start_pot)])
    for p1, s1, s2, p2 in matches:
        r1, pot1 = ratings[p1]
        r2, pot2 = ratings[p2]
        st_s1, st_p1 = factor*r1, factor*pot1
        st_s2, st_p2 = factor*r2, factor*pot2
        pool = st_s1 + st_s2 + st_p1 + st_p2
        total = s1 + s2
        share1, share2 = s1/total, s2/total
        ratings[p1] = [r1 - st_s1 + pool*share1, pot1 - st_p1]
        ratings[p2] = [r2 - st_s2 + pool*share2, pot2 - st_p2]
    return dict(ratings)

# ─── Layout ───
col_left, col_right = st.columns([1, 1])  # Two equal columns

with col_left:
    # Narrower input text area (about half width)
    input_text = st.text_area(
        "Enter Set [Str Int-Int Str]", height=150, max_chars=420
    )

    # Layout for button, slider, scale input with adjusted widths
    c1, c2, c3 = st.columns([2, 2, 1])  # Button and Scale input wider, slider less wide

    with c1:
        btn = st.button("EVALUATE", use_container_width=True)
    with c2:
        factor = st.slider("", 0.0, 1.0, 0.2, step=0.1, label_visibility="collapsed")
    with c3:
        scale_input = st.text_input("Scale", "42", max_chars=3)

with col_right:
    # Placeholder for ranking table, narrower width by using container width inside smaller column
    ranking_placeholder = st.empty()

if btn:
    try:
        start_pot = int(scale_input)
    except ValueError:
        st.error("Invalid Scale Value")
        st.stop()

    lines = [ln for ln in input_text.splitlines() if ln.strip()]
    matches, errors = [], []
    for line in lines:
        try:
            matches.append(parse_line(line))
        except ValueError:
            errors.append(f"Invalid input: {line}")
    if errors:
        for e in errors:
            st.error(e)
    else:
        results = evaluate(matches, factor, start_pot)
        ranked = sorted(results.items(), key=lambda x: x[1][0], reverse=True)

        # ranking table with no index column, half width (limited by right column)
        df_rank = pd.DataFrame({
            "Rank":   list(range(1, len(ranked)+1)),
            "Player": [p for p, _ in ranked],
            "Score":  [int(r[0]) for _, r in ranked]
        }).set_index("Rank")

        ranking_placeholder.dataframe(df_rank, use_container_width=True)
