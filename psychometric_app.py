import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return (
        pd.read_csv("questions_set.csv"),
        pd.read_csv("answers_set.csv"),
        pd.read_csv("stem_set.csv"),
        pd.read_csv("humanities_set.csv"),
        pd.read_csv("arts_set.csv"),
    )
questions_df, answers_df, stem_df, humanities_df, arts_df = load_data()


# Define subject mapping for options
option_subject_map = {
    "Option A": "STEM",
    "Option B": "Arts",
    "Option C": "Humanities",
    "Option D": "Humanities"
}

# Load answer weights dictionary
answer_weights = {}
for _, row in answers_df.iterrows():
    q_no = int(row["Q#"])
    answer_weights[q_no] = {
        "Option A": row["Option A Weights"],
        "Option B": row["Option B Weights"],
        "Option C": row["Option C Weights"],
        "Option D": row["Option D Weights"]
    }

st.title("🎯 Psychometric Career Guidance Test")
st.markdown("Answer the following questions to discover your ideal **career path**, **role type**, and **top subject inclination**.")

responses = {}
with st.form("psychometric_form"):
    for _, row in questions_df.iterrows():
        qno = int(row["Q#"])
        question = row["Question"]
        options = {
            "Option A": row["Option A"],
            "Option B": row["Option B"],
            "Option C": row["Option C"],
            "Option D": row["Option D"]
        }
        answer = st.radio(f"**Q{qno}: {question}**", options.keys(), format_func=lambda x: options[x])
        responses[qno] = answer

    submitted = st.form_submit_button("Submit and Get My Career Report")

if submitted:
    # Initialize scoring
    subject_scores = {"STEM": 0, "Humanities": 0, "Arts": 0}
    role_type_scores = {}
    career_line_scores = {}

    # Calculate scores
    for qno, selected_option in responses.items():
        subject = option_subject_map[selected_option]
        subject_scores[subject] += 1

        weight = answer_weights[qno][selected_option]
        if isinstance(weight, str) and ":" in weight:
            role_type, career_line = weight.split(":")
            role_type_scores[role_type] = role_type_scores.get(role_type, 0) + 1
            career_line_scores[career_line] = career_line_scores.get(career_line, 0) + 1

    # Determine top subject, role type, career line
    top_subject = max(subject_scores, key=subject_scores.get)
    top_role_type = max(role_type_scores, key=role_type_scores.get)
    top_career_line = max(career_line_scores, key=career_line_scores.get)

    st.subheader("🧭 Your Career Alignment Summary")
    st.markdown(f"**Top Subject Inclination:** {top_subject}")
    st.markdown(f"**Best Fit Role Type:** {top_role_type}")
    st.markdown(f"**Ideal Career Line:** {top_career_line}")

    # Pick right dataset
    domain_df = {
        "STEM": stem_df,
        "Humanities": humanities_df,
        "Arts": arts_df
    }[top_subject]

    result_row = domain_df[
        (domain_df["Role Type"].str.lower() == top_role_type.lower()) &
        (domain_df["Career Line"].str.lower() == top_career_line.lower())
    ]

    if not result_row.empty:
        row = result_row.iloc[0]
        st.success("🎉 Based on your inputs, here's your personalized guidance:")
        st.markdown(f"**Example Career Options:** {row['Example Career Options']}")
        st.markdown(f"**Entry-Level Designations:** {row['Entry-Level Designations']}")
        st.markdown(f"**Message:** {row['Message']}")
        st.markdown(f"**Top Universities (India & Abroad):** {row['Top Universities (India & Abroad)']}")
        st.markdown(f"**Potential Companies to Aim For:** {row['Potential Companies to Aim For']}")
    else:
        st.warning("No perfect match found for this combination. Please try again or revise mappings.")
