import React, { useState, useEffect } from 'react';
import { Card, CardBody, CardHeader, Button, Badge } from './ui';
import { smartBotAPI } from '../services/api';
import type { EmployerAnalysisView as EmployerAnalysisData } from '../services/api';

interface EmployerAnalysisViewProps {
  applicationId: number;
  onClose: () => void;
}

export const EmployerAnalysisView: React.FC<EmployerAnalysisViewProps> = ({
  applicationId,
  onClose,
}) => {
  const [analysis, setAnalysis] = useState<EmployerAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'summary' | 'chat' | 'details'>('summary');

  useEffect(() => {
    fetchAnalysis();
  }, [applicationId]);

  const fetchAnalysis = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await smartBotAPI.getEmployerApplicationAnalysis(applicationId);
      setAnalysis(response.data);
    } catch (err: any) {
      console.error('Error fetching analysis:', err);
      setError(err.response?.data?.detail || 'Ошибка при загрузке анализа');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score?: number) => {
    if (!score) return 'secondary';
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  const getRecommendationColor = (recommendation?: string) => {
    if (!recommendation) return 'secondary';
    if (recommendation === 'hire') return 'success';
    if (recommendation === 'consider') return 'warning';
    return 'danger';
  };

  const getRecommendationText = (recommendation?: string) => {
    switch (recommendation) {
      case 'hire': return 'Рекомендуется к найму';
      case 'consider': return 'Рассмотреть кандидатуру';
      case 'reject': return 'Не рекомендуется';
      default: return 'Не определено';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-4xl mx-4">
          <CardBody>
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <p className="text-secondary-600">Загрузка анализа кандидата...</p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-4xl mx-4">
          <CardHeader>
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Анализ кандидата</h2>
              <Button variant="outline" size="sm" onClick={onClose}>
                Закрыть
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Ошибка загрузки</h3>
              <p className="text-secondary-600 mb-4">{error}</p>
              <Button onClick={fetchAnalysis}>Попробовать снова</Button>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <Card className="w-full max-w-4xl mx-4">
          <CardHeader>
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">Анализ кандидата</h2>
              <Button variant="outline" size="sm" onClick={onClose}>
                Закрыть
              </Button>
            </div>
          </CardHeader>
          <CardBody>
            <div className="text-center py-8">
              <div className="w-12 h-12 bg-secondary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-secondary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Анализ не найден</h3>
              <p className="text-secondary-600">Для этого кандидата еще не проводился анализ SmartBot</p>
            </div>
          </CardBody>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-6xl max-h-[90vh] overflow-hidden">
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Анализ кандидата: {analysis.candidate_name}
              </h2>
              <p className="text-secondary-600 text-sm">
                {analysis.candidate_email} • Подал заявку: {formatDate(analysis.applied_at)}
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={onClose}>
              Закрыть
            </Button>
          </div>
        </CardHeader>

        <div className="border-b border-secondary-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('summary')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'summary'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
              }`}
            >
              Сводка
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
              }`}
            >
              История чата ({analysis.chat_messages.length})
            </button>
            <button
              onClick={() => setActiveTab('details')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'details'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300'
              }`}
            >
              Детали
            </button>
          </nav>
        </div>

        <CardBody className="overflow-y-auto max-h-[60vh]">
          {activeTab === 'summary' && (
            <div className="space-y-6">
              {/* Основные метрики */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card>
                  <CardBody>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900 mb-1">
                        {analysis.relevance_score ? `${analysis.relevance_score}%` : 'N/A'}
                      </div>
                      <div className="text-sm text-secondary-600">Соответствие</div>
                      <Badge variant={getScoreColor(analysis.relevance_score)} className="mt-2">
                        {analysis.relevance_score && analysis.relevance_score >= 80 ? 'Высокое' :
                         analysis.relevance_score && analysis.relevance_score >= 60 ? 'Среднее' : 'Низкое'}
                      </Badge>
                    </div>
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900 mb-1">
                        {getRecommendationText(analysis.recommendation)}
                      </div>
                      <div className="text-sm text-secondary-600">Рекомендация</div>
                      <Badge variant={getRecommendationColor(analysis.recommendation)} className="mt-2">
                        {analysis.recommendation || 'Не определено'}
                      </Badge>
                    </div>
                  </CardBody>
                </Card>

                <Card>
                  <CardBody>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900 mb-1">
                        {analysis.session_status === 'completed' ? 'Завершен' : 'В процессе'}
                      </div>
                      <div className="text-sm text-secondary-600">Статус анализа</div>
                      <Badge variant={analysis.session_status === 'completed' ? 'success' : 'warning'} className="mt-2">
                        {analysis.session_status}
                      </Badge>
                    </div>
                  </CardBody>
                </Card>
              </div>

              {/* Сводка */}
              {analysis.summary && (
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-semibold text-gray-900">Сводка анализа</h3>
                  </CardHeader>
                  <CardBody>
                    <p className="text-secondary-700 leading-relaxed">{analysis.summary}</p>
                  </CardBody>
                </Card>
              )}

              {/* Сильные стороны и проблемы */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {analysis.strengths.length > 0 && (
                  <Card>
                    <CardHeader>
                      <h3 className="text-lg font-semibold text-success-700">Сильные стороны</h3>
                    </CardHeader>
                    <CardBody>
                      <ul className="space-y-2">
                        {analysis.strengths.map((strength, index) => (
                          <li key={index} className="flex items-start">
                            <svg className="w-5 h-5 text-success-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="text-secondary-700">{strength}</span>
                          </li>
                        ))}
                      </ul>
                    </CardBody>
                  </Card>
                )}

                {analysis.concerns.length > 0 && (
                  <Card>
                    <CardHeader>
                      <h3 className="text-lg font-semibold text-warning-700">Проблемы</h3>
                    </CardHeader>
                    <CardBody>
                      <ul className="space-y-2">
                        {analysis.concerns.map((concern, index) => (
                          <li key={index} className="flex items-start">
                            <svg className="w-5 h-5 text-warning-500 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                            <span className="text-secondary-700">{concern}</span>
                          </li>
                        ))}
                      </ul>
                    </CardBody>
                  </Card>
                )}
              </div>
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="space-y-4">
              <div className="text-sm text-secondary-600 mb-4">
                История переписки кандидата с ИИ-ассистентом
              </div>
              
              {analysis.chat_messages.length === 0 ? (
                <Card>
                  <CardBody>
                    <div className="text-center py-8">
                      <svg className="w-12 h-12 text-secondary-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Нет сообщений</h3>
                      <p className="text-secondary-600">Переписка с кандидатом еще не началась</p>
                    </div>
                  </CardBody>
                </Card>
              ) : (
                <div className="space-y-3">
                  {analysis.chat_messages.map((message, index) => (
                    <div
                      key={message.id || index}
                      className={`flex ${message.role === 'USER' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          message.role === 'USER'
                            ? 'bg-primary-500 text-white'
                            : message.role === 'ASSISTANT'
                            ? 'bg-secondary-100 text-secondary-900'
                            : 'bg-warning-100 text-warning-900'
                        }`}
                      >
                        <div className="text-sm font-medium mb-1">
                          {message.role === 'USER' ? 'Кандидат' : 
                           message.role === 'ASSISTANT' ? 'ИИ-Ассистент' : 'Система'}
                        </div>
                        <div className="text-sm">{message.content}</div>
                        <div className="text-xs opacity-75 mt-1">
                          {formatDate(message.created_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Категории оценки */}
              {analysis.categories.length > 0 && (
                <Card>
                  <CardHeader>
                    <h3 className="text-lg font-semibold text-gray-900">Детальная оценка по категориям</h3>
                  </CardHeader>
                  <CardBody>
                    <div className="space-y-4">
                      {analysis.categories.map((category, index) => (
                        <div key={index} className="border-b border-secondary-200 pb-4 last:border-b-0">
                          <div className="flex justify-between items-center mb-2">
                            <h4 className="font-medium text-gray-900">{category.name}</h4>
                            <Badge variant={getScoreColor(category.score)}>
                              {category.score}%
                            </Badge>
                          </div>
                          <div className="w-full bg-secondary-200 rounded-full h-2 mb-2">
                            <div
                              className={`h-2 rounded-full ${
                                category.score >= 80 ? 'bg-success-500' :
                                category.score >= 60 ? 'bg-warning-500' : 'bg-danger-500'
                              }`}
                              style={{ width: `${category.score}%` }}
                            ></div>
                          </div>
                          <p className="text-sm text-secondary-600">{category.details}</p>
                        </div>
                      ))}
                    </div>
                  </CardBody>
                </Card>
              )}

              {/* Техническая информация */}
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold text-gray-900">Техническая информация</h3>
                </CardHeader>
                <CardBody>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="font-medium text-secondary-600">ID сессии:</span>
                      <div className="font-mono text-xs bg-secondary-100 p-2 rounded mt-1">
                        {analysis.session_id}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium text-secondary-600">ID заявки:</span>
                      <div className="font-mono text-xs bg-secondary-100 p-2 rounded mt-1">
                        {analysis.application_id}
                      </div>
                    </div>
                    <div>
                      <span className="font-medium text-secondary-600">Дата подачи заявки:</span>
                      <div className="text-secondary-700 mt-1">{formatDate(analysis.applied_at)}</div>
                    </div>
                    {analysis.analyzed_at && (
                      <div>
                        <span className="font-medium text-secondary-600">Дата анализа:</span>
                        <div className="text-secondary-700 mt-1">{formatDate(analysis.analyzed_at)}</div>
                      </div>
                    )}
                  </div>
                </CardBody>
              </Card>
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};

export default EmployerAnalysisView;