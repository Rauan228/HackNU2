import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Button, Badge, Card, CardBody, CardHeader } from '../components/ui';
import { jobsAPI, applicationsAPI } from '../services/api';
import { SmartBotWidget } from '../components/SmartBotWidget';

interface Job {
  id: string;
  title: string;
  location: string;
  salaryMin?: number;
  salaryMax?: number;
  employmentType: string;
  category: string;
  status: 'active' | 'paused' | 'closed';
  applicationsCount: number;
  viewsCount: number;
  postedDate: string;
  company_name?: string;
}

interface Application {
  id: string;
  jobId: string;
  jobTitle: string;
  candidateName: string;
  candidateEmail: string;
  resumeTitle: string;
  coverLetter: string;
  appliedDate: string;
  status: 'new' | 'viewed' | 'shortlisted' | 'rejected';
}

const statusLabels: Record<string, string> = {
  'active': 'Активна',
  'paused': 'Приостановлена',
  'closed': 'Закрыта',
};

const statusColors: Record<string, string> = {
  'active': 'success',
  'paused': 'warning',
  'closed': 'secondary',
};

const applicationStatusLabels: Record<string, string> = {
  'new': 'Новый',
  'viewed': 'Просмотрен',
  'shortlisted': 'В избранном',
  'rejected': 'Отклонен',
};

const applicationStatusColors: Record<string, string> = {
  'new': 'primary',
  'viewed': 'secondary',
  'shortlisted': 'success',
  'rejected': 'danger',
};

