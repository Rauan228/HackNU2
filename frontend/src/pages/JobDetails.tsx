import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Badge, Card, CardBody, CardHeader } from '../components/ui';
import { ApplicationModal } from '../components/modals/ApplicationModal';
// @ts-ignore
import { SmartBotWidget } from '../components/SmartBotWidget';
import { applicationsAPI } from '../services/api';

interface Job {
  id: string;
  title: string;
  company: string;
  location: string;
  salaryMin?: number;
  salaryMax?: number;
  employmentType: string;
  experience: string;
  category: string;
  description: string;
  requirements: string;
  conditions: string;
  postedDate: string;
  companyDescription?: string;
  contactEmail?: string;
}

const employmentTypeLabels: Record<string, string> = {
  'full-time': 'Полная занятость',
  'part-time': 'Частичная занятость',
  'contract': 'Контракт',
  'internship': 'Стажировка',
  'remote': 'Удаленная работа',
};

const experienceLabels: Record<string, string> = {
  'no-experience': 'Без опыта',
  '1-3': '1-3 года',
  '3-5': '3-5 лет',
  '5-10': '5-10 лет',
  '10+': 'Более 10 лет',
};

const categoryLabels: Record<string, string> = {
  'it': 'IT и разработка',
  'marketing': 'Маркетинг',
  'sales': 'Продажи',
  'design': 'Дизайн',
  'finance': 'Финансы',
  'hr': 'HR',
  'management': 'Менеджмент',
  'education': 'Образование',
  'healthcare': 'Медицина',
  'other': 'Другое',
};

