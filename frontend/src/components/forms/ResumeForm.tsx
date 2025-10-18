import React, { useState } from 'react';
import { Button, Input, Textarea, Select, Card, CardHeader, CardBody } from '../ui';

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
  // Личная информация
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  location: string;
  
  // Профессиональная информация
  desiredPosition: string;
  desiredSalary: string;
  summary: string;
  
  // Опыт работы
  experiences: Experience[];
  
  // Образование
  education: Education[];
  
  // Навыки
  skills: string[];
  languages: string[];
}

interface ResumeFormProps {
  onSubmit: (data: ResumeFormData) => void;
  loading?: boolean;
}

const salaryRanges = [
  { value: '100000-200000', label: '100,000 - 200,000 ₸' },
  { value: '200000-300000', label: '200,000 - 300,000 ₸' },
  { value: '300000-500000', label: '300,000 - 500,000 ₸' },
  { value: '500000-700000', label: '500,000 - 700,000 ₸' },
  { value: '700000+', label: 'Свыше 700,000 ₸' },
];

export const ResumeForm: React.FC<ResumeFormProps> = ({ onSubmit, loading = false }) => {
  const [formData, setFormData] = useState<ResumeFormData>({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    location: '',
    desiredPosition: '',
    desiredSalary: '',
    summary: '',
    experiences: [],
    education: [],
    skills: [],
    languages: [],
  });

  const [errors, setErrors] = useState<any>({});
  const [skillInput, setSkillInput] = useState('');
  const [languageInput, setLanguageInput] = useState('');

  const handleChange = (field: keyof ResumeFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev: any) => ({ ...prev, [field]: '' }));
    }
  };

  // Функции для работы с опытом работы
  const addExperience = () => {
    const newExperience: Experience = {
      id: Date.now().toString(),
      company: '',
      position: '',
      startDate: '',
      endDate: '',
      current: false,
      description: '',
    };
    setFormData(prev => ({
      ...prev,
      experiences: [...prev.experiences, newExperience],
    }));
  };

  const updateExperience = (id: string, field: keyof Experience, value: any) => {
    setFormData(prev => ({
      ...prev,
      experiences: prev.experiences.map(exp =>
        exp.id === id ? { ...exp, [field]: value } : exp
      ),
    }));
  };

  const removeExperience = (id: string) => {
    setFormData(prev => ({
      ...prev,
      experiences: prev.experiences.filter(exp => exp.id !== id),
    }));
  };

  // Функции для работы с образованием
  const addEducation = () => {
    const newEducation: Education = {
      id: Date.now().toString(),
      institution: '',
      degree: '',
      field: '',
      startDate: '',
      endDate: '',
      current: false,
    };
    setFormData(prev => ({
      ...prev,
      education: [...prev.education, newEducation],
    }));
  };

  const updateEducation = (id: string, field: keyof Education, value: any) => {
    setFormData(prev => ({
      ...prev,
      education: prev.education.map(edu =>
        edu.id === id ? { ...edu, [field]: value } : edu
      ),
    }));
  };

  const removeEducation = (id: string) => {
    setFormData(prev => ({
      ...prev,
      education: prev.education.filter(edu => edu.id !== id),
    }));
  };

  // Функции для работы с навыками
  const addSkill = () => {
    if (skillInput.trim() && !formData.skills.includes(skillInput.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, skillInput.trim()],
      }));
      setSkillInput('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill),
    }));
  };

  // Функции для работы с языками
  const addLanguage = () => {
    if (languageInput.trim() && !formData.languages.includes(languageInput.trim())) {
      setFormData(prev => ({
        ...prev,
        languages: [...prev.languages, languageInput.trim()],
      }));
      setLanguageInput('');
    }
  };

  const removeLanguage = (language: string) => {
    setFormData(prev => ({
      ...prev,
      languages: prev.languages.filter(l => l !== language),
    }));
  };

  const validateForm = (): boolean => {
    const newErrors: any = {};

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'Имя обязательно';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Фамилия обязательна';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email обязателен';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'Телефон обязателен';
    }

    if (!formData.desiredPosition.trim()) {
      newErrors.desiredPosition = 'Желаемая позиция обязательна';
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
    <div className="max-w-4xl mx-auto space-y-8">
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Личная информация */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-bold text-gray-900">Личная информация</h2>
          </CardHeader>
          <CardBody>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Input
                label="Имя *"
                value={formData.firstName}
                onChange={(e) => handleChange('firstName', e.target.value)}
                error={errors.firstName}
              />
              <Input
                label="Фамилия *"
                value={formData.lastName}
                onChange={(e) => handleChange('lastName', e.target.value)}
                error={errors.lastName}
              />
              <Input
                label="Email *"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                error={errors.email}
              />
              <Input
                label="Телефон *"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                error={errors.phone}
              />
              <div className="md:col-span-2">
                <Input
                  label="Местоположение"
                  placeholder="Город, страна"
                  value={formData.location}
                  onChange={(e) => handleChange('location', e.target.value)}
                />
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Профессиональная информация */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-bold text-gray-900">Профессиональная информация</h2>
          </CardHeader>
          <CardBody>
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Input
                  label="Желаемая позиция *"
                  placeholder="Например: Frontend разработчик"
                  value={formData.desiredPosition}
                  onChange={(e) => handleChange('desiredPosition', e.target.value)}
                  error={errors.desiredPosition}
                />
                <Select
                  label="Желаемая зарплата"
                  placeholder="Выберите диапазон"
                  options={salaryRanges}
                  value={formData.desiredSalary}
                  onChange={(e) => handleChange('desiredSalary', e.target.value)}
                />
              </div>
              <Textarea
                label="О себе"
                placeholder="Краткое описание ваших профессиональных качеств и целей..."
                value={formData.summary}
                onChange={(e) => handleChange('summary', e.target.value)}
                rows={4}
              />
            </div>
          </CardBody>
        </Card>

        {/* Опыт работы */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Опыт работы</h2>
              <Button type="button" variant="outline" size="sm" onClick={addExperience}>
                Добавить опыт
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            {formData.experiences.length === 0 ? (
              <p className="text-secondary-500 text-center py-8">
                Нажмите "Добавить опыт" чтобы добавить информацию о работе
              </p>
            ) : (
              <div className="space-y-6">
                {formData.experiences.map((exp, index) => (
                  <div key={exp.id} className="border border-secondary-200 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-medium text-gray-900">
                        Опыт работы #{index + 1}
                      </h3>
                      <Button
                        type="button"
                        variant="danger"
                        size="sm"
                        onClick={() => removeExperience(exp.id)}
                      >
                        Удалить
                      </Button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="Компания"
                        value={exp.company}
                        onChange={(e) => updateExperience(exp.id, 'company', e.target.value)}
                      />
                      <Input
                        label="Должность"
                        value={exp.position}
                        onChange={(e) => updateExperience(exp.id, 'position', e.target.value)}
                      />
                      <Input
                        label="Дата начала"
                        type="date"
                        value={exp.startDate}
                        onChange={(e) => updateExperience(exp.id, 'startDate', e.target.value)}
                      />
                      <div className="space-y-2">
                        <Input
                          label="Дата окончания"
                          type="date"
                          value={exp.endDate}
                          onChange={(e) => updateExperience(exp.id, 'endDate', e.target.value)}
                          disabled={exp.current}
                        />
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={exp.current}
                            onChange={(e) => updateExperience(exp.id, 'current', e.target.checked)}
                            className="mr-2"
                          />
                          <span className="text-sm text-secondary-700">Работаю в настоящее время</span>
                        </label>
                      </div>
                      <div className="md:col-span-2">
                        <Textarea
                          label="Описание обязанностей"
                          value={exp.description}
                          onChange={(e) => updateExperience(exp.id, 'description', e.target.value)}
                          rows={3}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Образование */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-900">Образование</h2>
              <Button type="button" variant="outline" size="sm" onClick={addEducation}>
                Добавить образование
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            {formData.education.length === 0 ? (
              <p className="text-secondary-500 text-center py-8">
                Нажмите "Добавить образование" чтобы добавить информацию об образовании
              </p>
            ) : (
              <div className="space-y-6">
                {formData.education.map((edu, index) => (
                  <div key={edu.id} className="border border-secondary-200 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-lg font-medium text-gray-900">
                        Образование #{index + 1}
                      </h3>
                      <Button
                        type="button"
                        variant="danger"
                        size="sm"
                        onClick={() => removeEducation(edu.id)}
                      >
                        Удалить
                      </Button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="Учебное заведение"
                        value={edu.institution}
                        onChange={(e) => updateEducation(edu.id, 'institution', e.target.value)}
                      />
                      <Input
                        label="Степень/Квалификация"
                        value={edu.degree}
                        onChange={(e) => updateEducation(edu.id, 'degree', e.target.value)}
                      />
                      <Input
                        label="Специальность"
                        value={edu.field}
                        onChange={(e) => updateEducation(edu.id, 'field', e.target.value)}
                      />
                      <Input
                        label="Год начала"
                        type="date"
                        value={edu.startDate}
                        onChange={(e) => updateEducation(edu.id, 'startDate', e.target.value)}
                      />
                      <div className="space-y-2">
                        <Input
                          label="Год окончания"
                          type="date"
                          value={edu.endDate}
                          onChange={(e) => updateEducation(edu.id, 'endDate', e.target.value)}
                          disabled={edu.current}
                        />
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={edu.current}
                            onChange={(e) => updateEducation(edu.id, 'current', e.target.checked)}
                            className="mr-2"
                          />
                          <span className="text-sm text-secondary-700">Учусь в настоящее время</span>
                        </label>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>

        {/* Навыки и языки */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-bold text-gray-900">Навыки и языки</h2>
          </CardHeader>
          <CardBody>
            <div className="space-y-6">
              {/* Навыки */}
              <div>
                <label className="form-label">Профессиональные навыки</label>
                <div className="flex gap-2 mb-3">
                  <Input
                    placeholder="Введите навык"
                    value={skillInput}
                    onChange={(e) => setSkillInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                  />
                  <Button type="button" variant="outline" onClick={addSkill}>
                    Добавить
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.skills.map((skill) => (
                    <span
                      key={skill}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 text-primary-800"
                    >
                      {skill}
                      <button
                        type="button"
                        onClick={() => removeSkill(skill)}
                        className="ml-2 text-primary-600 hover:text-primary-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              {/* Языки */}
              <div>
                <label className="form-label">Языки</label>
                <div className="flex gap-2 mb-3">
                  <Input
                    placeholder="Введите язык"
                    value={languageInput}
                    onChange={(e) => setLanguageInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addLanguage())}
                  />
                  <Button type="button" variant="outline" onClick={addLanguage}>
                    Добавить
                  </Button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {formData.languages.map((language) => (
                    <span
                      key={language}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-secondary-100 text-secondary-800"
                    >
                      {language}
                      <button
                        type="button"
                        onClick={() => removeLanguage(language)}
                        className="ml-2 text-secondary-600 hover:text-secondary-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </CardBody>
        </Card>

        {/* Кнопки */}
        <div className="flex flex-col sm:flex-row gap-4 pt-6">
          <Button
            type="submit"
            loading={loading}
            className="flex-1 sm:flex-none"
          >
            Сохранить резюме
          </Button>
          <Button
            type="button"
            variant="secondary"
            className="flex-1 sm:flex-none"
          >
            Предварительный просмотр
          </Button>
        </div>
      </form>
    </div>
  );
};