export const EmployerDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'jobs' | 'applications' | 'analytics'>('jobs');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState<string>('all');
  
  // SmartBot state
  const [showSmartBot, setShowSmartBot] = useState(false);
  const [isSmartBotMinimized, setIsSmartBotMinimized] = useState(false);
  const [selectedApplicationId, setSelectedApplicationId] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Получаем вакансии работодателя
        const jobsResponse = await jobsAPI.getMyJobs();
        
        // Преобразуем данные API в формат компонента
        const transformedJobs: Job[] = jobsResponse.data.map(job => ({
          id: job.id.toString(),
          title: job.title,
          location: job.location || 'Не указано',
          salaryMin: job.salary_min,
          salaryMax: job.salary_max,
          employmentType: job.employment_type || 'full-time',
          category: 'general', // Можно добавить категорию в API позже
          status: job.is_active ? 'active' : 'paused',
          applicationsCount: 0, // TODO: Получить количество заявок
          viewsCount: 0, // TODO: Получить количество просмотров
          postedDate: job.created_at.split('T')[0],
          company_name: job.company_name
        }));
        
        setJobs(transformedJobs);
        
        // Получаем заявки работодателя
        try {
          const applicationsResponse = await applicationsAPI.getApplications();
          
          // Преобразуем данные API в формат компонента
           const transformedApplications: Application[] = applicationsResponse.data.map(app => ({
             id: app.id.toString(),
             jobId: app.job_id.toString(),
             jobTitle: app.job_title || 'Не указано',
             candidateName: app.user_name || 'Не указано',
             candidateEmail: '', // Поле не возвращается API, можно добавить позже
             resumeTitle: app.resume_title || 'Не указано',
             coverLetter: app.cover_letter || '',
             appliedDate: app.created_at.split('T')[0],
             status: app.status === 'pending' ? 'new' : 
                    app.status === 'reviewed' ? 'viewed' :
                    app.status === 'accepted' ? 'shortlisted' : 'rejected'
           }));
          
          setApplications(transformedApplications);
        } catch (error) {
          console.error('Ошибка при загрузке заявок:', error);
          setApplications([]);
        }
        
      } catch (error) {
        console.error('Ошибка при загрузке данных:', error);
        // В случае ошибки показываем пустой список
        setJobs([]);
        setApplications([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Не указана';
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} ₸`;
    if (min) return `от ${min.toLocaleString()} ₸`;
    if (max) return `до ${max.toLocaleString()} ₸`;
    return 'Не указана';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
  };

  const filteredApplications = selectedJob === 'all' 
    ? applications 
    : applications.filter(app => app.jobId === selectedJob);

  const handleJobStatusChange = async (jobId: string, newStatus: string) => {
    try {
      // TODO: Отправить запрос на сервер
      // await fetch(`/api/jobs/${jobId}/status`, {
      //   method: 'PATCH',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ status: newStatus })
      // });

      setJobs(jobs.map(job => 
        job.id === jobId ? { ...job, status: newStatus as any } : job
      ));
    } catch (error) {
      console.error('Ошибка при изменении статуса:', error);
    }
  };

  const handleApplicationStatusChange = async (applicationId: string, newStatus: string) => {
    try {
      // TODO: Отправить запрос на сервер
      // await fetch(`/api/applications/${applicationId}/status`, {
      //   method: 'PATCH',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ status: newStatus })
      // });

      setApplications(applications.map(app => 
        app.id === applicationId ? { ...app, status: newStatus as any } : app
      ));
    } catch (error) {
      console.error('Ошибка при изменении статуса заявки:', error);
    }
  };

  const handleStartSmartBotAnalysis = (applicationId: string) => {
    setSelectedApplicationId(parseInt(applicationId));
    setShowSmartBot(true);
    setIsSmartBotMinimized(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-secondary-600">Загрузка панели управления...</p>
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
            Панель управления работодателя
          </h1>
          <p className="text-secondary-600">
            Управляйте вакансиями и просматривайте отклики кандидатов
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
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Активные вакансии</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {jobs.filter(job => job.status === 'active').length}
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
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Всего откликов</p>
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
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Просмотры</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {jobs.reduce((sum, job) => sum + job.viewsCount, 0)}
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
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Новые отклики</p>
                  <p className="text-2xl font-semibold text-gray-900">
                    {applications.filter(app => app.status === 'new').length}
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
                onClick={() => setActiveTab('jobs')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'jobs'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                Мои вакансии
              </button>
              <button
                onClick={() => setActiveTab('applications')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'applications'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                Отклики
                {applications.filter(app => app.status === 'new').length > 0 && (
                  <span className="ml-2 bg-danger-100 text-danger-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                    {applications.filter(app => app.status === 'new').length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'analytics'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
                }`}
              >
                Аналитика
              </button>
            </nav>
          </div>
        </div>

        {/* Контент табов */}
        {activeTab === 'jobs' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Мои вакансии</h2>
              <Link to="/create-job">
                <Button>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Создать вакансию
                </Button>
              </Link>
            </div>

            <div className="grid gap-6">
              {jobs.map((job) => (
                <Card key={job.id}>
                  <CardBody>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-4">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {job.title}
                            </h3>
                            <div className="flex items-center text-secondary-600 space-x-4">
                              <span>{job.location}</span>
                              <span>{formatSalary(job.salaryMin, job.salaryMax)}</span>
                              <span>Опубликовано {formatDate(job.postedDate)}</span>
                            </div>
                          </div>
                          <Badge variant={statusColors[job.status] as any}>
                            {statusLabels[job.status]}
                          </Badge>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-6 text-sm text-secondary-600">
                            <div className="flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                              </svg>
                              {job.applicationsCount} откликов
                            </div>
                            <div className="flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                              </svg>
                              {job.viewsCount} просмотров
                            </div>
                          </div>

                          <div className="flex items-center space-x-2">
                            <select
                              value={job.status}
                              onChange={(e) => handleJobStatusChange(job.id, e.target.value)}
                              className="text-sm border border-secondary-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            >
                              <option value="active">Активна</option>
                              <option value="paused">Приостановлена</option>
                              <option value="closed">Закрыта</option>
                            </select>
                            
                            <Button variant="outline" size="sm">
                              Редактировать
                            </Button>
                            
                            <Link to={`/jobs/${job.id}`}>
                              <Button variant="outline" size="sm">
                                Просмотр
                              </Button>
                            </Link>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'applications' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Отклики на вакансии</h2>
              <select
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                className="border border-secondary-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="all">Все вакансии</option>
                {jobs.map((job) => (
                  <option key={job.id} value={job.id}>
                    {job.title}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid gap-6">
              {filteredApplications.map((application) => (
                <Card key={application.id}>
                  <CardBody>
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">
                              {application.candidateName}
                            </h3>
                            <p className="text-primary-600 font-medium">
                              {application.jobTitle}
                            </p>
                            <p className="text-secondary-600 text-sm">
                              {application.candidateEmail}
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
                          <h4 className="font-medium text-gray-900 mb-1">Резюме:</h4>
                          <p className="text-secondary-700">{application.resumeTitle}</p>
                        </div>

                        <div className="mb-4">
                          <h4 className="font-medium text-gray-900 mb-1">Сопроводительное письмо:</h4>
                          <p className="text-secondary-700 line-clamp-3">
                            {application.coverLetter}
                          </p>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <select
                              value={application.status}
                              onChange={(e) => handleApplicationStatusChange(application.id, e.target.value)}
                              className="text-sm border border-secondary-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                            >
                              <option value="new">Новый</option>
                              <option value="viewed">Просмотрен</option>
                              <option value="shortlisted">В избранном</option>
                              <option value="rejected">Отклонен</option>
                            </select>
                          </div>

                          <div className="flex items-center space-x-2">
                            <Button 
                              variant="primary" 
                              size="sm"
                              onClick={() => handleStartSmartBotAnalysis(application.id)}
                            >
                              SmartBot Анализ
                            </Button>
                            <Button variant="outline" size="sm">
                              Скачать резюме
                            </Button>
                            <Button variant="outline" size="sm">
                              Связаться
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardBody>
                </Card>
              ))}

              {filteredApplications.length === 0 && (
                <Card>
                  <CardBody>
                    <div className="text-center py-8">
                      <svg className="w-12 h-12 text-secondary-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        Нет откликов
                      </h3>
                      <p className="text-secondary-600">
                        {selectedJob === 'all' 
                          ? 'У вас пока нет откликов на вакансии'
                          : 'На выбранную вакансию пока нет откликов'
                        }
                      </p>
                    </div>
                  </CardBody>
                </Card>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Аналитика</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Статистика по вакансиям</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-4">
                    {jobs.map((job) => (
                      <div key={job.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                        <div>
                          <h4 className="font-medium text-gray-900">{job.title}</h4>
                          <p className="text-sm text-secondary-600">{job.location}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">
                            {job.applicationsCount} откликов
                          </p>
                          <p className="text-sm text-secondary-600">
                            {job.viewsCount} просмотров
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Статистика откликов</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-primary-50 rounded-lg">
                      <span className="font-medium text-primary-900">Новые</span>
                      <span className="text-primary-600 font-semibold">
                        {applications.filter(app => app.status === 'new').length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                      <span className="font-medium text-secondary-900">Просмотренные</span>
                      <span className="text-secondary-600 font-semibold">
                        {applications.filter(app => app.status === 'viewed').length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-success-50 rounded-lg">
                      <span className="font-medium text-success-900">В избранном</span>
                      <span className="text-success-600 font-semibold">
                        {applications.filter(app => app.status === 'shortlisted').length}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-danger-50 rounded-lg">
                      <span className="font-medium text-danger-900">Отклоненные</span>
                      <span className="text-danger-600 font-semibold">
                        {applications.filter(app => app.status === 'rejected').length}
                      </span>
                    </div>
                  </div>
                </CardBody>
              </Card>
            </div>
          </div>
        )}
      </div>
      
      {/* SmartBot Widget */}
      {showSmartBot && selectedApplicationId && (
        <SmartBotWidget
          applicationId={selectedApplicationId!}
          isMinimized={isSmartBotMinimized}
          onToggleMinimize={() => setIsSmartBotMinimized(!isSmartBotMinimized)}
          onClose={() => {
            setShowSmartBot(false);
            setSelectedApplicationId(null);
            setIsSmartBotMinimized(false);
          }}
        />
      )}
    </div>
  );
};

export default EmployerDashboard;