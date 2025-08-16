import json
import os
from io import BytesIO
import base64
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2
from .job_matcher import find_matching_jobs

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def pdf_to_text(pdf_bytes):
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text.strip()

async def get_gemini_response(resume_text, job_description, skill_fields):
    # First, get matching jobs from MongoDB
    matching_jobs = await find_matching_jobs(skill_fields, job_description=job_description)
    
    # Format job matches for the prompt
    job_matches_text = "\n".join([
        f"- {job['title']} at {job['company_name']} ({job['match_percent']}% match)"
        f"\n  Matching skills: {', '.join(job['matching_skills'])}"
        f"\n  Missing skills: {', '.join(job['missing_skills'])}"
        for job in matching_jobs
    ])

    prompt = f"""
    Resume Text: {resume_text}

    Candidate Description: {job_description}

    Extracted Skills: {', '.join(skill_fields)}

    Top Matching Jobs Found:
    {job_matches_text}

    Tasks:
    1. List missing keywords for job matching, particularly focusing on the skills needed for the top matching jobs.
    2. Provide a profile summary that highlights strengths relative to the matching jobs.
    3. Return a resume quality score (0-100).
    4. Return scores for tone & style, content, and structure (0-100 each).
    5. Calculate percentage match for each of the top jobs identified.
    6. Analyze keyword optimization for ATS (Applicant Tracking System).
    7. Provide an overall ATS resume score (0-100).
    8. Suggest specific improvements to increase the ATS resume score and better match the identified job opportunities.
    
    Respond in JSON format with keys: 
    missing_keywords, profile_summary, resume_quality_score, tone_style_score, 
    content_score, structure_score, job_matches (array of job match percentages), 
    keyword_optimization, ats_resume_score, improvement_suggestions,
    best_fit_roles (array of job titles that are the best match based on the analysis)
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        print("Gemini Response:")
        print(response.text)
        
        # Parse the response and add the matching jobs data
        try:
            response_data = json.loads(response.text)
            response_data["matching_jobs"] = matching_jobs
            return json.dumps(response_data)
        except json.JSONDecodeError:
            return response.text
            
    except Exception as e:
        print("Error in Gemini API:", e)
        return json.dumps({
            "error": str(e),
            "matching_jobs": matching_jobs  # Still return the job matches even if Gemini fails
        })

async def get_mock_interview_questions_for_analysis(resume_text, job_description="General position"):
    """
    Generate mock interview questions specifically for resume analysis display.
    Returns a list of 5-6 relevant interview questions based on the resume.
    """
    prompt = f"""
    You are an experienced interviewer. Based on the candidate's resume, generate 5-6 relevant mock interview questions that would help assess this candidate.

    Resume: {resume_text}
    Target Role: {job_description}

    Generate questions that cover:
    1. Technical skills mentioned in the resume
    2. Experience and projects from the resume  
    3. Behavioral/soft skills assessment
    4. Role-specific questions based on the job description
    5. Career goals and motivations

    Respond with ONLY a JSON array of questions, no additional text:
    [
        "Question 1 about technical skills",
        "Question 2 about specific project experience", 
        "Question 3 about teamwork/collaboration",
        "Question 4 about problem-solving",
        "Question 5 about career goals",
        "Question 6 about role-specific experience"
    ]
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Clean up the response
        response_text = response.text.strip()
        
        # Remove any markdown code block markers
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        print("Mock Interview Questions Response:", response_text)
        
        # Parse the JSON array of questions
        try:
            questions = json.loads(response_text)
            if isinstance(questions, list):
                return questions
            else:
                # If not a list, extract questions from dict if needed
                if isinstance(questions, dict) and "questions" in questions:
                    return questions["questions"]
                else:
                    # Fallback: return the first 6 values if it's a dict
                    return list(questions.values())[:6] if isinstance(questions, dict) else []
        except json.JSONDecodeError:
            # Fallback: extract questions using regex
            import re
            questions = re.findall(r'"([^"]+\?)"', response_text)
            return questions[:6] if questions else []
            
    except Exception as e:
        print(f"Error generating mock interview questions: {e}")
        # Return fallback questions based on common interview patterns
        return [
            "Tell me about yourself and your background.",
            "What experience do you have with the key technologies mentioned in your resume?",
            "Describe a challenging project you've worked on and how you overcame obstacles.",
            "How do you approach learning new technologies or skills?",
            "Tell me about a time you worked effectively in a team.",
            "Where do you see yourself in your career in the next 3-5 years?"
        ]

