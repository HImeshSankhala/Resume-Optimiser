import re
import spacy

# Load spaCy NLP model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    raise RuntimeError("SpaCy model 'en_core_web_sm' not found. Run 'python -m spacy download en_core_web_sm'.") from e

def extract_skills_dynamic(job_description):
    """
    Extract potential skills dynamically from a job description.
    Args:
        job_description (str): The text of the job description.
    Returns:
        dict: Categorized keywords (skills, responsibilities, etc.).
    """
    doc = nlp(job_description.lower())
    keywords = {
        "skills": [],
        "responsibilities": [],
    }

    # Dependency Parsing for Skills
    for token in doc:
        # Find proper nouns (NNP), nouns (NOUN), or known entities (ORG, PRODUCT)
        if token.pos_ in {"NOUN", "PROPN"} and token.dep_ in {"dobj", "pobj", "attr"}:
            keywords["skills"].append(token.text)

        # Find verbs for responsibilities
        if token.pos_ == "VERB":
            keywords["responsibilities"].append(token.text)

    # Remove duplicates and sort
    keywords["skills"] = sorted(set(keywords["skills"]))
    keywords["responsibilities"] = sorted(set(keywords["responsibilities"]))

    return keywords

def extract_responsibilities_dynamic(job_description):
    """
    Dynamically extract responsibilities from the job description based on context.
    Args:
        job_description (str): The text of the job description.
    Returns:
        list: List of context-aware, job-relevant responsibilities.
    """
    doc = nlp(job_description.lower())
    responsibilities = []

    for token in doc:
        # Check if the token is a verb
        if token.pos_ == "VERB":
            # Find related objects and modifiers
            obj = [child.text for child in token.children if child.dep_ in {"dobj", "pobj", "attr", "prep"}]
            adv_mod = [child.text for child in token.children if child.dep_ == "advmod"]
            noun_mod = [child.text for child in token.children if child.dep_ == "nmod"]

            # Combine verb with its context (objects and modifiers)
            context = " ".join(obj + adv_mod + noun_mod).strip()
            if context:
                responsibilities.append(f"{token.text} {context}")
            else:
                responsibilities.append(token.text)

    # Remove duplicates and sort
    return sorted(set(responsibilities))

def parse_job_description(job_description):
    """
    Parse the job description text and extract useful information.
    Args:
        job_description (str): The text of the job description.
    Returns:
        dict: Extracted keywords categorized by skills and responsibilities.
    """
    keywords = extract_skills_dynamic(job_description)
    responsibilities = extract_responsibilities_dynamic(job_description)
    
    return {
        "skills": keywords["skills"],
        "responsibilities": responsibilities
    }

def generate_suggestions(matched_keywords, missing_keywords, resume_text, job_keywords):
    """
    Generate actionable suggestions based on missing keywords and areas for improvement.

    Args:
        matched_keywords (dict): Matched skills and responsibilities.
        missing_keywords (dict): Missing skills and responsibilities.
        resume_text (str): The full text of the resume.
        job_keywords (dict): Parsed job description keywords (skills, responsibilities).

    Returns:
        list: Suggestions for improving the resume.
    """
    suggestions = []

    # Suggest adding missing skills
    for skill in missing_keywords.get("skills", []):
        suggestions.append(f"You can add '{skill}' to your Skills section.")

    # Suggest adding missing responsibilities
    for responsibility in missing_keywords.get("responsibilities", []):
        suggestions.append(f"Highlight your experience with '{responsibility}' in your Work Experience section.")

    # Check for opportunities to rewrite lines in the resume
    resume_lines = resume_text.split("\n")
    for line in resume_lines:
        # Match lines that are vague or could use improvement
        if re.search(r"\b(develop|manage|improve)\b", line, re.IGNORECASE):
            suggestions.append(f"Line from resume: '{line.strip()}'. Suggestion: 'Expand it to include: {', '.join(missing_keywords.get('responsibilities', []))}'.")

    # Additional context-aware suggestions
    if "data" in job_keywords.get("skills", []):
        suggestions.append("Consider emphasizing your data analysis or data engineering achievements in your Work Experience section.")

    if "collaborate" in job_keywords.get("responsibilities", []):
        suggestions.append("Highlight examples where you collaborated with team members or stakeholders in your Work Experience section.")

    if "reports" in job_keywords.get("responsibilities", []):
        suggestions.append("Include any experience creating reports or dashboards in your Work Experience or Skills section.")

    return suggestions

