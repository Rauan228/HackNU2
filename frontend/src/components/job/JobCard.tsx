import React from 'react';
import { Button, Badge, Card, CardBody } from '../ui';
import { type Job } from '../../services/api';
interface JobCardProps {
  job: Job;
  onApply: (jobId: number) => void;
  onViewDetails: (jobId: number) => void;
  showApplyButton?: boolean;
  isApplied?: boolean;
}
const employmentTypeLabels: Record<string, string> = {
  'full_time': 'Полная занятость',
  'part_time': 'Частичная занятость',
  'contract': 'Контракт',
  'internship': 'Стажировка',
};
const experienceLabels: Record<string, string> = {
  'junior': 'Начальный уровень',
  'middle': 'Средний уровень',
  'senior': 'Старший уровень',
};
export const JobCard: React.FC<JobCardProps> = ({
  job,
  onApply,
  onViewDetails,
  showApplyButton = true,
  isApplied = false,
}) => {
  const formatSalary = (min?: number, max?: number, currency?: string) => {
    const currencySymbol = currency === 'USD' ? '$' : currency === 'EUR' ? '€' : '₸';
    if (!min && !max) return 'Зарплата не указана';
    if (min && max) return `${min.toLocaleString()} - ${max.toLocaleString()} ${currencySymbol}`;
    if (min) return `от ${min.toLocaleString()} ${currencySymbol}`;
    if (max) return `до ${max.toLocaleString()} ${currencySymbol}`;
    return 'Зарплата не указана';
  };
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    if (diffDays === 1) return 'Вчера';
    if (diffDays < 7) return `${diffDays} дней назад`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} недель назад`;
    return date.toLocaleDateString('ru-RU');
  };
  return (
    <Card className="hover:shadow-lg transition-shadow duration-200">
      <CardBody>
        <div className="space-y-4">
          {}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-1 line-clamp-2">
              {job.title}
            </h3>
            <p className="text-lg text-primary-600 font-medium">{job.company_name}</p>
          </div>
          {}
          <div className="space-y-2">
            {job.location && (
              <div className="flex items-center text-secondary-600">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span className="text-sm">{job.location}</span>
              </div>
            )}
            <div className="flex items-center text-secondary-600">
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
              <span className="text-sm font-medium text-primary-600">
                {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
              </span>
            </div>
          </div>
          {}
          <div>
            <p className="text-secondary-700 text-sm line-clamp-3">
              {job.description}
            </p>
          </div>
          {}
          <div className="flex flex-wrap gap-2">
            {job.employment_type && (
              <Badge variant="secondary">
                {employmentTypeLabels[job.employment_type] || job.employment_type}
              </Badge>
            )}
            {job.experience_level && (
              <Badge variant="warning">
                {experienceLabels[job.experience_level] || job.experience_level}
              </Badge>
            )}
          </div>
          {}
          <div className="text-xs text-secondary-500">
            Опубликовано: {formatDate(job.created_at)}
          </div>
          {}
          <div className="flex gap-3 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onViewDetails(job.id)}
              className="flex-1"
            >
              Подробнее
            </Button>
            {showApplyButton && (
              <Button
                size="sm"
                onClick={() => onApply(job.id)}
                disabled={isApplied}
                className="flex-1"
              >
                {isApplied ? 'Отклик отправлен' : 'Откликнуться'}
              </Button>
            )}
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
