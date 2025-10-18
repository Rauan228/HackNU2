import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ResumeForm } from '../components/forms/ResumeForm';
import { resumesAPI } from '../services/api';

interface Experience {
  id: string;
  company: string;
  position: string;
  startDate: string;
  endDate: string;
  current: boolean;
  description: string;
}

interface Education {
  id: string;
  institution: string;
  degree: string;
  field: string;
  startDate: string;
  endDate: string;
  current: boolean;
}

interface ResumeFormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  location: string;
  desiredPosition: string;
  desiredSalary: string;
  summary: string;
  experiences: Experience[];
  education: Education[];
  skills: string[];
  languages: string[];
}

export const CreateResume: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data: ResumeFormData) => {
    setLoading(true);
    try {
      // Преобразуем данные формы в формат API
      const resumeData = {
        title: data.desiredPosition || 'Резюме',
        summary: data.summary,
        experience: data.experiences.map(exp => 
          `${exp.position} в ${exp.company} (${exp.startDate} - ${exp.current ? 'настоящее время' : exp.endDate})\n${exp.description}`
        ).join('\n\n'),
        education: data.education.map(edu => 
          `${edu.degree} по специальности ${edu.field}, ${edu.institution} (${edu.startDate} - ${edu.current ? 'настоящее время' : edu.endDate})`
        ).join('\n'),
        skills: data.skills.join(', '),
        languages: data.languages.join(', '),
        desired_position: data.desiredPosition,
        desired_salary: data.desiredSalary ? parseFloat(data.desiredSalary.replace(/[^\d]/g, '')) : undefined,
        location: data.location,
        is_public: true
      };

      await resumesAPI.createResume(resumeData);
      
      // После успешного создания перенаправляем в личный кабинет
      navigate('/dashboard');
    } catch (error) {
      console.error('Ошибка при создании резюме:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Создание резюме</h1>
          <p className="text-secondary-600">
            Заполните информацию о себе, чтобы создать профессиональное резюме
          </p>
        </div>
        
        <ResumeForm onSubmit={handleSubmit} loading={loading} />
      </div>
    </div>
  );
};

export default CreateResume;