
from flask import Flask, render_template, request, redirect, url_for
import os
import io
from werkzeug.utils import secure_filename
import re
from datetime import datetime
from typing import Dict, List, Tuple

# Try to import PyPDF2, but make it optional
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

class ResumeEvaluator:
    def __init__(self):
        self.career_tracks = [
            "Healthcare",
            "Technology", 
            "Education",
            "Entrepreneurship",
            "Creative Arts",
            "Skilled Trades",
            "Public Service / Nonprofit",
            "I'm Still Figuring It Out"
        ]

        self.life_stages = [
            "High School Student",
            "College Student", 
            "Recent Graduate",
            "Career Starter",
            "Career Changer"
        ]

        # Keywords for different career tracks
        self.career_keywords = {
            "Healthcare": ["medical", "patient", "clinical", "health", "nursing", "therapy", "hospital", "care", "treatment"],
            "Technology": ["software", "programming", "coding", "development", "tech", "data", "computer", "digital", "IT"],
            "Education": ["teaching", "education", "student", "curriculum", "classroom", "learning", "academic", "school"],
            "Entrepreneurship": ["business", "startup", "entrepreneur", "leadership", "management", "strategy", "innovation"],
            "Creative Arts": ["design", "creative", "art", "visual", "media", "content", "marketing", "brand", "photography"],
            "Skilled Trades": ["construction", "electrical", "plumbing", "mechanical", "technical", "repair", "maintenance"],
            "Public Service / Nonprofit": ["community", "service", "volunteer", "nonprofit", "government", "public", "social"]
        }

    def analyze_resume_text(self, resume_text: str) -> Dict:
        """Analyze resume text for various metrics"""

        # Basic text analysis
        word_count = len(resume_text.split())
        has_contact_info = any(indicator in resume_text.lower() for indicator in ['email', '@', 'phone', 'linkedin'])
        has_experience_section = any(section in resume_text.lower() for section in ['experience', 'work', 'employment'])
        has_education_section = any(section in resume_text.lower() for section in ['education', 'degree', 'university', 'college'])
        has_skills_section = any(section in resume_text.lower() for section in ['skills', 'technical', 'proficient'])

        # Action verbs check
        action_verbs = ['led', 'managed', 'developed', 'created', 'implemented', 'achieved', 'improved', 'increased', 'decreased', 'organized', 'coordinated', 'designed', 'built', 'established']
        action_verb_count = sum(1 for verb in action_verbs if verb in resume_text.lower())

        # Quantifiable achievements (numbers/percentages)
        numbers_pattern = r'\b\d+(?:\.\d+)?%?\b'
        quantifiable_achievements = len(re.findall(numbers_pattern, resume_text))

        return {
            'word_count': word_count,
            'has_contact_info': has_contact_info,
            'has_experience_section': has_experience_section,
            'has_education_section': has_education_section,
            'has_skills_section': has_skills_section,
            'action_verb_count': action_verb_count,
            'quantifiable_achievements': quantifiable_achievements
        }

    def calculate_relevance_score(self, resume_text: str, career_track: str, dream_job: str) -> int:
        """Calculate relevance score (0-20)"""
        score = 0
        resume_lower = resume_text.lower()
        dream_job_lower = dream_job.lower()

        # Check for career track keywords
        if career_track in self.career_keywords:
            keywords = self.career_keywords[career_track]
            keyword_matches = sum(1 for keyword in keywords if keyword in resume_lower)
            score += min(10, keyword_matches * 2)

        # Check for dream job keywords in resume
        dream_job_words = dream_job_lower.split()
        dream_matches = sum(1 for word in dream_job_words if len(word) > 3 and word in resume_lower)
        score += min(10, dream_matches * 2)

        return min(20, score)

    def calculate_clarity_score(self, resume_text: str, analysis: Dict) -> int:
        """Calculate clarity score (0-20)"""
        score = 0

        # Word count check (not too short, not too long)
        if 200 <= analysis['word_count'] <= 800:
            score += 8
        elif analysis['word_count'] < 200:
            score += 3
        else:
            score += 5

        # Section organization
        if analysis['has_contact_info']:
            score += 3
        if analysis['has_experience_section']:
            score += 3
        if analysis['has_education_section']:
            score += 3
        if analysis['has_skills_section']:
            score += 3

        return min(20, score)

    def calculate_impact_score(self, analysis: Dict) -> int:
        """Calculate impact score (0-20)"""
        score = 0

        # Action verbs
        score += min(10, analysis['action_verb_count'] * 2)

        # Quantifiable achievements
        score += min(10, analysis['quantifiable_achievements'] * 3)

        return min(20, score)

    def calculate_completeness_score(self, analysis: Dict) -> int:
        """Calculate completeness score (0-20)"""
        score = 0

        sections = [
            analysis['has_contact_info'],
            analysis['has_experience_section'], 
            analysis['has_education_section'],
            analysis['has_skills_section']
        ]

        score = sum(sections) * 5
        return min(20, score)

    def calculate_differentiation_score(self, resume_text: str, dream_job: str) -> int:
        """Calculate differentiation score (0-20)"""
        score = 10  # Base score

        # Check for unique elements
        unique_indicators = ['portfolio', 'project', 'certification', 'award', 'volunteer', 'leadership']
        unique_count = sum(1 for indicator in unique_indicators if indicator in resume_text.lower())

        score += min(10, unique_count * 2)

        return min(20, score)

    def generate_strengths(self, analysis: Dict, scores: Dict, career_track: str) -> List[str]:
        """Generate strengths based on analysis"""
        strengths = []

        if scores['clarity'] >= 15:
            strengths.append("Clear, well-organized resume structure that's easy to scan")

        if analysis['action_verb_count'] >= 3:
            strengths.append("Strong use of action-oriented language that demonstrates initiative")

        if analysis['quantifiable_achievements'] >= 2:
            strengths.append("Good inclusion of measurable results and achievements")

        if scores['relevance'] >= 12:
            strengths.append(f"Resume content aligns well with {career_track} career path")

        if len(strengths) == 0:
            strengths.append("Shows commitment to professional development by seeking feedback")

        return strengths[:4]  # Max 4 strengths

    def generate_improvements(self, analysis: Dict, scores: Dict, career_track: str, life_stage: str) -> List[str]:
        """Generate improvement suggestions"""
        improvements = []

        if scores['relevance'] < 12:
            improvements.append(f"Add more {career_track.lower()}-specific keywords and experiences to better align with your target field")

        if analysis['action_verb_count'] < 3:
            improvements.append("Use more powerful action verbs (led, developed, achieved, implemented) to start your bullet points")

        if analysis['quantifiable_achievements'] < 2:
            improvements.append("Include specific numbers, percentages, or measurable outcomes to demonstrate your impact")

        if not analysis['has_skills_section']:
            improvements.append("Add a dedicated skills section highlighting both technical and soft skills relevant to your field")

        if scores['clarity'] < 15:
            improvements.append("Improve formatting and organization - ensure clear section headers and consistent styling")

        # Life stage specific advice
        if life_stage in ["High School Student", "College Student"]:
            improvements.append("Consider adding relevant coursework, projects, or extracurricular activities that demonstrate your interests")

        return improvements[:5]  # Max 5 improvements

    def generate_career_alignment(self, career_track: str, dream_job: str, life_stage: str, scores: Dict) -> str:
        """Generate career alignment feedback"""

        alignment_feedback = f"Based on your goal of '{dream_job}' in {career_track}, "

        if scores['relevance'] >= 15:
            alignment_feedback += "your resume shows strong alignment with your target career path. "
        elif scores['relevance'] >= 10:
            alignment_feedback += "your resume shows moderate alignment with your target career path. "
        else:
            alignment_feedback += "there's room to better align your resume with your target career path. "

        # Next steps based on life stage
        next_steps = {
            "High School Student": "Focus on building relevant experience through internships, volunteer work, or personal projects that showcase your interest in this field.",
            "College Student": "Seek internships, join relevant student organizations, and consider coursework that directly supports your career goals.",
            "Recent Graduate": "Look for entry-level positions, consider informational interviews with professionals in your field, and build a portfolio of relevant work.",
            "Career Starter": "Focus on gaining specialized skills through online courses or certifications, and seek mentorship from experienced professionals.",
            "Career Changer": "Highlight transferable skills from your previous experience and consider additional training or certifications to bridge any knowledge gaps."
        }

        alignment_feedback += next_steps.get(life_stage, "Continue building relevant experience and skills in your chosen field.")

        return alignment_feedback

    def generate_resources(self, career_track: str, life_stage: str) -> List[str]:
        """Generate tailored resource recommendations"""

        resources = []

        # Career track specific resources
        track_resources = {
            "Healthcare": [
                "Khan Academy Medical School Prep courses",
                "Healthcare Financial Management Association (HFMA) resources",
                "American Medical Association career guidance"
            ],
            "Technology": [
                "FreeCodeCamp for programming fundamentals", 
                "Google Career Certificates (Data Analytics, UX Design, IT Support)",
                "GitHub for building a coding portfolio"
            ],
            "Education": [
                "Teach for America application resources",
                "National Education Association career center",
                "Coursera Teaching courses"
            ],
            "Creative Arts": [
                "Behance for portfolio creation",
                "Adobe Creative Suite tutorials",
                "Creative Live online courses"
            ],
            "Entrepreneurship": [
                "SCORE mentorship program",
                "Small Business Administration (SBA) resources",
                "Coursera Entrepreneurship specializations"
            ]
        }

        if career_track in track_resources:
            resources.extend(track_resources[career_track][:2])

        # Universal resources
        resources.append("LinkedIn Learning for professional skill development")

        return resources[:3]

    def evaluate_resume(self, resume_text: str, career_track: str, dream_job: str, life_stage: str) -> Dict:
        """Main evaluation function"""

        # Analyze resume
        analysis = self.analyze_resume_text(resume_text)

        # Calculate scores
        relevance_score = self.calculate_relevance_score(resume_text, career_track, dream_job)
        clarity_score = self.calculate_clarity_score(resume_text, analysis)
        impact_score = self.calculate_impact_score(analysis)
        completeness_score = self.calculate_completeness_score(analysis)
        differentiation_score = self.calculate_differentiation_score(resume_text, dream_job)

        scores = {
            'relevance': relevance_score,
            'clarity': clarity_score,
            'impact': impact_score,
            'completeness': completeness_score,
            'differentiation': differentiation_score
        }

        total_score = sum(scores.values())

        # Generate feedback sections
        strengths = self.generate_strengths(analysis, scores, career_track)
        improvements = self.generate_improvements(analysis, scores, career_track, life_stage)
        career_alignment = self.generate_career_alignment(career_track, dream_job, life_stage, scores)
        resources = self.generate_resources(career_track, life_stage)

        return {
            'scores': scores,
            'total_score': total_score,
            'strengths': strengths,
            'improvements': improvements,
            'career_alignment': career_alignment,
            'resources': resources
        }

    def format_evaluation_report(self, evaluation: Dict, career_track: str, dream_job: str, life_stage: str) -> str:
        """Format the evaluation into the specified output format"""

        report = f"""🎯 Resume Evaluation Report

Career Track: {career_track}
Dream Job: {dream_job}
Life Stage: {life_stage}
Evaluation Date: {datetime.now().strftime('%B %d, %Y')}

═══════════════════════════════════════════════════════════════

📝 1. Resume Scorecard ({evaluation['total_score']}/100)

• Relevance ({evaluation['scores']['relevance']}/20): How aligned the resume is with the selected career track and dream job description
• Clarity ({evaluation['scores']['clarity']}/20): Formatting, grammar, readability, and ease of scanning  
• Impact ({evaluation['scores']['impact']}/20): Demonstration of results, quantifiable achievements, and action-oriented language
• Completeness ({evaluation['scores']['completeness']}/20): Key sections included (contact info, summary/objective, experience, education, skills, certifications)
• Differentiation ({evaluation['scores']['differentiation']}/20): Uniqueness, personal brand, or value proposition clarity

→ Total Resume Score: {evaluation['total_score']}/100

═══════════════════════════════════════════════════════════════

📊 2. Strengths Summary

"""

        for strength in evaluation['strengths']:
            report += f"• {strength}\n"

        report += f"""
═══════════════════════════════════════════════════════════════

🔧 3. Areas to Strengthen

"""

        for improvement in evaluation['improvements']:
            report += f"• {improvement}\n"

        report += f"""
═══════════════════════════════════════════════════════════════

🧭 4. Career Alignment Feedback

{evaluation['career_alignment']}

═══════════════════════════════════════════════════════════════

📚 5. Resource Recommendations

"""

        for resource in evaluation['resources']:
            report += f"• {resource}\n"

        report += """
═══════════════════════════════════════════════════════════════

This evaluation was generated by the Resume Evaluator App. 
Keep building, keep growing! 🚀
"""

        return report

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize evaluator
evaluator = ResumeEvaluator()

