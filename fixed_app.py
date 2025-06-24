from flask import Flask, render_template, request
import os
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

class ResumeEvaluator:
    def __init__(self):
        self.career_tracks = [
            "Technology & Software",
            "Healthcare & Medicine",
            "Finance & Banking",
            "Marketing & Communications",
            "Education & Training",
            "Public Service & Nonprofit",
            "Engineering & Manufacturing",
            "Creative & Design",
            "Sales & Business Development",
            "Consulting & Strategy",
            "Legal & Compliance",
            "Operations & Supply Chain"
        ]

        self.life_stages = [
            "High School Student (16-18)",
            "College Student (18-22)",
            "Recent Graduate (22-25)",
            "Early Career (25-30)",
            "Career Transition",
            "Returning to Workforce"
        ]

        self.rubric_descriptions = {
            "relevance": "How well your resume matches your target job or field - includes relevant keywords, experience, and skills.",
            "clarity": "How clear, organized, and easy to read your resume is - formatting, structure, and readability.",
            "impact": "How strongly your achievements and results are communicated - quantified accomplishments and action verbs.",
            "completeness": "Whether all key sections and details are present - contact info, experience, education, skills.",
            "differentiation": "How well you stand out from other candidates - unique value proposition and memorable elements."
        }

    def extract_good_phrases(self, resume_text):
        """Extract strong phrases and accomplishments from resume"""
        good_phrases = []

        # Look for quantified achievements
        quantified_patterns = [
            r'[Ii]ncreased.*?(\d+%|\d+\s*percent)',
            r'[Rr]educed.*?(\d+%|\d+\s*percent)',
            r'[Mm]anaged.*?\$[\d,]+',
            r'[Ll]ed.*?(\d+)\s*(people|team|members)',
            r'[Aa]chieved.*?(\d+%|\d+\s*percent)',
            r'[Gg]enerated.*?\$[\d,]+',
            r'[Ss]aved.*?\$[\d,]+',
            r'[Ii]mproved.*?(\d+%|\d+\s*percent)'
        ]

        for pattern in quantified_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                # Get the full sentence containing the match
                sentences = re.split(r'[.!?]', resume_text)
                for sentence in sentences:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        good_phrases.append(sentence.strip())
                        break

        # Look for strong action verbs at start of bullet points
        action_patterns = [
            r'[•\-\*]\s*(Developed|Created|Implemented|Led|Managed|Designed|Built|Launched|Optimized|Streamlined).*',
            r'^\s*(Developed|Created|Implemented|Led|Managed|Designed|Built|Launched|Optimized|Streamlined).*'
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, resume_text, re.MULTILINE | re.IGNORECASE)
            good_phrases.extend(matches[:3])  # Limit to 3 examples

        return list(set(good_phrases))[:5]  # Return top 5 unique phrases

    def extract_growth_phrases(self, resume_text):
        """Extract phrases that indicate areas for improvement"""
        growth_phrases = []

        # Look for weak language patterns
        weak_patterns = [
            r'[Rr]esponsible for.*',
            r'[Hh]elped with.*',
            r'[Aa]ssisted in.*',
            r'[Ww]orked on.*',
            r'[Ii]nvolved in.*'
        ]

        for pattern in weak_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                sentences = re.split(r'[.!?]', resume_text)
                for sentence in sentences:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        growth_phrases.append(sentence.strip())
                        break

        return list(set(growth_phrases))[:3]  # Return top 3 unique phrases

    def generate_personal_feedback(self, user_inputs, evaluation, resume_text):
        """Generate personalized feedback based on user inputs and resume"""
        feedback = []

        career_track = user_inputs.get('career_track', '')
        dream_job = user_inputs.get('dream_job', '')
        life_stage = user_inputs.get('life_stage', '')

        # Career alignment feedback
        if dream_job:
            if evaluation['total_score'] >= 70:
                feedback.append(f"Your resume shows strong alignment with your goal of '{dream_job}'. The experience and skills you've highlighted demonstrate clear progression toward this role.")
            else:
                feedback.append(f"To better align with your goal of '{dream_job}', consider emphasizing more relevant experience and incorporating industry-specific keywords.")

        # Life stage specific feedback
        if "Student" in life_stage or "Graduate" in life_stage:
            feedback.append("As someone early in your career, focus on highlighting academic projects, internships, and transferable skills. Consider adding relevant coursework and certifications.")
        elif "Career Transition" in life_stage:
            feedback.append("For a career transition, emphasize transferable skills and any relevant experience or training in your target field. Consider adding a professional summary that bridges your past and future.")

        # Score-based feedback
        if evaluation['scores']['impact'] < 15:
            feedback.append("Your resume would benefit from more quantified achievements. Try to add specific numbers, percentages, or dollar amounts to demonstrate your impact.")

        if evaluation['scores']['relevance'] < 15:
            feedback.append(f"Consider incorporating more keywords and terminology specific to {career_track} to improve relevance for your target roles.")

        return feedback

    def suggest_career_paths(self, user_inputs, resume_text):
        """Suggest career paths based on resume content and user inputs"""
        insights = []

        career_track = user_inputs.get('career_track', '')
        dream_job = user_inputs.get('dream_job', '')

        # Analyze resume for skills and experience
        tech_keywords = ['python', 'javascript', 'sql', 'data', 'software', 'programming', 'development']
        business_keywords = ['management', 'strategy', 'analysis', 'project', 'leadership', 'operations']
        creative_keywords = ['design', 'creative', 'marketing', 'content', 'brand', 'visual']

        resume_lower = resume_text.lower()

        # Suggest paths based on detected skills
        if any(keyword in resume_lower for keyword in tech_keywords):
            insights.append("Your technical background positions you well for roles in software development, data analysis, or product management.")

        if any(keyword in resume_lower for keyword in business_keywords):
            insights.append("Your business and leadership experience could lead to opportunities in consulting, operations management, or business development.")

        if any(keyword in resume_lower for keyword in creative_keywords):
            insights.append("Your creative skills suggest potential paths in digital marketing, UX/UI design, or brand management.")

        # Career track specific suggestions
        if career_track == "Technology & Software":
            insights.append("Consider specializing in emerging areas like AI/ML, cybersecurity, or cloud computing to stay competitive in tech.")
        elif career_track == "Healthcare & Medicine":
            insights.append("Healthcare technology and telemedicine are growing fields that combine healthcare with digital innovation.")
        elif career_track == "Finance & Banking":
            insights.append("FinTech and sustainable finance are rapidly expanding areas within the financial sector.")

        # Add general career development insight
        insights.append("Consider building a portfolio of projects or case studies that demonstrate your skills in action, especially for your target role.")

        return insights[:4]  # Return top 4 insights

    def evaluate_resume(self, resume_text, career_track, life_stage, dream_job):
        """Enhanced evaluation with more detailed analysis"""
        scores = {}

        # Relevance scoring (enhanced)
        relevance_score = self._score_relevance(resume_text, career_track, dream_job)
        scores['relevance'] = relevance_score

        # Clarity scoring
        clarity_score = self._score_clarity(resume_text)
        scores['clarity'] = clarity_score

        # Impact scoring (enhanced)
        impact_score = self._score_impact(resume_text)
        scores['impact'] = impact_score

        # Completeness scoring
        completeness_score = self._score_completeness(resume_text)
        scores['completeness'] = completeness_score

        # Differentiation scoring
        differentiation_score = self._score_differentiation(resume_text)
        scores['differentiation'] = differentiation_score

        total_score = sum(scores.values())

        # Generate enhanced feedback
        strengths = self._generate_strengths(scores, resume_text)
        improvements = self._generate_improvements(scores, resume_text, career_track)
        career_alignment = self._generate_career_alignment(total_score, career_track, dream_job, life_stage)
        resources = self._generate_resources(scores, career_track, life_stage)

        return {
            'scores': scores,
            'total_score': total_score,
            'strengths': strengths,
            'improvements': improvements,
            'career_alignment': career_alignment,
            'resources': resources
        }

    def _score_relevance(self, resume_text, career_track, dream_job):
        """Enhanced relevance scoring"""
        score = 10  # Base score

        # Career track keywords
        track_keywords = {
            "Technology & Software": ['python', 'javascript', 'software', 'development', 'programming', 'coding', 'technical', 'system', 'database', 'api'],
            "Healthcare & Medicine": ['patient', 'clinical', 'medical', 'healthcare', 'treatment', 'diagnosis', 'care', 'health', 'medicine', 'hospital'],
            "Finance & Banking": ['financial', 'investment', 'banking', 'accounting', 'budget', 'analysis', 'risk', 'portfolio', 'audit', 'compliance'],
            "Marketing & Communications": ['marketing', 'brand', 'campaign', 'social media', 'content', 'advertising', 'promotion', 'communications', 'digital', 'seo'],
            "Education & Training": ['teaching', 'education', 'curriculum', 'student', 'learning', 'training', 'instruction', 'academic', 'classroom', 'pedagogy'],
            "Public Service & Nonprofit": ['community', 'public', 'nonprofit', 'volunteer', 'service', 'social', 'advocacy', 'outreach', 'civic', 'government']
        }

        if career_track in track_keywords:
            keywords = track_keywords[career_track]
            keyword_count = sum(1 for keyword in keywords if keyword.lower() in resume_text.lower())
            score += min(keyword_count * 2, 8)  # Up to 8 bonus points

        # Dream job relevance
        if dream_job:
            dream_words = dream_job.lower().split()
            dream_relevance = sum(1 for word in dream_words if word in resume_text.lower())
            score += min(dream_relevance, 2)  # Up to 2 bonus points

        return min(score, 20)

    def _score_clarity(self, resume_text):
        """Score resume clarity and organization"""
        score = 15  # Base score for having text

        # Check for common sections
        sections = ['experience', 'education', 'skills', 'summary', 'objective']
        section_count = sum(1 for section in sections if section.lower() in resume_text.lower())
        score += min(section_count, 3)  # Up to 3 points for sections

        # Check for bullet points (good formatting)
        if '•' in resume_text or '-' in resume_text or '*' in resume_text:
            score += 2

        return min(score, 20)

    def _score_impact(self, resume_text):
        """Enhanced impact scoring"""
        score = 8  # Base score

        # Look for quantified achievements
        numbers = re.findall(r'\d+%|\d+\s*percent|\$[\d,]+|\d+\s*(people|team|members|clients|customers)', resume_text, re.IGNORECASE)
        score += min(len(numbers) * 2, 8)  # Up to 8 points for quantified results

        # Strong action verbs
        strong_verbs = ['achieved', 'improved', 'increased', 'reduced', 'led', 'managed', 'developed', 'created', 'implemented', 'optimized']
        verb_count = sum(1 for verb in strong_verbs if verb.lower() in resume_text.lower())
        score += min(verb_count, 4)  # Up to 4 points for action verbs

        return min(score, 20)

    def _score_completeness(self, resume_text):
        """Score resume completeness"""
        score = 10  # Base score

        # Essential elements
        if '@' in resume_text:  # Email
            score += 2
        if any(word in resume_text.lower() for word in ['phone', 'tel', '(']):  # Phone
            score += 2
        if any(word in resume_text.lower() for word in ['experience', 'work', 'employment']):
            score += 3
        if any(word in resume_text.lower() for word in ['education', 'degree', 'university', 'college']):
            score += 3

        return min(score, 20)

    def _score_differentiation(self, resume_text):
        """Score how well the resume stands out"""
        score = 12  # Base score

        # Unique elements
        if any(word in resume_text.lower() for word in ['award', 'recognition', 'honor', 'achievement']):
            score += 3
        if any(word in resume_text.lower() for word in ['project', 'portfolio', 'publication']):
            score += 2
        if any(word in resume_text.lower() for word in ['volunteer', 'community', 'leadership']):
            score += 2
        if any(word in resume_text.lower() for word in ['certification', 'certified', 'license']):
            score += 1

        return min(score, 20)

    def _generate_strengths(self, scores, resume_text):
        """Generate specific strengths based on scores and content"""
        strengths = []

        if scores['clarity'] >= 18:
            strengths.append("Excellent resume structure and organization that's easy to scan and read")
        elif scores['clarity'] >= 15:
            strengths.append("Clear, well-organized resume structure")

        if scores['impact'] >= 16:
            strengths.append("Strong use of quantified achievements and measurable results")
        elif scores['impact'] >= 12:
            strengths.append("Good inclusion of measurable results and achievements")

        if scores['completeness'] >= 18:
            strengths.append("Comprehensive coverage of all essential resume sections")

        if scores['differentiation'] >= 16:
            strengths.append("Notable unique elements that help you stand out from other candidates")

        if scores['relevance'] >= 16:
            strengths.append("Strong alignment between your experience and target career field")

        # Content-based strengths
        if any(word in resume_text.lower() for word in ['led', 'managed', 'supervised']):
            strengths.append("Demonstrated leadership and management experience")

        if len(re.findall(r'\d+%|\d+\s*percent', resume_text)) >= 3:
            strengths.append("Excellent use of specific percentages to quantify your impact")

        return strengths[:4]  # Return top 4 strengths

    def _generate_improvements(self, scores, resume_text, career_track):
        """Generate specific improvement suggestions"""
        improvements = []

        if scores['relevance'] < 15:
            improvements.append(f"Add more {career_track.lower()}-specific keywords and terminology to better align with your target field")

        if scores['impact'] < 14:
            improvements.append("Include more quantified achievements with specific numbers, percentages, or dollar amounts")

        if scores['clarity'] < 16:
            improvements.append("Improve formatting with consistent bullet points, clear section headers, and better organization")

        if scores['differentiation'] < 14:
            improvements.append("Add unique elements like awards, certifications, projects, or volunteer work to stand out")

        if scores['completeness'] < 16:
            improvements.append("Ensure all essential sections are complete: contact info, experience, education, and skills")

        # Content-based improvements
        weak_verbs = ['responsible for', 'helped with', 'assisted in', 'worked on']
        if any(phrase in resume_text.lower() for phrase in weak_verbs):
            improvements.append("Replace weak phrases like 'responsible for' with stronger action verbs like 'led', 'developed', or 'achieved'")

        if not re.search(r'\d+%|\d+\s*percent|\$[\d,]+', resume_text):
            improvements.append("Add specific metrics and numbers to demonstrate the scope and impact of your work")

        return improvements[:4]  # Return top 4 improvements

    def _generate_career_alignment(self, total_score, career_track, dream_job, life_stage):
        """Generate career alignment feedback"""
        if total_score >= 80:
            alignment = f"Excellent alignment! Your resume strongly positions you for {career_track.lower()} roles"
        elif total_score >= 65:
            alignment = f"Good alignment with {career_track.lower()}, with room for targeted improvements"
        else:
            alignment = f"Moderate alignment with {career_track.lower()}. Focus on adding more relevant experience and keywords"

        if dream_job:
            alignment += f" and specifically for your goal of '{dream_job}'."
        else:
            alignment += "."

        # Life stage specific advice
        if "Student" in life_stage:
            alignment += " As a student, emphasize academic projects, internships, and relevant coursework."
        elif "Recent Graduate" in life_stage:
            alignment += " As a recent graduate, highlight your education, projects, and any internship experience."
        elif "Career Transition" in life_stage:
            alignment += " For your career transition, focus on transferable skills and any relevant training or experience."

        return alignment

    def _generate_resources(self, scores, career_track, life_stage):
        """Generate targeted resource recommendations"""
        resources = []

        # Score-based resources
        if scores['impact'] < 15:
            resources.append("Harvard Business Review's guide to quantifying achievements on your resume")

        if scores['clarity'] < 16:
            resources.append("Resume formatting templates and best practices from industry professionals")

        # Career track specific resources
        track_resources = {
            "Technology & Software": "GitHub portfolio development and technical resume writing guides",
            "Healthcare & Medicine": "Healthcare resume templates and medical terminology resources",
            "Finance & Banking": "Financial services resume examples and industry certification guides",
            "Marketing & Communications": "Marketing portfolio development and creative resume strategies",
            "Education & Training": "Teaching resume templates and education sector job search resources",
            "Public Service & Nonprofit": "Nonprofit resume writing and public service career development resources"
        }

        if career_track in track_resources:
            resources.append(track_resources[career_track])

        # Life stage specific resources
        if "Student" in life_stage or "Graduate" in life_stage:
            resources.append("Entry-level resume writing and new graduate job search strategies")
        elif "Career Transition" in life_stage:
            resources.append("Career change resume strategies and transferable skills identification")

        # General resources
        resources.append("LinkedIn profile optimization to complement your resume")
        resources.append("Industry-specific job boards and networking opportunities in your field")

        return resources[:5]  # Return top 5 resources

