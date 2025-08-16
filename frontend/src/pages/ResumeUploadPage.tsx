import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Upload, FileText, CheckCircle, Download, Trash2 } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { resumeService } from '../services/resumeService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import toast from 'react-hot-toast';

interface AnalysisResult {
  filename: string;
  raw_text: string;
  extracted_text: string;
  extracted_fields: string[];
  score?: number;
  suggested_edits?: string[];
  matching_jobs?: Array<{
    job_id: string;
    title: string;
    company_name: string;
    location: string;
    match_percent: number;
    matching_skills: string[];
    missing_skills: string[];
  }>;
  gemini_analysis?: any;
  scores?: any;
  top_job_suggestions?: any[];
  skill_match_details?: any;
  download_report_url?: string;
}

export const ResumeUploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploadResult, setUploadResult] = useState<AnalysisResult | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [jobDetails, setJobDetails] = useState({
    company_name: '',
    job_title: '',
    job_description: ''
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const uploadedFile = acceptedFiles[0];
    if (uploadedFile) {
      if (uploadedFile.type !== 'application/pdf') {
        toast.error('Please upload a PDF file');
        return;
      }
      if (uploadedFile.size > 10 * 1024 * 1024) { // 10MB limit
        toast.error('File size should be less than 10MB');
        return;
      }
      setFile(uploadedFile);
      setUploadResult(null);
      setAnalysisResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false
  });

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    try {
      toast.loading('Uploading and processing resume...', { id: 'upload' });
      const result = await resumeService.uploadResume(file);
      setUploadResult(result);
      toast.success('Resume uploaded successfully!', { id: 'upload' });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to upload resume', { id: 'upload' });
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    if (!file || !jobDetails.company_name || !jobDetails.job_title || !jobDetails.job_description) {
      toast.error('Please provide all job details for analysis');
      return;
    }

    setIsAnalyzing(true);
    try {
      toast.loading('Analyzing resume against job requirements...', { id: 'analyze' });
      const result = await resumeService.analyzeResume(
        file,
        jobDetails.company_name,
        jobDetails.job_title,
        jobDetails.job_description
      );
      setAnalysisResult(result);
      toast.success('Analysis completed!', { id: 'analyze' });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to analyze resume', { id: 'analyze' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDownloadReport = async () => {
    if (analysisResult?.download_report_url) {
      try {
        const filename = analysisResult.download_report_url.split('filename=')[1];
        const blob = await resumeService.downloadReport(filename);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Report downloaded successfully!');
      } catch (error) {
        toast.error('Failed to download report');
      }
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadResult(null);
    setAnalysisResult(null);
    setJobDetails({
      company_name: '',
      job_title: '',
      job_description: ''
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Resume Upload & Analysis</h1>
        <p className="mt-2 text-gray-600">
          Upload your resume for AI-powered analysis and job matching.
        </p>
      </div>

      {/* File Upload Section */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Resume</h3>
        
        {!file ? (
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
            </p>
            <p className="text-gray-600">
              Drag and drop your PDF resume, or click to browse
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Supports PDF files up to 10MB
            </p>
          </div>
        ) : (
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <FileText className="h-8 w-8 text-primary-600" />
              <div>
                <p className="font-medium text-gray-900">{file.name}</p>
                <p className="text-sm text-gray-500">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleUpload}
                disabled={isUploading}
                className="btn-primary"
              >
                {isUploading ? <LoadingSpinner size="sm" /> : 'Upload'}
              </button>
              <button
                onClick={handleReset}
                className="btn-secondary"
              >
                <Trash2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Upload Result */}
        {uploadResult && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg"
          >
            <div className="flex items-center space-x-2 mb-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="font-medium text-green-800">Upload Successful</span>
            </div>
            <p className="text-sm text-green-700">
              Resume processed. {uploadResult.extracted_fields.length} skills extracted:
            </p>
            <div className="flex flex-wrap gap-2 mt-2">
              {uploadResult.extracted_fields.slice(0, 10).map((skill, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded"
                >
                  {skill}
                </span>
              ))}
              {uploadResult.extracted_fields.length > 10 && (
                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                  +{uploadResult.extracted_fields.length - 10} more
                </span>
              )}
            </div>

            {/* Display Top 3 Job Recommendations */}
            {uploadResult.matching_jobs && uploadResult.matching_jobs.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium text-green-800 mb-2">
                  🎯 Top Job Recommendations
                </h4>
                <div className="space-y-2">
                  {uploadResult.matching_jobs.slice(0, 3).map((job, index) => (
                    <div key={index} className="bg-white border border-green-200 rounded-lg p-3">
                      <div className="flex justify-between items-start">
                        <div>
                          <h5 className="font-medium text-gray-900">{job.title}</h5>
                          <p className="text-sm text-gray-600">{job.company_name} • {job.location}</p>
                          <div className="flex items-center mt-1">
                            <span className="text-xs text-green-700 font-medium">
                              {job.match_percent}% match
                            </span>
                            <span className="mx-2 text-gray-300">•</span>
                            <span className="text-xs text-gray-600">
                              {job.matching_skills.length} skills matched
                            </span>
                          </div>
                        </div>
                        <span className="text-lg font-bold text-green-600">
                          #{index + 1}
                        </span>
                      </div>
                      {job.matching_skills && job.matching_skills.length > 0 && (
                        <div className="mt-2">
                          <p className="text-xs text-gray-500 mb-1">Matching skills:</p>
                          <div className="flex flex-wrap gap-1">
                            {job.matching_skills.slice(0, 5).map((skill, skillIndex) => (
                              <span
                                key={skillIndex}
                                className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded"
                              >
                                {skill}
                              </span>
                            ))}
                            {job.matching_skills.length > 5 && (
                              <span className="text-xs text-gray-500">
                                +{job.matching_skills.length - 5} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}
      </div>

      {/* Job Details Section */}
      {uploadResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Job Details for Analysis
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                type="text"
                value={jobDetails.company_name}
                onChange={(e) => setJobDetails(prev => ({ ...prev, company_name: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="e.g., Google, Microsoft, etc."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title
              </label>
              <input
                type="text"
                value={jobDetails.job_title}
                onChange={(e) => setJobDetails(prev => ({ ...prev, job_title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="e.g., Software Engineer, Data Scientist, etc."
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description
              </label>
              <textarea
                value={jobDetails.job_description}
                onChange={(e) => setJobDetails(prev => ({ ...prev, job_description: e.target.value }))}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Paste the job description here..."
              />
            </div>
          </div>
          <div className="mt-4">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || !jobDetails.company_name || !jobDetails.job_title || !jobDetails.job_description}
              className="btn-primary"
            >
              {isAnalyzing ? <LoadingSpinner size="sm" /> : 'Analyze Resume'}
            </button>
          </div>
        </motion.div>
      )}

      {/* Analysis Results */}
      {analysisResult && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Scores */}
          {analysisResult.scores && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Scores</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(analysisResult.scores).map(([key, scoreData]: [string, any]) => (
                  <div key={key} className="text-center">
                    <div
                      className={`text-2xl font-bold ${
                        scoreData.color === 'green' ? 'text-green-600' :
                        scoreData.color === 'yellow' ? 'text-yellow-600' :
                        scoreData.color === 'red' ? 'text-red-600' : 'text-gray-600'
                      }`}
                    >
                      {scoreData.value}%
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Gemini Analysis */}
          {analysisResult.gemini_analysis && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">AI Analysis Report</h3>
                {analysisResult.download_report_url && (
                  <button
                    onClick={handleDownloadReport}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <Download className="h-4 w-4" />
                    <span>Download Report</span>
                  </button>
                )}
              </div>
              
              <div className="space-y-4">
                {/* Profile Summary */}
                {analysisResult.gemini_analysis.profile_summary && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Profile Summary</h4>
                    <p className="text-gray-700">{analysisResult.gemini_analysis.profile_summary}</p>
                  </div>
                )}

                {/* Missing Keywords */}
                {analysisResult.gemini_analysis.missing_keywords && analysisResult.gemini_analysis.missing_keywords.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Missing Keywords</h4>
                    <div className="flex flex-wrap gap-2">
                      {analysisResult.gemini_analysis.missing_keywords.map((keyword: string, index: number) => (
                        <span
                          key={index}
                          className="px-2 py-1 bg-red-100 text-red-800 text-sm rounded"
                        >
                          {keyword}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Job Match Percentage */}
                {analysisResult.gemini_analysis.percentage_match && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Job Match</h4>
                    <div className="flex items-center space-x-4">
                      <div className="text-2xl font-bold text-primary-600">
                        {analysisResult.gemini_analysis.percentage_match}%
                      </div>
                      <p className="text-gray-600">compatibility with job requirements</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Top Job Suggestions */}
          {analysisResult.top_job_suggestions && analysisResult.top_job_suggestions.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Jobs</h3>
              <div className="space-y-3">
                {analysisResult.top_job_suggestions.slice(0, 5).map((job: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium text-gray-900">{job.title}</h4>
                      <p className="text-sm text-gray-600">{job.company_name} • {job.location}</p>
                    </div>
                    <span className="text-sm text-primary-600 font-medium">
                      {job.match_score || 'Good'}% match
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Mock Interview Questions */}
          {analysisResult.mock_interview_questions && analysisResult.mock_interview_questions.length > 0 && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">🎯 Mock Interview Questions</h3>
                <span className="text-sm text-gray-500">Based on your resume</span>
              </div>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800">
                  💡 Practice with these AI-generated questions tailored to your background and the target role.
                </p>
              </div>
              <div className="space-y-3">
                {analysisResult.mock_interview_questions.map((question: string, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex-shrink-0">
                      <span className="inline-flex items-center justify-center h-6 w-6 rounded-full bg-primary-100 text-primary-600 text-sm font-medium">
                        {index + 1}
                      </span>
                    </div>
                    <div className="flex-1">
                      <p className="text-gray-900">{question}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-sm text-amber-800">
                  💪 Want to practice with a live AI interviewer? Visit the{' '}
                  <button
                    onClick={() => window.location.href = '/mock-interview'}
                    className="text-primary-600 hover:text-primary-700 underline font-medium"
                  >
                    Mock Interview page
                  </button>{' '}
                  for an interactive interview experience!
                </p>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
};
