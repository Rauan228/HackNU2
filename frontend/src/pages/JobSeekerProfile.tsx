import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button, Badge, Card, CardBody, CardHeader } from '../components/ui';
import { applicationsAPI, resumesAPI } from '../services/api';


interface Resume {
  id: string;
  title: string;
  position: string;
  experience: string;
  location: string;
  salary?: number;
  skills: string[];
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  company: string;
  appliedDate: string;
  status: 'pending' | 'viewed' | 'shortlisted' | 'rejected' | 'interview';
  coverLetter: string;
}

interface JobRecommendation {
  id: string;
  title: string;
  company: string;
  location: string;
  salaryMin?: number;
  salaryMax?: number;
  matchPercentage: number;
  postedDate: string;
}

const applicationStatusLabels: Record<string, string> = {
  'pending': 'На рассмотрении',
  'viewed': 'Просмотрено',
  'shortlisted': 'В избранном',
  'rejected': 'Отклонено',
  'interview': 'Приглашение на интервью',
};

const applicationStatusColors: Record<string, string> = {
  'pending': 'warning',
  'viewed': 'secondary',
  'shortlisted': 'success',
  'rejected': 'danger',
  'interview': 'primary',
};

export const JobSeekerProfile: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'resumes' | 'applications' | 'recommendations' | 'profile'>('resumes');
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Загружаем реальные данные откликов
        const applicationsResponse = await applicationsAPI.getApplications();
        
        // Преобразуем данные из API в формат компонента
        const transformedApplications: Application[] = applicationsResponse.data.map(app => ({
          id: app.id.toString(),
          jobId: app.job_id.toString(),
          jobTitle: app.job_title || 'Без названия',
          company: app.company_name || 'Неизвестная компания',
          appliedDate: new Date(app.created_at).toLocaleDateString('ru-RU'),
          status: app.status === 'pending' ? 'pending' : 
                  app.status === 'reviewed' ? 'viewed' :
                  app.status === 'accepted' ? 'shortlisted' :
                  app.status === 'rejected' ? 'rejected' : 'pending',
          coverLetter: app.cover_letter || '',
        }));
        
        // Загружаем реальные данные резюме
        const resumesResponse = await resumesAPI.getResumes();
        
        // Преобразуем данные из API в формат компонента
        const transformedResumes: Resume[] = resumesResponse.data.map(resume => ({
          id: resume.id.toString(),
          title: resume.title || 'Резюме',
          position: resume.desired_position || 'Не указано',
          experience: '3-5', // Можно извлечь из experience поля
          location: resume.location || 'Не указано',
          salary: resume.desired_salary ? Number(resume.desired_salary) : undefined,
          skills: resume.skills ? resume.skills.split(', ').filter(skill => skill.trim()) : [],
          createdAt: new Date(resume.created_at).toLocaleDateString('ru-RU'),
          updatedAt: new Date(resume.updated_at).toLocaleDateString('ru-RU'),
          isActive: resume.is_public || false,
        }));

        const mockRecommendations: JobRecommendation[] = [
          {
            id: '1',
            title: 'Senior React Developer',
            company: 'InnovateTech',
            location: 'Алматы',
            salaryMin: 550000,
            salaryMax: 750000,
            matchPercentage: 95,
            postedDate: '2024-01-17',
          },
          {
            id: '2',
            title: 'Frontend Team Lead',
            company: 'DigitalSoft',
            location: 'Нур-Султан',
            salaryMin: 700000,
            salaryMax: 900000,
            matchPercentage: 88,
            postedDate: '2024-01-16',
          },
          {
            id: '3',
            title: 'JavaScript Developer',
            company: 'CodeFactory',
            location: 'Алматы',
            salaryMin: 450000,
            salaryMax: 650000,
            matchPercentage: 82,
            postedDate: '2024-01-15',
          },
        ];

        setResumes(transformedResumes);
        setApplications(transformedApplications);
        setRecommendations(mockRecommendations);
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        // В случае ошибки устанавливаем пустые массивы
        setApplications([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
  };

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Не указана';
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} ₸`;
    if (min) return `от ${min.toLocaleString()} ₸`;
    if (max) return `до ${max.toLocaleString()} ₸`;
    return 'Не указана';
  };

  const handleResumeToggle = async (resumeId: string) => {
    try {
      // TODO: Отправить запрос на сервер
      // await fetch(`/api/resumes/${resumeId}/toggle`, { method: 'PATCH' });

      setResumes(resumes.map(resume => 
        resume.id === resumeId 
          ? { ...resume, isActive: !resume.isActive }
          : resume
      ));
    } catch (error) {
      console.error('Ошибка при изменении статуса резюме:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600">Загрузка профиля...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Заголовок */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Личный кабинет
          </h1>
          <p className="text-secondary-600">
            Управляйте резюме, отслеживайте отклики и находите подходящие вакансии
          </p>
        </div>

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardBody>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Резюме</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {resumes.length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Отклики</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {applications.length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Рекомендации</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {recommendations.length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>

          <Card>
            <CardBody>
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-5 5-5-5h5v-5a7.5 7.5 0 00-15 0v5h5l-5 5-5-5h5V7.5a7.5 7.5 0 0115 0V17z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Интервью</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {applications.filter(app => app.status === 'interview').length}
                  </p>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        {/* Навигация по табам */}
        <div className="mb-6">
          <div className="border-b border-secondary-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('resumes')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'resumes'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                Мои резюме
              </button>
              <button
                onClick={() => setActiveTab('applications')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'applications'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                История откликов
                {applications.filter(app => app.status === 'interview').length > 0 && (
                  <span className="ml-2 bg-primary-100 text-primary-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    {applications.filter(app => app.status === 'interview').length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'recommendations'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                Рекомендации
                {recommendations.length > 0 && (
                  <span className="ml-2 bg-success-100 text-success-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    {recommendations.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('profile')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'profile'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                Настройки профиля
              </button>
            </nav>
          </div>
        </div>

        {/* Контент табов */}
        {activeTab === 'resumes' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Мои резюме</h2>
              <Link to="/create-resume">
                <Button>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Создать резюме
                </Button>
              </Link>
            </div>

            <div className="grid gap-6">
              {resumes.map((resume) => (
                <Card key={resume.id}>
                  <CardBody>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {resume.title}
                            </h3>
                            <p className="text-primary-600 font-medium mb-2">
                              {resume.position}
                            </p>
                            <div className="flex items-center text-secondary-600 space-x-4 text-sm">
                              <span>{resume.location}</span>
                              <span>Опыт: {resume.experience} лет</span>
                              {resume.salary && (
                                <span>от {resume.salary.toLocaleString()} ₸</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge variant={resume.isActive ? 'success' : 'secondary'}>
                              {resume.isActive ? 'Активно' : 'Неактивно'}
                            </Badge>
                          </div>
                        </div>

                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-2">Навыки:</h4>
                          <div className="flex flex-wrap gap-2">
                            {resume.skills.map((skill, index) => (
                              <Badge key={index} variant="secondary">
                                {skill}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="text-sm text-secondary-600">
                            <span>Создано: {formatDate(resume.createdAt)}</span>
                            <span className="mx-2">•</span>
                            <span>Обновлено: {formatDate(resume.updatedAt)}</span>
                          </div>

                          <div className="flex items-center space-x-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleResumeToggle(resume.id)}
                            >
                              {resume.isActive ? 'Деактивировать' : 'Активировать'}
                            </Button>
                            <Button variant="outline" size="sm">
                              Редактировать
                            </Button>
                            <Button variant="outline" size="sm">
                              Скачать PDF
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}

              {resumes.length === 0 && (
                <Card>
                  <CardBody>
                    <div className="text-center py-8">
                      <svg className="w-12 h-12 text-secondary-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        У вас пока нет резюме
                      </h3>
                      <p className="text-secondary-600 mb-4">
                        Создайте свое первое резюме, чтобы начать поиск работы
                      </p>
                      <Link to="/create-resume">
                        <Button>Создать резюме</Button>
                      </Link>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>
        )}

        {activeTab === 'applications' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">История откликов</h2>

            <div className="grid gap-6">
              {applications.map((application) => (
                <Card key={application.id}>
                  <CardBody>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {application.jobTitle}
                            </h3>
                            <p className="text-primary-600 font-medium">
                              {application.company}
                            </p>
                          </div>
                          <div className="text-right">
                            <Badge variant={applicationStatusColors[application.status] as any}>
                              {applicationStatusLabels[application.status]}
                            </Badge>
                            <p className="text-sm text-secondary-500 mt-1">
                              {formatDate(application.appliedDate)}
                            </p>
                          </div>
                        </div>

                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-1">Сопроводительное письмо:</h4>
                          <p className="text-secondary-700 line-clamp-2">
                            {application.coverLetter}
                          </p>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-4">
                            {application.status === 'interview' && (
                              <div className="flex items-center text-primary-600">
                                <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Приглашение на интервью!
                              </div>
                            )}
                          </div>

                          <div className="flex items-center space-x-2">
                            <Link to={`/jobs/${application.jobId}`}>
                              <Button variant="outline" size="sm">
                                Посмотреть вакансию
                              </Button>
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}

              {applications.length === 0 && (
                <Card>
                  <CardBody>
                    <div className="text-center py-8">
                      <svg className="w-12 h-12 text-secondary-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        У вас пока нет откликов
                      </h3>
                      <p className="text-secondary-600 mb-4">
                        Начните поиск работы и откликайтесь на интересные вакансии
                      </p>
                      <Link to="/jobs">
                        <Button>Найти вакансии</Button>
                      </Link>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>
        )}

        {activeTab === 'recommendations' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Рекомендуемые вакансии</h2>

            <div className="grid gap-6">
              {recommendations.map((job) => (
                <Card key={job.id} className="hover:shadow-lg transition-shadow duration-200">
                  <CardBody>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {job.title}
                            </h3>
                            <p className="text-primary-600 font-medium">
                              {job.company}
                            </p>
                            <div className="flex items-center text-secondary-600 mt-1">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              {job.location}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="flex items-center mb-2">
                              <div className="w-16 bg-secondary-200 rounded-full h-2 mr-2">
                                <div 
                                  className="bg-success-600 h-2 rounded-full" 
                                  style={{ width: `${job.matchPercentage}%` }}
                                ></div>
                              </div>
                              <span className="text-sm font-medium text-success-600">
                                {job.matchPercentage}%
                              </span>
                            </div>
                            <p className="text-sm text-secondary-500">
                              {formatDate(job.postedDate)}
                            </p>
                          </div>
                        </div>

                        <div className="mb-4">
                          <p className="text-secondary-700">
                            {formatSalary(job.salaryMin, job.salaryMax)}
                          </p>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="text-sm text-success-600">
                            Совпадение: {job.matchPercentage}% - отличная вакансия для вас!
                          </div>

                          <div className="flex items-center space-x-2">
                            <Link to={`/jobs/${job.id}`}>
                              <Button variant="outline" size="sm">
                                Подробнее
                              </Button>
                            </Link>
                            <Button size="sm">
                              Откликнуться
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}

              {recommendations.length === 0 && (
                <Card>
                  <CardBody>
                    <div className="text-center py-8">
                      <svg className="w-12 h-12 text-secondary-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Нет рекомендаций
                      </h3>
                      <p className="text-secondary-600 mb-4">
                        Создайте резюме, чтобы получать персональные рекомендации вакансий
                      </p>
                      <Link to="/create-resume">
                        <Button>Создать резюме</Button>
                      </Link>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>
        )}

        {activeTab === 'profile' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Настройки профиля</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Личная информация</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Имя
                      </label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        defaultValue="Алексей Петров"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email
                      </label>
                      <input
                        type="email"
                        className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        defaultValue="alexey@example.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Телефон
                      </label>
                      <input
                        type="tel"
                        className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                        defaultValue="+7 (777) 123-45-67"
                      />
                    </div>
                    <Button>Сохранить изменения</Button>
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Уведомления</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Email уведомления</h4>
                        <p className="text-sm text-secondary-600">
                          Получать уведомления о новых вакансиях
                        </p>
                      </div>
                      <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Рекомендации</h4>
                        <p className="text-sm text-secondary-600">
                          Получать персональные рекомендации
                        </p>
                      </div>
                      <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">Статус заявок</h4>
                        <p className="text-sm text-secondary-600">
                          Уведомления об изменении статуса откликов
                        </p>
                      </div>
                      <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
                    </div>
                    <Button>Сохранить настройки</Button>
                  </div>
                </CardBody>
              </Card>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};