import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { JobForm } from '../components/forms/JobForm';
import { jobsAPI } from '../services/api';
interface JobFormData {
  title: string;
  description: string;
  requirements: string;
  conditions: string;
  category: string;
  salaryMin: string;
  salaryMax: string;
  location: string;
  employmentType: string;
  experience: string;
}
export const CreateJob: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const handleSubmit = async (data: JobFormData) => {
    setLoading(true);
    setError('');
    try {
      const jobData = {
        title: data.title,
        description: data.description,
        requirements: data.requirements || undefined,
        salary_min: data.salaryMin ? parseFloat(data.salaryMin) : undefined,
        salary_max: data.salaryMax ? parseFloat(data.salaryMax) : undefined,
        location: data.location || undefined,
        employment_type: data.employmentType || undefined,
        experience_level: data.experience || undefined,
        company_name: 'Моя компания' 
      };
      await jobsAPI.createJob(jobData);
      navigate('/employer-dashboard');
    } catch (error: any) {
      console.error('Ошибка при создании вакансии:', error);
      setError(error.response?.data?.detail || 'Произошла ошибка при создании вакансии');
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
          </div>
        )}
        <JobForm onSubmit={handleSubmit} loading={loading} />
      </div>
    </div>
  );
};
export default CreateJob;