def extract_text_from_pdf(file_stream):
    """Extract text from PDF file"""
    if not PDF_SUPPORT:
        return "PDF support not available. Please install PyPDF2: pip install PyPDF2"

    try:
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route for the application"""
    if request.method == 'POST':
        try:
            # Get form data
            career_track = request.form.get('career_track')
            life_stage = request.form.get('life_stage')
            dream_job = request.form.get('dream_job', '').strip()
            resume_text = request.form.get('resume_text', '').strip()

            # Validate required fields
            if not career_track or not life_stage or not dream_job:
                return render_template('index.html', 
                                     career_tracks=evaluator.career_tracks,
                                     life_stages=evaluator.life_stages,
                                     error="Please fill in all required fields.")

            # Handle file upload
            file = request.files.get('resume_file')
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_ext = os.path.splitext(filename)[1].lower()

                if file_ext == '.pdf':
                    resume_text = extract_text_from_pdf(file.stream)
                elif file_ext in ['.txt', '.text']:
                    resume_text = file.read().decode('utf-8', errors='ignore')
                else:
                    return render_template('index.html', 
                                         career_tracks=evaluator.career_tracks,
                                         life_stages=evaluator.life_stages,
                                         error="Please upload a PDF or TXT file.")

            # Check if we have resume text
            if not resume_text:
                return render_template('index.html', 
                                     career_tracks=evaluator.career_tracks,
                                     life_stages=evaluator.life_stages,
                                     error="Please provide resume text either by uploading a file or pasting text.")

            # Evaluate resume
            evaluation = evaluator.evaluate_resume(resume_text, career_track, dream_job, life_stage)
            report = evaluator.format_evaluation_report(evaluation, career_track, dream_job, life_stage)

            return render_template('result.html', 
                                 report=report,
                                 evaluation=evaluation,
                                 career_track=career_track,
                                 dream_job=dream_job,
                                 life_stage=life_stage)

        except Exception as e:
            return render_template('index.html', 
                                 career_tracks=evaluator.career_tracks,
                                 life_stages=evaluator.life_stages,
                                 error=f"An error occurred: {str(e)}")

    # GET request - show the form
    return render_template('index.html', 
                         career_tracks=evaluator.career_tracks,
                         life_stages=evaluator.life_stages)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