export const JobDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [isApplicationModalOpen, setIsApplicationModalOpen] = useState(false);
  const [isApplied, setIsApplied] = useState(false);
  const [showSmartBot, setShowSmartBot] = useState(false);
  const [isSmartBotMinimized, setIsSmartBotMinimized] = useState(false);
  const [applicationId, setApplicationId] = useState<number | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        // TODO: Заменить на реальный API вызов
        // const response = await fetch(`/api/jobs/${id}`);
        // const jobData = await response.json();
        
        // Временные данные для демонстрации
        const mockJob: Job = {
          id: id || '1',
          title: 'Senior Frontend Developer',
          company: 'TechCorp Kazakhstan',
          location: 'Алматы',
          salaryMin: 500000,
          salaryMax: 800000,
          employmentType: 'full-time',
          experience: '3-5',
          category: 'it',
          description: 'Мы ищем опытного Frontend разработчика для работы над инновационными проектами. Вы будете работать с современными технологиями и создавать пользовательские интерфейсы мирового класса.',
          requirements: 'Опыт работы с React, TypeScript, современными инструментами сборки. Знание принципов UX/UI дизайна. Опыт работы с REST API и GraphQL.',
          conditions: 'Официальное трудоустройство, медицинская страховка, гибкий график работы, возможность удаленной работы, корпоративное обучение.',
          postedDate: '2024-01-15',
          companyDescription: 'TechCorp Kazakhstan - ведущая IT-компания, специализирующаяся на разработке корпоративных решений.',
          contactEmail: 'hr@techcorp.kz'
        };
        
        setJob(mockJob);
        
        // TODO: Проверить, подавал ли пользователь заявку на эту вакансию
        // const applicationResponse = await fetch(`/api/applications/check/${id}`);
        // setIsApplied(applicationResponse.ok);
        
      } catch (error) {
        console.error('Ошибка при загрузке вакансии:', error);
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchJob();
    }
  }, [id]);

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Зарплата не указана';
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} ₸`;
    if (min) return `от ${min.toLocaleString()} ₸`;
    if (max) return `до ${max.toLocaleString()} ₸`;
    return 'Зарплата не указана';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleApply = () => {
    setIsApplicationModalOpen(true);
  };

  const handleApplicationSubmit = async (data: { resumeId: string; coverLetter: string }) => {
    try {
      const applicationData = {
        job_id: parseInt(job?.id || '0'),
        resume_id: parseInt(data.resumeId),
        cover_letter: data.coverLetter
      };
      
      const response = await applicationsAPI.createApplication(applicationData);
      console.log('Заявка отправлена:', data);
      setIsApplied(true);
      setIsApplicationModalOpen(false);
      setApplicationId(response.data.id);
      setShowSmartBot(true);
      setIsSmartBotMinimized(false);
    } catch (error) {
      console.error('Ошибка при отправке заявки:', error);
      throw error;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600">Загрузка вакансии...</p>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Вакансия не найдена</h1>
          <Button onClick={() => navigate('/jobs')}>
            Вернуться к поиску
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Навигация */}
        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-primary-600 hover:text-primary-700 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Назад
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Основная информация */}
          <div className="lg:col-span-2 space-y-6">
            {/* Заголовок */}
            <Card>
              <CardBody>
                <div className="space-y-4">
                  <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                      {job.title}
                    </h1>
                    <p className="text-xl text-primary-600 font-medium">
                      {job.company}
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-4 text-secondary-600">
                    <div className="flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {job.location}
                    </div>
                    
                    <div className="flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                      </svg>
                      {formatSalary(job.salaryMin, job.salaryMax)}
                    </div>

                    <div className="flex items-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 0h6m-6 0l-2 13a2 2 0 002 2h6a2 2 0 002-2L16 7" />
                      </svg>
                      Опубликовано {formatDate(job.postedDate)}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    <Badge variant="primary">
                      {categoryLabels[job.category] || job.category}
                    </Badge>
                    <Badge variant="secondary">
                      {employmentTypeLabels[job.employmentType] || job.employmentType}
                    </Badge>
                    <Badge variant="secondary">
                      {experienceLabels[job.experience] || job.experience}
                    </Badge>
                  </div>
                </div>
              </CardBody>
            </Card>

            {/* Описание */}
            <Card>
              <CardHeader>
                <h2 className="text-xl font-semibold">Описание вакансии</h2>
              </CardHeader>
              <CardBody>
                <div className="prose prose-secondary max-w-none">
                  <p className="whitespace-pre-line">{job.description}</p>
                </div>
              </CardBody>
            </Card>

            {/* Требования */}
            <Card>
              <CardHeader>
                <h2 className="text-xl font-semibold">Требования</h2>
              </CardHeader>
              <CardBody>
                <div className="prose prose-secondary max-w-none">
                  <p className="whitespace-pre-line">{job.requirements}</p>
                </div>
              </CardBody>
            </Card>

            {/* Условия */}
            <Card>
              <CardHeader>
                <h2 className="text-xl font-semibold">Условия работы</h2>
              </CardHeader>
              <CardBody>
                <div className="prose prose-secondary max-w-none">
                  <p className="whitespace-pre-line">{job.conditions}</p>
                </div>
              </CardBody>
            </Card>

            {/* О компании */}
            {job.companyDescription && (
              <Card>
                <CardHeader>
                  <h2 className="text-xl font-semibold">О компании</h2>
                </CardHeader>
                <CardBody>
                  <div className="prose prose-secondary max-w-none">
                    <p className="whitespace-pre-line">{job.companyDescription}</p>
                  </div>
                </CardBody>
              </Card>
            )}
          </div>

          {/* Боковая панель */}
          <div className="space-y-6">
            {/* Кнопка отклика */}
            <Card>
              <CardBody>
                <Button
                  className="w-full"
                  size="lg"
                  onClick={handleApply}
                  disabled={isApplied}
                  variant={isApplied ? 'secondary' : 'primary'}
                >
                  {isApplied ? 'Отклик отправлен' : 'Откликнуться'}
                </Button>
                
                {isApplied && (
                  <p className="text-sm text-success-600 mt-2 text-center">
                    ✓ Ваш отклик успешно отправлен
                  </p>
                )}
              </CardBody>
            </Card>

            {/* Контактная информация */}
            {job.contactEmail && (
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Контакты</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-2">
                    <div className="flex items-center text-secondary-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      <a 
                        href={`mailto:${job.contactEmail}`}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        {job.contactEmail}
                      </a>
                    </div>
                  </div>
                </CardBody>
              </Card>
            )}

            {/* Похожие вакансии */}
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold">Похожие вакансии</h3>
              </CardHeader>
              <CardBody>
                <div className="space-y-3">
                  <div className="p-3 border border-secondary-200 rounded-lg hover:bg-secondary-50 cursor-pointer transition-colors">
                    <h4 className="font-medium text-gray-900 text-sm">Frontend Developer</h4>
                    <p className="text-sm text-secondary-600">IT Solutions</p>
                    <p className="text-sm text-primary-600">400,000 - 600,000 ₸</p>
                  </div>
                  <div className="p-3 border border-secondary-200 rounded-lg hover:bg-secondary-50 cursor-pointer transition-colors">
                    <h4 className="font-medium text-gray-900 text-sm">React Developer</h4>
                    <p className="text-sm text-secondary-600">WebTech</p>
                    <p className="text-sm text-primary-600">450,000 - 700,000 ₸</p>
                  </div>
                </div>
              </CardBody>
            </Card>
          </div>
        </div>
      </div>

      {/* Модальное окно заявки */}
      <ApplicationModal
        isOpen={isApplicationModalOpen}
        onClose={() => setIsApplicationModalOpen(false)}
        job={job}
        onSubmit={handleApplicationSubmit}
      />

      {/* SmartBot Widget */}
      {showSmartBot && applicationId && (
        <SmartBotWidget
          applicationId={applicationId}
          isMinimized={isSmartBotMinimized}
          onToggleMinimize={() => setIsSmartBotMinimized(!isSmartBotMinimized)}
          onClose={() => setShowSmartBot(false)}
        />
      )}
    </div>
  );
};

export default JobDetails;