# Initialize evaluator
evaluator = ResumeEvaluator()

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', 
                         career_tracks=evaluator.career_tracks,
                         life_stages=evaluator.life_stages,
                         error=None,
                         prev_data={})

@app.route('/evaluate', methods=['POST'])
def evaluate():
    # Get form data
    career_track = request.form.get('career_track')
    life_stage = request.form.get('life_stage')
    dream_job = request.form.get('dream_job')
    resume_text = request.form.get('resume_text', '')

    # Handle file upload
    if 'resume_file' in request.files:
        file = request.files['resume_file']
        if file and file.filename:
            try:
                if file.filename.endswith('.txt'):
                    resume_text = file.read().decode('utf-8')
                elif file.filename.endswith('.pdf'):
                    # Basic PDF support - install PyPDF2 for full support
                    try:
                        from PyPDF2 import PdfReader
                        import io
                        pdf_bytes = file.read()
                        pdf_stream = io.BytesIO(pdf_bytes)
                        reader = PdfReader(pdf_stream)
                        resume_text = ""
                        for page in reader.pages:
                            resume_text += page.extract_text() or ""
                    except ImportError:
                        # PyPDF2 not installed, skip PDF processing
                        pass
            except Exception as e:
                print(f"Error reading file: {e}")

    # Validation
    if not career_track or not life_stage or not dream_job:
        return render_template('index.html',
                             career_tracks=evaluator.career_tracks,
                             life_stages=evaluator.life_stages,
                             error="Please fill in all required fields.",
                             prev_data=request.form)

    if not resume_text.strip():
        return render_template('index.html',
                             career_tracks=evaluator.career_tracks,
                             life_stages=evaluator.life_stages,
                             error="Please provide your resume text or upload a file.",
                             prev_data=request.form)

    # Store user inputs
    user_inputs = {
        'career_track': career_track,
        'life_stage': life_stage,
        'dream_job': dream_job
    }

    # Evaluate resume
    evaluation = evaluator.evaluate_resume(resume_text, career_track, life_stage, dream_job)

    # Extract phrases and generate enhanced feedback
    strength_quotes = evaluator.extract_good_phrases(resume_text)
    growth_quotes = evaluator.extract_growth_phrases(resume_text)
    personal_feedback = evaluator.generate_personal_feedback(user_inputs, evaluation, resume_text)
    career_insights = evaluator.suggest_career_paths(user_inputs, resume_text)

    return render_template('result.html',
                         evaluation=evaluation,
                         user_inputs=user_inputs,
                         rubric_descriptions=evaluator.rubric_descriptions,
                         strength_quotes=strength_quotes,
                         growth_quotes=growth_quotes,
                         personal_feedback=personal_feedback,
                         career_insights=career_insights)

if __name__ == '__main__':
    app.run(debug=True)