async def get_gemini_mock_interview_response(resume_text, job_description):
    """
    Specialized function for generating mock interview questions with better JSON handling.
    """
    prompt = f"""
    You are an experienced technical recruiter. Based on the candidate's resume and job requirements, generate interview questions.
    
    Resume: {resume_text}
    Job Description: {job_description}
    
    Respond ONLY with valid JSON in this exact format:
    {{
        "technical_questions": [
            "Question about specific technical skills from resume",
            "Question about frameworks or tools mentioned",
            "Question about problem-solving approach",
            "Question about experience with technologies in job description",
            "Question about system design or architecture"
        ],
        "behavioral_questions": [
            "Question about teamwork and collaboration",
            "Question about handling challenges and pressure",
            "Question about learning and adaptability"
        ],
        "fit_analysis": "Analysis of how well the candidate's background aligns with the role requirements",
        "focus_areas": [
            "Key technical area to assess",
            "Important soft skill to evaluate", 
            "Critical experience area to verify"
        ]
    }}
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Clean up the response text
        response_text = response.text.strip()
        
        # Remove any markdown code block markers
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        print("Cleaned Gemini Response for Mock Interview:")
        print(response_text)
        
        # Try to parse as JSON
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Extract JSON using regex if direct parsing fails
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise Exception("Could not extract valid JSON from response")
                
    except Exception as e:
        print(f"Error in get_gemini_mock_interview_response: {e}")
        # Return a fallback response
        return {
            "technical_questions": [
                "What specific experience do you have with the technologies mentioned in this role?",
                "Can you walk me through your approach to solving complex technical problems?",
                "How do you ensure code quality and maintainability in your projects?",
                "Describe a challenging technical decision you had to make recently.",
                "What strategies do you use for debugging and troubleshooting?"
            ],
            "behavioral_questions": [
                "Tell me about a time when you had to work under tight deadlines.",
                "How do you approach learning new technologies or frameworks?",
                "Describe a situation where you had to collaborate with a difficult team member."
            ],
            "fit_analysis": "Based on the resume, the candidate shows relevant technical experience. Further discussion needed to assess cultural fit and specific project experience.",
            "focus_areas": ["Technical expertise validation", "Problem-solving methodology", "Team collaboration skills"],
            "error": str(e)
        }

async def get_gemini_interview_question(resume_text, role, job_description, conversation_history):
    """
    Generate a single interview question based on resume, role, and conversation history.
    Creates a continuous conversation flow that only stops when user explicitly requests it.
    """
    # Analyze conversation to understand current state
    total_questions = len([msg for msg in conversation_history if msg.get("type") == "question"])
    recent_messages = conversation_history[-6:] if conversation_history else []
    
    # Track topics discussed and follow-up counts
    topics_covered = set()
    follow_up_count = 0
    
    # Analyze recent conversation for topic tracking
    if recent_messages:
        for i, msg in enumerate(recent_messages):
            if msg.get("type") == "question":
                question_content = msg.get("content", "").lower()
                # Identify topic based on keywords
                if any(keyword in question_content for keyword in ["project", "experience", "worked on", "built", "developed"]):
                    topics_covered.add("projects")
                elif any(keyword in question_content for keyword in ["skill", "technology", "programming", "language", "framework"]):
                    topics_covered.add("technical_skills")
                elif any(keyword in question_content for keyword in ["team", "collaboration", "leadership", "challenge", "difficult"]):
                    topics_covered.add("behavioral")
                elif any(keyword in question_content for keyword in ["background", "yourself", "experience", "career"]):
                    topics_covered.add("background")
                elif any(keyword in question_content for keyword in ["company", "culture", "work environment", "team structure"]):
                    topics_covered.add("company_culture")
                elif any(keyword in question_content for keyword in ["goal", "future", "aspiration", "career path"]):
                    topics_covered.add("career_goals")
    
    # Check if we're following up on the same topic too much
    if len(recent_messages) >= 4:
        last_two_questions = [msg.get("content", "").lower() for msg in recent_messages[-4:] if msg.get("type") == "question"]
        if len(last_two_questions) >= 2:
            # Simple topic similarity check
            common_words = set(last_two_questions[-1].split()) & set(last_two_questions[-2].split())
            if len(common_words) >= 2:  # If questions share significant words
                follow_up_count = 2  # Force topic change
    
    # Format conversation history for context (limit to recent messages)
    history_text = ""
    if recent_messages:
        for msg in recent_messages:
            if msg.get("type") == "question":
                history_text += f"Previous Question: {msg.get('content', '')}\n"
            elif msg.get("type") == "answer":
                history_text += f"Student Answer: {msg.get('content', '')}\n"
    
    # Create intelligent prompt based on conversation state
    if total_questions == 0:
        # First question - always start with introduction
        prompt_strategy = "introduction"
    elif follow_up_count >= 2:
        # Too many follow-ups - force topic change
        prompt_strategy = "new_topic"
    else:
        # Analyze last answer quality to decide on follow-up vs new topic
        last_answer = ""
        for msg in reversed(recent_messages):
            if msg.get("type") == "answer":
                last_answer = msg.get("content", "")
                break
        
        # Simple answer quality check (length and keywords)
        if len(last_answer.split()) < 15 or last_answer.lower().count("i don't") > 0:
            prompt_strategy = "follow_up"
        else:
            prompt_strategy = "new_topic"
    
    # Select next topic to cover (expanded list for longer interviews)
    all_topics = ["projects", "technical_skills", "behavioral", "background", "company_culture", "career_goals", "problem_solving", "learning_approach"]
    uncovered_topics = [topic for topic in all_topics if topic not in topics_covered]
    
    # Cycle through topics or revisit with different angles
    if uncovered_topics:
        next_topic = uncovered_topics[0]
    else:
        # All main topics covered, cycle back with different angles
        topic_rotation = ["technical_deep_dive", "leadership_scenarios", "innovation_thinking", "industry_insights"]
        next_topic = topic_rotation[total_questions % len(topic_rotation)]
    
    # Build context-aware prompt
    prompt = f"""
    You are conducting a dynamic mock interview that continues until the candidate chooses to stop.
    
    Current status:
    - Total questions asked: {total_questions}
    - Strategy: {prompt_strategy}
    - Next topic to cover: {next_topic}
    - Topics already covered: {', '.join(topics_covered) if topics_covered else 'none'}
    
    Context:
    - Role: {role}
    - Job Description: {job_description or "Not provided"}
    - Resume: {resume_text[:800]}...
    
    Recent Conversation:
    {history_text}
    
    INSTRUCTIONS:
    """
    
    if prompt_strategy == "introduction":
        prompt += """
        Generate an opening question that:
        - Welcomes the candidate warmly
        - Asks them to introduce themselves
        - Is conversational and puts them at ease
        Example: "Thank you for joining me today. Let's start with you telling me a bit about yourself and what interests you about this role."
        """
    elif prompt_strategy == "follow_up":
        prompt += """
        The candidate's last answer was brief or unclear. Generate a follow-up question that:
        - Gently probes for more details
        - Helps them elaborate on their experience
        - Is encouraging and supportive
        - Stays on the same topic but digs deeper
        """
    elif prompt_strategy == "new_topic":
        if next_topic == "projects":
            prompt += """
            Ask about a specific project from their resume:
            - Reference something mentioned in their resume
            - Ask about challenges, solutions, or learning outcomes
            - Make it conversational, not interrogative
            """
        elif next_topic == "technical_skills":
            prompt += """
            Ask about their technical expertise:
            - Focus on skills relevant to the role
            - Ask about experience with specific technologies
            - Could ask about a technical decision or approach
            """
        elif next_topic == "behavioral":
            prompt += """
            Ask a behavioral question:
            - About teamwork, leadership, or problem-solving
            - Keep it relevant to their experience level
            - Ask for specific examples
            """
        elif next_topic == "background":
            prompt += """
            Ask about their career journey or aspirations:
            - What led them to this field
            - Their career goals
            - What they're looking for in their next role
            """
        elif next_topic == "company_culture":
            prompt += """
            Ask about fit and work environment preferences:
            - What type of work environment they thrive in
            - How they handle different company cultures
            - Their collaboration style
            """
        elif next_topic == "career_goals":
            prompt += """
            Ask about their future aspirations:
            - Where they see themselves in 3-5 years
            - What skills they want to develop
            - What motivates them professionally
            """
        elif next_topic == "problem_solving":
            prompt += """
            Present a hypothetical scenario or ask about problem-solving approach:
            - How they approach complex problems
            - A technical challenge they might face in this role
            - Their debugging or troubleshooting methodology
            """
        elif next_topic == "learning_approach":
            prompt += """
            Ask about continuous learning and adaptation:
            - How they stay updated with technology trends
            - A time they had to learn something completely new
            - Their approach to professional development
            """
        else:
            # Advanced topics for longer interviews
            prompt += """
            Ask an advanced question about:
            - Leadership potential or mentoring experience
            - Innovation or creative problem solving
            - Industry trends and insights
            - Strategic thinking or decision making
            """
    
    prompt += """
    
    IMPORTANT:
    - Generate ONLY the question text
    - Keep it conversational and natural
    - No more than 2 sentences
    - Don't repeat previous questions
    - Be encouraging and professional
    - This interview continues until the candidate chooses to stop
    - Never suggest ending the interview - let it flow naturally
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        question = response.text.strip()
        
        # Clean up any unwanted formatting
        if question.startswith('"') and question.endswith('"'):
            question = question[1:-1]
        
        # Remove any instruction artifacts
        question = question.replace("Question:", "").replace("Ask:", "").strip()
        
        # Fallback questions by strategy if response is poor
        if len(question) < 10:
            if prompt_strategy == "introduction":
                question = "Thank you for joining me today. Could you start by telling me a bit about yourself and what interests you about this role?"
            elif prompt_strategy == "follow_up":
                question = "That's interesting. Could you tell me more about that experience and what you learned from it?"
            elif next_topic == "projects":
                question = "I'd love to hear about a project you've worked on that you're particularly proud of. What was your role and what challenges did you face?"
            elif next_topic == "technical_skills":
                question = "What technologies or tools have you enjoyed working with the most, and why?"
            elif next_topic == "behavioral":
                question = "Can you describe a time when you had to overcome a significant challenge in a team setting?"
            elif next_topic == "career_goals":
                question = "Where do you see yourself professionally in the next few years, and what steps are you taking to get there?"
            else:
                question = "What aspect of this role excites you the most, and how does it align with your career goals?"
        
        return question
        
    except Exception as e:
        print(f"Error generating interview question: {e}")
        # Return safe fallback based on question count
        if total_questions == 0:
            return "Thank you for joining me today. Could you start by telling me a bit about yourself and what interests you about this role?"
        else:
            return "Can you tell me more about your experience and what motivates you in your work?"

