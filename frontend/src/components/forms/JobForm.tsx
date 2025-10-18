import React, { useState } from 'react';
import { Button, Input, Textarea, Select, Card, CardHeader, CardBody } from '../ui';

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

interface JobFormProps {
  onSubmit: (data: JobFormData) => void;
  loading?: boolean;
}

const categories = [
  { value: 'it', label: 'IT и разработка' },
  { value: 'marketing', label: 'Маркетинг и реклама' },
  { value: 'sales', label: 'Продажи' },
  { value: 'design', label: 'Дизайн' },
  { value: 'finance', label: 'Финансы и бухгалтерия' },
  { value: 'hr', label: 'HR и кадры' },
  { value: 'management', label: 'Менеджмент' },
  { value: 'education', label: 'Образование' },
  { value: 'healthcare', label: 'Медицина' },
  { value: 'other', label: 'Другое' },
];

const employmentTypes = [
  { value: 'full_time', label: 'Полная занятость' },
  { value: 'part_time', label: 'Частичная занятость' },
  { value: 'contract', label: 'Контракт' },
  { value: 'internship', label: 'Стажировка' },
];

const experienceLevels = [
  { value: 'junior', label: 'Без опыта / Junior' },
  { value: 'middle', label: 'Middle (1-5 лет)' },
  { value: 'senior', label: 'Senior (5+ лет)' },
];

export const JobForm: React.FC<JobFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState<JobFormData>({
    title: '',
    description: '',
    requirements: '',
    conditions: '',
    category: '',
    salaryMin: '',
    salaryMax: '',
    location: '',
    employmentType: '',
    experience: '',
  });

  const [errors, setErrors] = useState<Partial<JobFormData>>({});

  const handleChange = (field: keyof JobFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<JobFormData> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Название вакансии обязательно';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Описание вакансии обязательно';
    }

    if (!formData.requirements.trim()) {
      newErrors.requirements = 'Требования обязательны';
    }

    if (!formData.category) {
      newErrors.category = 'Выберите категорию';
    }

    if (!formData.employmentType) {
      newErrors.employmentType = 'Выберите тип занятости';
    }

    if (!formData.experience) {
      newErrors.experience = 'Выберите требуемый опыт';
    }

    if (!formData.location.trim()) {
      newErrors.location = 'Укажите местоположение';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  return (
    <Card className="max-w-4xl mx-auto">
      <CardHeader>
        <h2 className="text-2xl font-bold text-gray-900">Создание вакансии</h2>
        <p className="text-secondary-600 mt-1">
          Заполните информацию о вакансии для привлечения подходящих кандидатов
        </p>
      </CardHeader>
      
      <CardBody>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Основная информация */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-2">
              <Input
                label="Название вакансии *"
                placeholder="Например: Frontend разработчик"
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                error={errors.title}
              />
            </div>

            <Select
              label="Категория *"
              placeholder="Выберите категорию"
              options={categories}
              value={formData.category}
              onChange={(e) => handleChange('category', e.target.value)}
              error={errors.category}
            />

            <Input
              label="Местоположение *"
              placeholder="Например: Алматы, Казахстан"
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              error={errors.location}
            />

            <Select
              label="Тип занятости *"
              placeholder="Выберите тип занятости"
              options={employmentTypes}
              value={formData.employmentType}
              onChange={(e) => handleChange('employmentType', e.target.value)}
              error={errors.employmentType}
            />

            <Select
              label="Требуемый опыт *"
              placeholder="Выберите уровень опыта"
              options={experienceLevels}
              value={formData.experience}
              onChange={(e) => handleChange('experience', e.target.value)}
              error={errors.experience}
            />
          </div>

          {/* Зарплата */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Уровень зарплаты</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                label="Минимальная зарплата"
                type="number"
                placeholder="100000"
                value={formData.salaryMin}
                onChange={(e) => handleChange('salaryMin', e.target.value)}
                help="Укажите сумму в тенге"
              />
              <Input
                label="Максимальная зарплата"
                type="number"
                placeholder="200000"
                value={formData.salaryMax}
                onChange={(e) => handleChange('salaryMax', e.target.value)}
                help="Укажите сумму в тенге"
              />
            </div>
          </div>

          {/* Описание */}
          <div>
            <Textarea
              label="Описание вакансии *"
              placeholder="Опишите обязанности, задачи и особенности работы..."
              value={formData.description}
              onChange={(e) => handleChange('description', e.target.value)}
              error={errors.description}
              rows={6}
              help="Подробное описание поможет привлечь подходящих кандидатов"
            />
          </div>

          {/* Требования */}
          <div>
            <Textarea
              label="Требования к кандидату *"
              placeholder="Укажите необходимые навыки, образование, опыт работы..."
              value={formData.requirements}
              onChange={(e) => handleChange('requirements', e.target.value)}
              error={errors.requirements}
              rows={5}
              help="Четкие требования помогут кандидатам понять, подходят ли они для позиции"
            />
          </div>

          {/* Условия */}
          <div>
            <Textarea
              label="Условия работы"
              placeholder="Опишите условия работы, льготы, график работы..."
              value={formData.conditions}
              onChange={(e) => handleChange('conditions', e.target.value)}
              rows={4}
              help="Привлекательные условия помогут заинтересовать кандидатов"
            />
          </div>

          {/* Кнопки */}
          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-secondary-200">
            <Button
              type="submit"
              loading={loading}
              className="flex-1 sm:flex-none"
            >
              Опубликовать вакансию
            </Button>
            <Button
              type="button"
              variant="secondary"
              className="flex-1 sm:flex-none"
            >
              Сохранить как черновик
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  );
};