import { useState, useEffect } from 'react';
import { jobService } from '../services/jobService';
import { useLoading } from './useLoading';
import type { Job } from '../types';

export const useJobs = (params?: {
  skip?: number;
  limit?: number;
  location?: string;
  company?: string;
  skills?: string[];
}) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const { isLoading, error, executeAsync } = useLoading();

  const fetchJobs = async () => {
    const data = await executeAsync(() => jobService.getJobs(params));
    if (data) {
      setJobs(data);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, [params?.skip, params?.limit, params?.location, params?.company]);

  const refreshJobs = () => {
    fetchJobs();
  };

  return {
    jobs,
    isLoading,
    error,
    refreshJobs,
  };
};

export const useJobDetails = (jobId: string | null) => {
  const [job, setJob] = useState<Job | null>(null);
  const { isLoading, error, executeAsync } = useLoading();

  useEffect(() => {
    if (jobId) {
      const fetchJob = async () => {
        const data = await executeAsync(() => jobService.getJobDetails(jobId));
        if (data) {
          setJob(data);
        }
      };
      fetchJob();
    }
  }, [jobId]);

  return {
    job,
    isLoading,
    error,
  };
};

export const useMyJobs = () => {
  const [myJobs, setMyJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const { isLoading, error, executeAsync } = useLoading();

  const fetchMyJobs = async () => {
    const data = await executeAsync(() => jobService.getMyJobs());
    if (data) {
      setMyJobs(data.jobs);
      setTotalJobs(data.total_jobs);
    }
  };

  useEffect(() => {
    fetchMyJobs();
  }, []);

  const refreshMyJobs = () => {
    fetchMyJobs();
  };

  return {
    myJobs,
    totalJobs,
    isLoading,
    error,
    refreshMyJobs,
  };
};
