import React, { useState } from 'react';
import { Button, Textarea, Select, Card, CardHeader, CardBody } from '../ui';
interface ApplicationFormData {
  resumeId: string;
  coverLetter: string;
}
interface Resume {
  id: string;
  title: string;
  lastUpdated: string;
}
interface ApplicationFormProps {
  jobId?: string;
  jobTitle: string;
  companyName?: string;
  resumes?: Resume[];
  onSubmit: (data: ApplicationFormData) => void;
  onCancel?: () => void;
  loading?: boolean;
  isSubmitting?: boolean;
}
export const ApplicationForm: React.FC<ApplicationFormProps> = ({
  jobTitle,
  companyName,
  resumes = [],
  onSubmit,
  onCancel,
  loading = false,
  isSubmitting = false,
}) => {
  const [formData, setFormData] = useState<ApplicationFormData>({
    resumeId: '',
    coverLetter: '',
  });
  const [errors, setErrors] = useState<Partial<ApplicationFormData>>({});
  const handleChange = (field: keyof ApplicationFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };
  const validateForm = (): boolean => {
    const newErrors: Partial<ApplicationFormData> = {};
    if (!formData.resumeId) {
      newErrors.resumeId = 'Выберите резюме для отправки';
    }
    if (!formData.coverLetter.trim()) {
      newErrors.coverLetter = 'Сопроводительное письмо обязательно';
    } else if (formData.coverLetter.trim().length < 50) {
      newErrors.coverLetter = 'Сопроводительное письмо должно содержать минимум 50 символов';
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
  const resumeOptions = resumes.map(resume => ({
    value: resume.id,
    label: `${resume.title} (обновлено ${new Date(resume.lastUpdated).toLocaleDateString('ru-RU')})`,
  }));
  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <h2 className="text-2xl font-bold text-gray-900">Отклик на вакансию</h2>
        <div className="mt-2 text-secondary-600">
          <p className="font-medium">{jobTitle}</p>
          <p className="text-sm">{companyName}</p>
        </div>
      </CardHeader>
      <CardBody>
        <form onSubmit={handleSubmit} className="space-y-6">
          {}
          <div>
            <Select
              label="Выберите резюме *"
              placeholder="Выберите резюме для отправки"
              options={resumeOptions}
              value={formData.resumeId}
              onChange={(e) => handleChange('resumeId', e.target.value)}
              error={errors.resumeId}
              help={resumes.length === 0 ? 'У вас нет созданных резюме. Создайте резюме перед подачей отклика.' : undefined}
            />
            {resumes.length === 0 && (
              <div className="mt-4 p-4 bg-warning-50 border border-warning-200 rounded-lg">
                <p className="text-warning-800 text-sm">
                  У вас пока нет резюме. 
                  <a href="/create-resume" className="font-medium underline ml-1">
                    Создайте резюме
                  </a>
                  , чтобы откликнуться на вакансию.
                </p>
              </div>
            )}
          </div>
          {}
          <div>
            <Textarea
              label="Сопроводительное письмо *"
              placeholder="Расскажите, почему вы подходите для этой позиции. Опишите ваш опыт и мотивацию..."
              value={formData.coverLetter}
              onChange={(e) => handleChange('coverLetter', e.target.value)}
              error={errors.coverLetter}
              rows={8}
              help="Персонализированное сопроводительное письмо увеличивает шансы на получение ответа от работодателя"
            />
            <div className="mt-2 text-sm text-secondary-500">
              Символов: {formData.coverLetter.length} / минимум 50
            </div>
          </div>
          {}
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <h4 className="font-medium text-primary-900 mb-2">💡 Советы для сопроводительного письма:</h4>
            <ul className="text-sm text-primary-800 space-y-1">
              <li>• Обратитесь к работодателю по имени, если оно указано</li>
              <li>• Упомяните конкретные требования из вакансии</li>
              <li>• Приведите примеры вашего релевантного опыта</li>
              <li>• Объясните, почему вас интересует именно эта компания</li>
              <li>• Будьте конкретны и избегайте общих фраз</li>
            </ul>
          </div>
          {}
          <div className="flex flex-col sm:flex-row gap-4 pt-6 border-t border-secondary-200">
            <Button
              type="submit"
              loading={loading || isSubmitting}
              disabled={resumes.length === 0}
              className="flex-1 sm:flex-none"
            >
              {(loading || isSubmitting) ? 'Отправка...' : 'Отправить отклик'}
            </Button>
            {onCancel && (
              <Button
                type="button"
                variant="secondary"
                onClick={onCancel}
                className="flex-1 sm:flex-none"
              >
                Отмена
              </Button>
            )}
          </div>
        </form>
      </CardBody>
    </Card>
  );
};
