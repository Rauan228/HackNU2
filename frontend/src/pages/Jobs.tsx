import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsAPI } from '../services/api';
import { type Job } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Search, MapPin, Building, DollarSign, Plus } from 'lucide-react';

const Jobs: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const { isEmployer } = useAuth();

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

  const formatSalary = (min?: number, max?: number) => {
    if (!min && !max) return 'Зарплата не указана';
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} ₽`;
    if (min) return `от ${min.toLocaleString()} ₽`;
    if (max) return `до ${max.toLocaleString()} ₽`;
    return '';
  };

  return (
    <div className="space-y-6">
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
          <button
            type="submit"
            className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Найти вакансии
          </button>
        </form>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md">
          {error}
        </div>
      )}

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.map((job) => (
          <div key={job.id} className="bg-white p-6 rounded-lg shadow hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  <Link to={`/jobs/${job.id}`} className="hover:text-blue-600">
                    {job.title}
                  </Link>
                </h3>
                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                  <div className="flex items-center">
                    <Building className="h-4 w-4 mr-1" />
                    {job.company_name}
                  </div>
                  <div className="flex items-center">
                    <MapPin className="h-4 w-4 mr-1" />
                    {job.location}
                  </div>
                  <div className="flex items-center">
                    <DollarSign className="h-4 w-4 mr-1" />
                    {formatSalary(job.salary_min, job.salary_max)}
                  </div>
                </div>
                <p className="text-gray-700 mb-4 line-clamp-3">
                  {job.description}
                </p>
                <div className="text-sm text-gray-500">
                  Опубликовано: {new Date(job.created_at).toLocaleDateString('ru-RU')}
                </div>
              </div>
            </div>
          </div>
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
    </div>
  );
};

export default Jobs;