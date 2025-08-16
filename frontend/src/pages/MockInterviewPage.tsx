import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Brain, MessageCircle, Send, RotateCcw } from 'lucide-react';
import toast from 'react-hot-toast';
import { getAxiosErrorMessage } from '../utils/helpers';
import { studentService } from '../services/studentService';

interface InterviewSession {
  session_id: string;
  status: 'active' | 'completed';
  role: string;
  job_description?: string;
  messages: Array<{
    type: 'question' | 'answer';
    content: string;
    timestamp: string;
  }>;
  feedback?: InterviewFeedback;
}

interface InterviewFeedback {
  overall_score: {
    value: number;
    description: string;
  };
  strengths: string[];
  weaknesses: string[];
  detailed_feedback: {
    communication: { score: number; feedback: string };
    technical_competency: { score: number; feedback: string };
    cultural_fit: { score: number; feedback: string };
    problem_solving: { score: number; feedback: string };
  };
  question_analysis: Array<{
    question: string;
    candidate_answer: string;
    feedback: string;
    suggested_improvement: string;
    sample_answer: string;
  }>;
  key_recommendations: string[];
  next_steps: string[];
}

export const MockInterviewPage: React.FC = () => {
  const [role, setRole] = useState('Software Engineer');
  const [jobDescription, setJobDescription] = useState('');
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [session?.messages]);

  const startInterview = async () => {
    if (!role.trim()) {
      toast.error('Please enter a role');
      return;
    }

    setIsStarting(true);
    try {
      toast.loading('Starting interview...', { id: 'start' });
      
      const formData = new FormData();
      formData.append('role', role);
      if (jobDescription.trim()) {
        formData.append('job_description', jobDescription);
      }

      const response = await studentService.startMockInterview(formData);
      
      setSession({
        session_id: response.session_id,
        role: role,
        job_description: jobDescription,
        status: 'active',
        messages: [{
          type: 'question',
          content: response.first_question,
          timestamp: new Date().toISOString()
        }]
      });

      toast.success('Interview started!', { id: 'start' });
    } catch (error: any) {
      console.error('Error starting interview:', error);
      const msg = getAxiosErrorMessage(error, 'Failed to start interview');
      toast.error(msg, { id: 'start' });
    } finally {
      setIsStarting(false);
    }
  };

  const submitAnswer = async () => {
    if (!currentAnswer.trim() || !session) return;

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('answer', currentAnswer);

      const response = await studentService.respondToInterview(session.session_id, formData);
      
      // Add the student's answer to the conversation
      const updatedMessages = [
        ...session.messages,
        {
          type: 'answer' as const,
          content: currentAnswer,
          timestamp: new Date().toISOString()
        }
      ];

      if (response.is_complete) {
        // Fetch detailed feedback
        try {
          const feedbackResponse = await studentService.getInterviewFeedback(session.session_id);
          setSession({
            ...session,
            status: 'completed',
            messages: [
              ...updatedMessages,
              {
                type: 'question' as const,
                content: response.message || 'Interview completed. Thank you for practicing!',
                timestamp: new Date().toISOString()
              }
            ],
            feedback: feedbackResponse
          });
        } catch (feedbackError) {
          // If feedback fetch fails, still mark as completed but without feedback
          console.error('Failed to fetch feedback:', feedbackError);
          setSession({
            ...session,
            status: 'completed',
            messages: [
              ...updatedMessages,
              {
                type: 'question' as const,
                content: response.message || 'Interview completed. Thank you for practicing!',
                timestamp: new Date().toISOString()
              }
            ]
          });
        }
        toast.success('Interview completed! View your detailed feedback below.');
      } else {
        // Add the next question
        setSession({
          ...session,
          messages: [
            ...updatedMessages,
            {
              type: 'question' as const,
              content: response.next_question || 'Thank you for your response. Let me ask you another question.',
              timestamp: new Date().toISOString()
            }
          ]
        });
      }

      setCurrentAnswer('');
    } catch (error: any) {
      console.error('Error submitting answer:', error);
      const msg = getAxiosErrorMessage(error, 'Failed to submit answer');
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const resetInterview = () => {
    setSession(null);
    setCurrentAnswer('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (session && session.status === 'active') {
        submitAnswer();
      } else {
        startInterview();
      }
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 flex items-center gap-2 transition-colors duration-200">
          <Brain className="h-8 w-8 text-primary-600 dark:text-primary-400"/> 
          Mock Interview Practice
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400 transition-colors duration-200">
          Practice your interview skills with AI-powered questions tailored to your resume
        </p>
      </div>

      {!session ? (
        /* Setup Form */
        <div className="card space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 transition-colors duration-200">
                Role/Position *
              </label>
              <input
                type="text"
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="e.g., Software Engineer, Data Scientist, Product Manager"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 transition-colors duration-200"
                disabled={isStarting}
              />
            </div>
            <div className="md:col-span-2">
              <label htmlFor="jobDescription" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 transition-colors duration-200">
                Job Description (Optional)
              </label>
              <textarea
                id="jobDescription"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                placeholder="Paste the job description here for more targeted questions..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 transition-colors duration-200"
                disabled={isStarting}
              />
            </div>
          </div>

          <button
            onClick={startInterview}
            disabled={isStarting || !role.trim()}
            className="btn-primary flex items-center gap-2"
          >
            <MessageCircle className="h-4 w-4" />
            {isStarting ? 'Starting Interview...' : 'Start Mock Interview'}
          </button>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-blue-800 mb-2">How it works:</h3>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• The AI will ask you questions based on your uploaded resume</li>
              <li>• Answer naturally as you would in a real interview</li>
              <li>• Questions will adapt based on your responses</li>
              <li>• <strong>The interview continues until YOU decide to stop</strong></li>
              <li>• Click "End Interview" or type "stop" when you're ready to finish</li>
            </ul>
          </div>
        </div>
      ) : (
        /* Interview Chat Interface */
        <div className="card overflow-hidden">
          {/* Interview Info Bar */}
          <div className="bg-gray-50 px-6 py-3 border-b flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div>
                <span className="font-medium text-gray-700">Role:</span>
                <span className="ml-2 text-gray-900">{session.role}</span>
              </div>
              {session.status === 'completed' && (
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                  Completed
                </span>
              )}
            </div>
            <button
              onClick={resetInterview}
              className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-800 underline"
            >
              <RotateCcw className="h-3 w-3" />
              Start New Interview
            </button>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {session.messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex ${
                  message.type === 'answer' ? 'justify-end' : 'justify-start'
                }`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                    message.type === 'answer'
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="text-xs opacity-75 mb-1">
                    {message.type === 'answer' ? 'You' : 'Interviewer'}
                  </div>
                  <div className="whitespace-pre-wrap">{message.content}</div>
                </div>
              </motion.div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          {session.status === 'active' && (
            <div className="border-t p-4">
              <div className="flex space-x-3">
                <textarea
                  value={currentAnswer}
                  onChange={(e) => setCurrentAnswer(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your answer here... (Press Enter to send, Shift+Enter for new line)"
                  rows={2}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                  disabled={isLoading}
                />
                <div className="flex flex-col gap-2">
                  <button
                    onClick={submitAnswer}
                    disabled={!currentAnswer.trim() || isLoading}
                    className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
                  >
                    <Send className="h-4 w-4" />
                    {isLoading ? 'Sending...' : 'Send'}
                  </button>
                  <button
                    onClick={() => {
                      setCurrentAnswer('stop');
                      submitAnswer();
                    }}
                    disabled={isLoading}
                    className="bg-red-100 text-red-600 px-4 py-1 rounded-lg hover:bg-red-200 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors flex items-center gap-1 text-sm"
                  >
                    <RotateCcw className="h-3 w-3" />
                    End Interview
                  </button>
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                💡 This interview will continue until you click "End Interview" or type "stop"
              </div>
            </div>
          )}

          {/* Feedback Display */}
          {session.status === 'completed' && session.feedback && (
            <div className="border-t border-gray-200 dark:border-gray-700 p-6 bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
              <h3 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-6 flex items-center gap-2 transition-colors duration-200">
                <Brain className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                Interview Feedback & Analysis
              </h3>

              {/* Overall Performance Summary */}
              {session.feedback?.overall_score && (
                <div className="mb-8 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 transition-colors duration-200">
                  <h4 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100 transition-colors duration-200">Overall Performance</h4>
                  <p className="text-gray-700 dark:text-gray-300 transition-colors duration-200">{session.feedback.overall_score.description}</p>
                </div>
              )}

              {/* Strengths and Weaknesses */}
              <div className="grid md:grid-cols-2 gap-6 mb-8">
                {session.feedback?.strengths && session.feedback.strengths.length > 0 && (
                  <div className="p-6 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800 transition-colors duration-200">
                    <h4 className="text-lg font-semibold text-green-800 dark:text-green-300 mb-4 transition-colors duration-200">💪 Strengths</h4>
                    <ul className="space-y-2">
                      {session.feedback.strengths.map((strength, index) => (
                        <li key={index} className="text-green-700 dark:text-green-200 flex items-start gap-2 transition-colors duration-200">
                          <span className="text-green-500 dark:text-green-400 mt-1">•</span>
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {session.feedback?.weaknesses && session.feedback.weaknesses.length > 0 && (
                  <div className="p-6 bg-orange-50 dark:bg-orange-900/20 rounded-lg border border-orange-200 dark:border-orange-800 transition-colors duration-200">
                    <h4 className="text-lg font-semibold text-orange-800 dark:text-orange-300 mb-4 transition-colors duration-200">🎯 Areas for Improvement</h4>
                    <ul className="space-y-2">
                      {session.feedback.weaknesses.map((weakness, index) => (
                        <li key={index} className="text-orange-700 dark:text-orange-200 flex items-start gap-2 transition-colors duration-200">
                          <span className="text-orange-500 dark:text-orange-400 mt-1">•</span>
                          <span>{weakness}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Detailed Feedback Categories */}
              {session.feedback?.detailed_feedback && (
                <div className="mb-8">
                  <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100 transition-colors duration-200">Detailed Analysis</h4>
                  <div className="grid md:grid-cols-2 gap-4">
                    {Object.entries(session.feedback.detailed_feedback).map(([category, details]) => (
                      <div key={category} className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors duration-200">
                        <h5 className="font-medium capitalize text-gray-900 dark:text-gray-100 transition-colors duration-200 mb-3">
                          {category.replace('_', ' ')}
                        </h5>
                        <p className="text-sm text-gray-600 dark:text-gray-400 transition-colors duration-200">{details.feedback}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Question Analysis */}
              {session.feedback?.question_analysis && session.feedback.question_analysis.length > 0 && (
                <div className="mb-8">
                  <h4 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100 transition-colors duration-200">Question-by-Question Analysis</h4>
                  <div className="space-y-6">
                    {session.feedback.question_analysis.map((analysis, index) => (
                      <div key={index} className="p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 transition-colors duration-200">
                        <h5 className="font-medium text-gray-900 dark:text-gray-100 mb-3 transition-colors duration-200">Question {index + 1}</h5>
                        <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-700 rounded transition-colors duration-200">
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 transition-colors duration-200">Question:</p>
                          <p className="text-gray-600 dark:text-gray-400 transition-colors duration-200">{analysis.question}</p>
                        </div>
                        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded transition-colors duration-200">
                          <p className="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1 transition-colors duration-200">Your Answer:</p>
                          <p className="text-blue-600 dark:text-blue-200 transition-colors duration-200">{analysis.candidate_answer}</p>
                        </div>
                        <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded transition-colors duration-200">
                          <p className="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1 transition-colors duration-200">Feedback:</p>
                          <p className="text-yellow-600 dark:text-yellow-200 transition-colors duration-200">{analysis.feedback}</p>
                        </div>
                        {analysis.suggested_improvement && (
                          <div className="mb-4 p-3 bg-orange-50 dark:bg-orange-900/20 rounded transition-colors duration-200">
                            <p className="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1 transition-colors duration-200">Suggested Improvement:</p>
                            <p className="text-orange-600 dark:text-orange-200 transition-colors duration-200">{analysis.suggested_improvement}</p>
                          </div>
                        )}
                        {analysis.sample_answer && (
                          <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded transition-colors duration-200">
                            <p className="text-sm font-medium text-green-700 dark:text-green-300 mb-1 transition-colors duration-200">Sample Answer:</p>
                            <p className="text-green-600 dark:text-green-200 transition-colors duration-200">{analysis.sample_answer}</p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Key Recommendations */}
              {session.feedback?.key_recommendations && session.feedback.key_recommendations.length > 0 && (
                <div className="mb-8 p-6 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 transition-colors duration-200">
                  <h4 className="text-lg font-semibold text-blue-800 dark:text-blue-300 mb-4 transition-colors duration-200">🔑 Key Recommendations</h4>
                  <ul className="space-y-2">
                    {session.feedback.key_recommendations.map((recommendation, index) => (
                      <li key={index} className="text-blue-700 dark:text-blue-200 flex items-start gap-2 transition-colors duration-200">
                        <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                        <span>{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Next Steps */}
              {session.feedback?.next_steps && session.feedback.next_steps.length > 0 && (
                <div className="p-6 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800 transition-colors duration-200">
                  <h4 className="text-lg font-semibold text-purple-800 dark:text-purple-300 mb-4 transition-colors duration-200">🚀 Next Steps</h4>
                  <ul className="space-y-2">
                    {session.feedback.next_steps.map((step, index) => (
                      <li key={index} className="text-purple-700 dark:text-purple-200 flex items-start gap-2 transition-colors duration-200">
                        <span className="text-purple-500 dark:text-purple-400 mt-1">{index + 1}.</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Start New Interview Button */}
              <div className="mt-8 text-center">
                <button
                  onClick={() => {
                    setSession(null);
                    setCurrentAnswer('');
                    setRole('Software Engineer');
                    setJobDescription('');
                  }}
                  className="bg-primary-600 hover:bg-primary-700 dark:bg-primary-500 dark:hover:bg-primary-600 text-white px-6 py-3 rounded-lg transition-colors duration-200 font-medium"
                >
                  Start New Interview
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default MockInterviewPage;
