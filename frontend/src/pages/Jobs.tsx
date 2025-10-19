import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { jobsAPI, applicationsAPI, resumesAPI } from '../services/api';
import { type Job } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { JobCard } from '../components/job/JobCard';
import { Search, MapPin, Plus } from 'lucide-react';
import SmartBotWidget from '../components/SmartBotWidget';
import { Loader } from '../components/ui';

const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [showSmartBot, setShowSmartBot] = useState(false);
  const [smartBotApplicationId, setSmartBotApplicationId] = useState<number | null>(null);
  const [isApplying, setIsApplying] = useState(false);
  
  const { isEmployer } = useAuth();
  const navigate = useNavigate();

  const fetchJobs = async (pageNum: number = 1, reset: boolean = false) => {
    try {
      setLoading(true);
      const response = await jobsAPI.getJobs({
        page: pageNum,
        limit: 10,
        search: searchTerm || undefined,
        location: locationFilter || undefined
      });
      
      if (reset) {
        setJobs(response.data.jobs);
      } else {
        setJobs(prev => [...prev, ...response.data.jobs]);
      }
      
      setHasMore(response.data.jobs.length === 10);
      setError('');
    } catch (err: any) {
      setError('Ошибка загрузки вакансий');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs(1, true);
    setPage(1);
  }, [searchTerm, locationFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchJobs(1, true);
    setPage(1);
  };

  const loadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchJobs(nextPage, false);
  };

  const handleApply = async (jobId: number) => {
    setIsApplying(true);
    try {
      // Получаем список резюме пользователя
      const resumesResponse = await resumesAPI.getResumes();
      
      if (!resumesResponse.data || resumesResponse.data.length === 0) {
        alert('У вас нет резюме. Пожалуйста, создайте резюме перед подачей заявки.');
        navigate('/create-resume');
        return;
      }
      
      // Используем первое доступное резюме
      const firstResume = resumesResponse.data[0];
      
      const applicationData = {
        job_id: jobId,
        resume_id: firstResume.id,
        cover_letter: "Заинтересован в данной позиции. Готов обсудить детали."
      };
      
      const response = await applicationsAPI.createApplication(applicationData);
      console.log('Отклик успешно отправлен на вакансию:', jobId);
      
      // Открываем SmartBot виджет с ID заявки
      if (response.data && response.data.id) {
        setSmartBotApplicationId(response.data.id);
        setShowSmartBot(true);
      }
      
      // Обновляем список вакансий чтобы показать что отклик отправлен
      fetchJobs(1, true);
    } catch (error) {
      console.error('Ошибка при отправке отклика:', error);
      console.error('Детали ошибки:', (error as any).response?.data);
      console.error('Статус ошибки:', (error as any).response?.status);
      alert(`Ошибка при отправке отклика: ${(error as any).response?.data?.detail || (error as any).message}`);
    } finally {
      setIsApplying(false);
    }
  };

  const handleViewDetails = (jobId: number) => {
    navigate(`/jobs/${jobId}`);
  };

  return (
    <div className="space-y-6">
      {/* Overlay loader while applying */}
      {isApplying && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-lg shadow p-6 flex items-center space-x-3">
            <span className="inline-block w-6 h-6 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin" />
            <div>
              <div className="text-gray-900 font-medium">Отклик отправляется...</div>
              <div className="text-sm text-gray-600">Открываем чат со SmartBot</div>
            </div>
          </div>
        </div>
      )}
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Вакансии</h1>
        {isEmployer && (
          <Link
            to="/jobs/create"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Создать вакансию
          </Link>
        )}
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-6 rounded-lg shadow">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-1">
                Поиск по названию или описанию
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  id="search"
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Например: разработчик, менеджер..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
                Местоположение
              </label>
              <div className="relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  id="location"
                  className="pl-10 w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Город или регион"
                  value={locationFilter}
                  onChange={(e) => setLocationFilter(e.target.value)}
                />
              </div>
            </div>
          </div>
          <div className="flex justify-end">
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Найти
            </button>
          </div>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* Jobs Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            onApply={handleApply}
            onViewDetails={handleViewDetails}
            showApplyButton={!isEmployer}
          />
        ))}
      </div>

      {/* Loading */}
      {loading && (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600">Загрузка вакансий...</p>
        </div>
      )}

      {/* Load More */}
      {!loading && hasMore && jobs.length > 0 && (
        <div className="text-center">
          <button
            onClick={loadMore}
            className="px-6 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
          >
            Загрузить еще
          </button>
        </div>
      )}

      {/* No Jobs */}
      {!loading && jobs.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Вакансии не найдены</p>
          <p className="text-gray-400 mt-2">Попробуйте изменить параметры поиска</p>
        </div>
      )}

      {/* SmartBot Widget */}
    {showSmartBot && smartBotApplicationId && (
      <SmartBotWidget
        applicationId={smartBotApplicationId}
        isMinimized={false}
        onToggleMinimize={() => setShowSmartBot(!showSmartBot)}
        onClose={() => {
          setShowSmartBot(false);
          setSmartBotApplicationId(null);
        }}
      />
    )}
    </div>
  );
};

export default Jobs;