async def generate_interview_feedback(resume_text, role, job_description, conversation_history):
    """
    Generate detailed feedback after an interview session including strengths, weaknesses, and suggested answers.
    """
    # Extract questions and answers from conversation history
    qa_pairs = []
    current_question = None
    
    for message in conversation_history:
        if message.get("type") == "question":
            current_question = message.get("content", "")
        elif message.get("type") == "answer" and current_question:
            qa_pairs.append({
                "question": current_question,
                "answer": message.get("content", "")
            })
            current_question = None
    
    # Format conversation for analysis
    conversation_text = ""
    for i, qa in enumerate(qa_pairs, 1):
        conversation_text += f"Q{i}: {qa['question']}\nA{i}: {qa['answer']}\n\n"
    
    prompt = f"""
    You are an experienced interview coach providing detailed feedback on a mock interview session.
    
    CANDIDATE INFORMATION:
    Resume: {resume_text[:1000]}...
    Target Role: {role}
    Job Description: {job_description or "General position"}
    
    INTERVIEW CONVERSATION:
    {conversation_text}
    
    Please provide comprehensive feedback in the following JSON format:
    {{
        "overall_score": {{
            "value": 75,
            "description": "Good overall performance with room for improvement"
        }},
        "strengths": [
            "Clear communication and articulate responses",
            "Strong technical knowledge demonstrated",
            "Good examples provided for behavioral questions"
        ],
        "weaknesses": [
            "Could provide more specific details in technical answers",
            "Answers were sometimes too brief",
            "Could demonstrate more enthusiasm for the role"
        ],
        "detailed_feedback": {{
            "communication": {{
                "score": 80,
                "feedback": "Spoke clearly and confidently. Could improve by providing more structured answers using the STAR method."
            }},
            "technical_competency": {{
                "score": 75,
                "feedback": "Demonstrated solid technical understanding. Consider providing more specific examples of technologies used."
            }},
            "cultural_fit": {{
                "score": 70,
                "feedback": "Shows good alignment with role requirements. Could express more specific interest in company culture."
            }},
            "problem_solving": {{
                "score": 72,
                "feedback": "Good analytical thinking demonstrated. Could walk through problem-solving process more systematically."
            }}
        }},
        "question_analysis": [
            {{
                "question": "First question from the interview",
                "candidate_answer": "The candidate's actual answer",
                "feedback": "Specific feedback on this answer",
                "suggested_improvement": "How this answer could be improved",
                "sample_answer": "An example of a strong answer to this question"
            }}
        ],
        "key_recommendations": [
            "Practice the STAR method for behavioral questions",
            "Prepare more specific technical examples",
            "Research the company culture and values more thoroughly",
            "Work on expressing enthusiasm and genuine interest"
        ],
        "next_steps": [
            "Review technical concepts mentioned in the job description",
            "Practice answering behavioral questions with specific examples",
            "Research the company's recent projects and initiatives",
            "Prepare thoughtful questions to ask the interviewer"
        ]
    }}
    
    IMPORTANT: 
    - Provide specific, actionable feedback
    - Include actual quotes from the candidate's answers where relevant
    - Suggest concrete improvements for each weak area
    - Provide realistic sample answers that align with the candidate's background
    - Be encouraging while being honest about areas for improvement
    - Consider the target role and job requirements in your assessment
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        
        # Clean up the response
        response_text = response.text.strip()
        
        # Remove any markdown code block markers
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        print("Interview Feedback Response:", response_text)
        
        # Parse the JSON response
        try:
            feedback_data = json.loads(response_text)
            return feedback_data
        except json.JSONDecodeError:
            # Extract JSON using regex if direct parsing fails
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise Exception("Could not extract valid JSON from feedback response")
                
    except Exception as e:
        print(f"Error generating interview feedback: {e}")
        # Return fallback feedback structure
        return {
            "overall_score": {
                "value": 75,
                "description": "Good interview performance with areas for growth"
            },
            "strengths": [
                "Participated actively in the interview",
                "Answered questions thoughtfully",
                "Demonstrated relevant experience"
            ],
            "weaknesses": [
                "Could provide more detailed examples",
                "Consider using the STAR method for behavioral questions",
                "Practice expressing enthusiasm for the role"
            ],
            "detailed_feedback": {
                "communication": {
                    "score": 75,
                    "feedback": "Good communication skills demonstrated. Continue practicing to improve clarity and structure."
                },
                "technical_competency": {
                    "score": 70,
                    "feedback": "Solid technical foundation. Consider preparing more specific examples for technical discussions."
                },
                "cultural_fit": {
                    "score": 75,
                    "feedback": "Good alignment with role. Research company culture more deeply for stronger connection."
                },
                "problem_solving": {
                    "score": 70,
                    "feedback": "Analytical thinking evident. Practice explaining thought processes more systematically."
                }
            },
            "question_analysis": [],
            "key_recommendations": [
                "Practice the STAR method for answering behavioral questions",
                "Prepare specific technical examples from your experience",
                "Research target company's culture and recent developments",
                "Work on expressing genuine enthusiasm for opportunities"
            ],
            "next_steps": [
                "Review job requirements and align your examples accordingly",
                "Practice mock interviews with peers or mentors",
                "Prepare thoughtful questions about the role and company",
                "Continue building relevant skills and experience"
            ],
            "error": str(e)
        }


