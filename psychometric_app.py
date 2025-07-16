import pandas as pd
import streamlit as st

# Load files
questions_df = pd.read_excel("questions_set.xlsx")
scoring_df = pd.read_excel("scoring_set.xlsx")
stem_df = pd.read_excel("stem_set.xlsx")
arts_df = pd.read_excel("arts_set.xlsx")
humanities_df = pd.read_excel("humanities_set.xlsx")

st.set_page_config(page_title="Career Guidance Tool", layout="centered")

st.title("🎓 Career & Role Type Guidance")
st.subheader("Step 1: Answer these questions to understand your preferences")

# Store answers
responses = {}

# Render questions
for idx, row in questions_df.iterrows():
    question = row["Question"]
    options = [row[f"Option {opt}"] for opt in ["A", "B", "C", "D"] if f"Option {opt}" in row]
    selected = st.radio(question, options, key=idx)
    responses[question] = selected

st.subheader("Step 2: Tell us your best 6 subjects & marks")

subject_marks = []
for i in range(6):
    col1, col2 = st.columns([2, 1])
    with col1:
        subject = st.text_input(f"Subject {i+1}", key=f"subject_{i}")
    with col2:
        marks = st.number_input(f"Marks", min_value=0, max_value=100, key=f"marks_{i}")
    if subject:
        subject_marks.append((subject.lower(), marks))

def get_inclination(subject_marks):
    stem_subjects = {"math", "physics", "chemistry", "biology", "cs", "computer science"}
    arts_subjects = {"music", "painting", "fine arts", "drama", "dance"}
    humanities_subjects = {"history", "geography", "political science", "sociology", "psychology", "economics", "english"}

    scores = {"STEM": 0, "ARTS": 0, "HUMANITIES": 0}

    for subj, marks in subject_marks:
        if subj in stem_subjects:
            scores["STEM"] += marks
        elif subj in arts_subjects:
            scores["ARTS"] += marks
        elif subj in humanities_subjects:
            scores["HUMANITIES"] += marks

    return max(scores, key=scores.get)

# Score Calculation
def calculate_scores(responses):
    category_scores = {}
    for question, answer in responses.items():
        row = scoring_df[scoring_df["Question"] == question]
        if not row.empty:
            category = row.iloc[0]["Category"]
            score = row.iloc[0][f"Weight {answer[-1]}"]  # Assuming Option A = last char A
            category_scores[category] = category_scores.get(category, 0) + score
    return category_scores

if st.button("🔍 Generate Report"):
    if len(subject_marks) < 6 or len(responses) < len(questions_df):
        st.error("Please answer all questions and enter 6 subjects with marks.")
    else:
        inclination = get_inclination(subject_marks)
        st.success(f"Your academic inclination: **{inclination}**")

        scores = calculate_scores(responses)
        st.subheader("🔢 Your Category Scores")
        st.write(scores)

        # Choose dataset
        if inclination == "STEM":
            report_df = stem_df
        elif inclination == "ARTS":
            report_df = arts_df
        else:
            report_df = humanities_df

        # Match top categories
        top_categories = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]
        top_roles = report_df[report_df["Category"].isin([c[0] for c in top_categories])]

        st.subheader("🎯 Suggested Careers & Role Types")
        st.dataframe(top_roles.reset_index(drop=True))

