import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, MapPin, Clock, DollarSign, Building, Briefcase, X, Plus } from 'lucide-react';
import { useApi } from '../hooks/useApi';
import { jobService } from '../services/jobService';
import { studentService } from '../services/studentService';
import { LoadingSpinner } from '../components/LoadingSpinner';
import type { Job } from '../types';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { getAxiosErrorMessage } from '../utils/helpers';

export const JobListPage: React.FC = () => {
  const { data: jobs, loading, error, execute: fetchJobs } = useApi<Job[]>();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedExperience, setSelectedExperience] = useState('');
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  const [skillInput, setSkillInput] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const { user } = useAuth();

  // Predefined common skills to avoid dependency on fetched job skills
  const commonSkills = [
    'JavaScript', 'TypeScript', 'React', 'Node.js', 'Python', 'Java', 'C++', 'SQL',
    'HTML', 'CSS', 'Angular', 'Vue.js', 'PHP', 'Ruby', 'Go', 'Rust', 'Swift',
    'Kotlin', 'C#', '.NET', 'Spring', 'Django', 'Flask', 'Express.js', 'MongoDB',
    'PostgreSQL', 'MySQL', 'Redis', 'Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP',
    'Git', 'Jenkins', 'Linux', 'Agile', 'Scrum', 'REST API', 'GraphQL', 'Machine Learning',
    'Data Science', 'AI', 'DevOps', 'CI/CD', 'Testing', 'Unit Testing', 'Integration Testing'
  ];

  // Manual search function - only triggers on button click
  const handleSearch = async () => {
    setIsSearching(true);
    setHasSearched(true);
    try {
      await fetchJobs(() => jobService.getJobs({
        // Pass search parameters to backend if needed
        // For now, we'll do client-side filtering
      }));
    } catch (error) {
      toast.error(getAxiosErrorMessage(error, 'Failed to search jobs'));
      setFilteredJobs([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Add skill function
  const addSkill = (skill: string) => {
    const trimmedSkill = skill.trim();
    if (trimmedSkill && !selectedSkills.includes(trimmedSkill)) {
      setSelectedSkills([...selectedSkills, trimmedSkill]);
      setSkillInput('');
    }
  };

  // Remove skill function
  const removeSkill = (skillToRemove: string) => {
    setSelectedSkills(selectedSkills.filter(skill => skill !== skillToRemove));
  };

  // Handle enter key for adding skills
  const handleSkillKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill(skillInput);
    }
  };

  // Handle search on Enter key
  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSearch();
    }
  };

  useEffect(() => {
    // Initial setup complete - no need to set skills array
  }, []);

  useEffect(() => {
    if (!jobs) {
      setFilteredJobs([]);
      return;
    }
    
    let filtered = jobs;
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(job => 
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Skills filter
    if (selectedSkills.length > 0) {
      filtered = filtered.filter(job =>
        selectedSkills.some(skill =>
          job.skills_required.some(jobSkill =>
            jobSkill.toLowerCase().includes(skill.toLowerCase())
          )
        )
      );
    }
    
    // Experience filter
    if (selectedExperience) {
      filtered = filtered.filter(job => job.experience_level === selectedExperience);
    }
    
    setFilteredJobs(filtered);
  }, [jobs, searchTerm, selectedSkills, selectedExperience]);

  const [applyingId, setApplyingId] = useState<string | null>(null);

  const handleApply = async (jobId: string) => {
    if (!user || user.role !== 'student') {
      toast.error('Only students can apply to jobs');
      return;
    }

    setApplyingId(jobId);
    try {
      await studentService.applyToJob(jobId);
      toast.success('Application submitted successfully!');
    } catch (error) {
      toast.error(getAxiosErrorMessage(error, 'Failed to submit application'));
    } finally {
      setApplyingId(null);
    }
  };

  const experienceLevels = ['Entry Level', 'Mid Level', 'Senior Level', 'Executive'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100 transition-colors duration-200">Job Opportunities</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400 transition-colors duration-200">
          Browse and apply to jobs that match your skills and experience.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 transition-colors duration-200">
        <div className="space-y-4">
          {/* Search Bar */}
          <div className="flex space-x-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400 dark:text-gray-500" />
              <input
                type="text"
                placeholder="Search jobs, companies, or keywords..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={handleSearchKeyPress}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:focus:ring-primary-400 focus:border-primary-500 dark:focus:border-primary-400 transition-colors duration-200"
              />
            </div>
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:bg-primary-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="h-4 w-4" />
                  <span>Search</span>
                </>
              )}
            </button>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Skills Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Skills
              </label>
              
              {/* Selected Skills Tags */}
              {selectedSkills.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-2">
                  {selectedSkills.map(skill => (
                    <span
                      key={skill}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800"
                    >
                      {skill}
                      <button
                        onClick={() => removeSkill(skill)}
                        className="ml-2 h-4 w-4 rounded-full hover:bg-primary-200 flex items-center justify-center"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
              
              {/* Skill Input */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Type a skill and press Enter (e.g., React, Python, JavaScript)"
                  value={skillInput}
                  onChange={(e) => setSkillInput(e.target.value)}
                  onKeyPress={handleSkillKeyPress}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <button
                  onClick={() => addSkill(skillInput)}
                  disabled={!skillInput.trim()}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-primary-600 hover:text-primary-700 disabled:text-gray-400"
                >
                  <Plus className="h-4 w-4" />
                </button>
              </div>
              
              {/* Skill Suggestions */}
              <div className="mt-2">
                <p className="text-xs text-gray-500 mb-1">Popular skills:</p>
                <div className="flex flex-wrap gap-1">
                  {commonSkills.slice(0, 8).filter(skill => !selectedSkills.includes(skill)).map(skill => (
                    <button
                      key={skill}
                      onClick={() => addSkill(skill)}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                    >
                      {skill}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Experience Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level
              </label>
              <select
                value={selectedExperience}
                onChange={(e) => setSelectedExperience(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">All Levels</option>
                {experienceLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Filter Summary */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              {hasSearched ? (
                <>
                  {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
                  {(searchTerm || selectedSkills.length > 0 || selectedExperience) && (
                    <span className="ml-2 text-primary-600">
                      • {[
                        searchTerm && `"${searchTerm}"`,
                        selectedSkills.length > 0 && `${selectedSkills.length} skill${selectedSkills.length !== 1 ? 's' : ''}`,
                        selectedExperience && selectedExperience
                      ].filter(Boolean).join(', ')}
                    </span>
                  )}
                </>
              ) : (
                'Use search or filters to find jobs'
              )}
            </p>
            <button
              onClick={() => {
                setSearchTerm('');
                setSelectedSkills([]);
                setSelectedExperience('');
                setSkillInput('');
                setHasSearched(false);
                setFilteredJobs([]);
              }}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium"
            >
              Clear All
            </button>
          </div>
        </div>
      </div>

      {/* Job List */}
      <div className="space-y-4">
        {hasSearched ? (
          filteredJobs.map((job, index) => (
            <motion.div
              key={job.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg dark:hover:shadow-xl transition-all duration-200 border border-gray-200 dark:border-gray-700"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <Building className="h-5 w-5 text-gray-500" />
                    <span className="text-sm text-gray-600">{job.company_name}</span>
                  </div>
                  
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">{job.title}</h3>
                  
                  <div className="flex items-center space-x-4 mb-3 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <MapPin className="h-4 w-4" />
                      <span>{job.location}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Briefcase className="h-4 w-4" />
                      <span>{job.experience_level}</span>
                    </div>
                    {job.salary_range && (
                      <div className="flex items-center space-x-1">
                        <DollarSign className="h-4 w-4" />
                        <span>{job.salary_range}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4" />
                      <span>{new Date(job.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  <p className="text-gray-700 mb-4 line-clamp-2">{job.description}</p>

                  {/* Skills */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {job.skills_required.slice(0, 5).map((skill, skillIndex) => (
                      <span
                        key={skillIndex}
                        className="px-3 py-1 bg-primary-100 text-primary-800 text-xs rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                    {job.skills_required.length > 5 && (
                      <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                        +{job.skills_required.length - 5} more
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  {user?.role === 'student' ? (
                    <button
                      onClick={() => handleApply(job.id)}
                      disabled={applyingId === job.id}
                      className="btn-primary px-6 py-2 text-sm disabled:opacity-60"
                    >
                      {applyingId === job.id ? 'Applying…' : 'Apply Now'}
                    </button>
                  ) : (
                    <div className="text-xs text-gray-500 text-right mb-2">Recruiter view</div>
                  )}
                  <button
                    onClick={() => navigate(`/jobs/${job.id}`)}
                    className="btn-secondary px-6 py-2 text-sm"
                  >
                    View Details
                  </button>
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <Search className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Ready to find your next opportunity?</h3>
            <p className="mt-1 text-sm text-gray-500">
              Enter keywords in the search bar and click "Search" to discover jobs that match your skills and interests.
            </p>
            <button
              onClick={handleSearch}
              className="mt-4 bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              Browse All Jobs
            </button>
          </motion.div>
        )}
      </div>

      {/* No Results */}
      {hasSearched && filteredJobs.length === 0 && !loading && !error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your search criteria or filters.
          </p>
        </motion.div>
      )}

      {/* Error State */}
      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="bg-red-50 border border-red-200 rounded-lg p-4"
        >
          <p className="text-red-800 text-sm">
            Unable to load jobs. Please try refreshing the page.
          </p>
        </motion.div>
      )}
    </motion.div>
  );
};
