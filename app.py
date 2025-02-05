from flask import Flask, render_template, request, jsonify
from modules.parse_resume import parse_resume
from modules.job_analysis import parse_job_description
from modules.ats_scoring import calculate_score
from modules.suggestions import generate_suggestions

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """
    Render the main page with the upload form.
    """
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """
    Handle file uploads and analyze the resume content against the job description.
    """
    try:
        # Retrieve the uploaded resume and job description
        resume_file = request.files.get('resume')
        job_desc = request.form.get('job_description')

        # Validate inputs
        if not resume_file or not job_desc:
            return jsonify({"error": "Both resume and job description are required!"}), 400

        # Log the file name and job description for debugging
        print(f"Uploaded file name: {resume_file.filename}")
        print(f"Job Description: {job_desc[:100]}...")  # Log first 100 characters

        # Parse the resume content
        resume_text = parse_resume(resume_file)
        if "Error reading file" in resume_text:
            return jsonify({"error": resume_text}), 400
        print(f"Parsed Resume Text: {resume_text[:100]}...")  # Log first 100 characters of resume

        # Parse the job description
        job_keywords = parse_job_description(job_desc)
        print(f"Parsed Job Keywords: {job_keywords}")  # Log parsed keywords

        # Calculate ATS score
        score, matched_keywords, missing_keywords = calculate_score(resume_text, job_keywords)
        print(f"ATS Score: {score}")
        print(f"Matched Keywords: {matched_keywords}")
        print(f"Missing Keywords: {missing_keywords}")

        # Generate suggestions
        suggestions = generate_suggestions(matched_keywords, missing_keywords, resume_text, job_keywords)
        print(f"Suggestions: {suggestions}")  # Log suggestions

        # Return the results
        # Ensure matched_keywords and missing_keywords are lists
        return jsonify({
            "score": score,
            "matched_keywords": list(matched_keywords),  # Ensure it's a list
            "missing_keywords": list(missing_keywords),  # Ensure it's a list
            "suggestions": suggestions
        })


    except Exception as e:
        # Log the error for debugging
        print(f"Internal Server Error: {e}")
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500


if __name__ == '__main__':
    app.run(debug=True)
