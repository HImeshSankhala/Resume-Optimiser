import re

def calculate_score(resume_text, job_keywords):
    """
    Calculate the ATS score by comparing keywords from the job description and resume.
    Args:
        resume_text (str): Parsed text from the resume.
        job_keywords (dict): Extracted keywords from the job description (skills, responsibilities).
    Returns:
        tuple: ATS score, matched keywords, missing keywords.
    """
    # Convert resume text to lowercase and tokenize it
    resume_tokens = set(re.findall(r'\b\w+\b', resume_text.lower()))

    # Initialize matched and missing keywords
    matched_keywords = {
        "skills": [],
        "responsibilities": []
    }
    missing_keywords = {
        "skills": [],
        "responsibilities": []
    }

    # Match keywords for each category
    for category in job_keywords.keys():
        job_tokens = set(job_keywords[category])
        matched_keywords[category] = list(job_tokens.intersection(resume_tokens))
        missing_keywords[category] = list(job_tokens.difference(resume_tokens))

    # Calculate the ATS score
    total_keywords = sum(len(job_keywords[cat]) for cat in job_keywords)
    matched_count = sum(len(matched_keywords[cat]) for cat in matched_keywords)
    score = (matched_count / total_keywords) * 100 if total_keywords > 0 else 0

    return round(score, 2), matched_keywords, missing_keywords
