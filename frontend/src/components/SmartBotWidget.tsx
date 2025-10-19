import React, { useState, useEffect, useRef } from 'react';
import { Bot, X, Minimize2, BarChart3, MessageCircle, ChevronLeft, ChevronRight, FileText, User, Star, TrendingUp, AlertCircle, Download } from 'lucide-react';
import { smartBotAPI, applicationsAPI, type SmartBotMessage, type CandidateAnalysis, type Resume } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

interface SmartBotWidgetProps {
  applicationId: number;
  onClose: () => void;
  isMinimized: boolean;
  onToggleMinimize: () => void;
}

type TabType = 'analysis' | 'chat' | 'resume';

const SmartBotWidget: React.FC<SmartBotWidgetProps> = ({ applicationId, onClose, isMinimized, onToggleMinimize }) => {
  const { isJobSeeker, isEmployer } = useAuth();
  const [messages, setMessages] = useState<SmartBotMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [analysis, setAnalysis] = useState<CandidateAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState<TabType>(isJobSeeker ? 'chat' : 'analysis');
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [resume, setResume] = useState<Resume | null>(null);
  const [loadingResume, setLoadingResume] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (applicationId) {
      startAnalysis();
    }
  }, [applicationId]);

  // Fetch resume when tab changes to resume
  const fetchResume = async () => {
    if (!applicationId || resume) return;
    
    setLoadingResume(true);
    try {
      const response = await applicationsAPI.getApplicationResume(applicationId);
      setResume(response.data);
    } catch (error) {
      console.error('Ошибка при загрузке резюме:', error);
    } finally {
      setLoadingResume(false);
    }
  };

  const downloadResume = () => {
    if (!resume) return;
    
    // Создаем текстовое содержимое резюме
    const resumeContent = `
РЕЗЮМЕ: ${resume.title}

ОСНОВНАЯ ИНФОРМАЦИЯ:
Желаемая позиция: ${resume.desired_position || 'Не указано'}
Желаемая зарплата: ${resume.desired_salary ? `${resume.desired_salary.toLocaleString()} руб.` : 'Не указано'}
Местоположение: ${resume.location || 'Не указано'}

О СЕБЕ:
${resume.summary || 'Не указано'}

ОПЫТ РАБОТЫ:
${resume.experience || 'Не указан'}

ОБРАЗОВАНИЕ:
${resume.education || 'Не указано'}

НАВЫКИ:
${resume.skills || 'Не указаны'}

ЯЗЫКИ:
${resume.languages || 'Не указаны'}

ПОРТФОЛИО:
${resume.portfolio_url || 'Не указано'}

Дата создания: ${new Date(resume.created_at).toLocaleDateString('ru-RU')}
Последнее обновление: ${new Date(resume.updated_at).toLocaleDateString('ru-RU')}
    `.trim();

    // Создаем и скачиваем файл
    const blob = new Blob([resumeContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `resume_${resume.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (activeTab === 'resume') {
      fetchResume();
    }
  }, [activeTab, applicationId]);

  const startAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await smartBotAPI.startAnalysis({ application_id: applicationId });
      
      setSessionId(response.data.session_id);
      
      if (response.data.initial_message) {
        const initialMessage: SmartBotMessage = {
          id: Date.now().toString(),
          role: 'ASSISTANT' as const,
          content: response.data.initial_message,
          created_at: new Date().toISOString()
        };
        setMessages([initialMessage]);
      }
      
      if (response.data.is_completed) {
        setIsCompleted(true);
        // Имитируем полученный анализ для демонстрации
        setAnalysis({
          id: 1,
          application_id: applicationId,
          overall_score: 85,
          summary: "Кандидат демонстрирует сильные технические навыки в области frontend-разработки с хорошим пониманием современных технологий. Имеет релевантный опыт работы и показывает потенциал для роста в команде.",
          strengths: [
            "Отличное знание React и TypeScript",
            "Опыт работы с современными инструментами разработки",
            "Хорошие коммуникативные навыки",
            "Готовность к обучению новым технологиям"
          ],
          weaknesses: [
            "Ограниченный опыт работы с backend технологиями",
            "Недостаточный опыт работы в больших командах",
            "Нет опыта работы с облачными платформами"
          ],
          recommendations: [
            "Рекомендуется провести техническое интервью",
            "Обратить внимание на soft skills во время собеседования",
            "Рассмотреть возможность менторства по backend технологиям"
          ],
          created_at: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Error starting analysis:', error);
      setMessages([{
        id: Date.now().toString(),
        role: 'ASSISTANT' as const,
        content: 'Извините, произошла ошибка при запуске анализа. Попробуйте позже.',
        created_at: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId) return;

    const userMessage: SmartBotMessage = {
      id: Date.now().toString(),
      role: 'USER' as const,
      content: inputMessage.trim(),
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await smartBotAPI.sendMessage({
        session_id: sessionId,
        message: userMessage.content
      });
      
      const botMessage: SmartBotMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ASSISTANT' as const,
        content: response.data.message,
        created_at: new Date().toISOString()
      };

      setMessages(prev => [...prev, botMessage]);
      
      if (response.data.is_completed) {
        setIsCompleted(true);
        if (response.data.analysis) {
          setAnalysis(response.data.analysis);
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: SmartBotMessage = {
        id: (Date.now() + 1).toString(),
        role: 'ASSISTANT' as const,
        content: 'Извините, произошла ошибка. Попробуйте еще раз.',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderAnalysisTab = () => (
    <div className="space-y-6">
      {/* Общий балл */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-semibold text-gray-900 text-lg flex items-center">
            <TrendingUp className="w-5 h-5 mr-3 text-blue-600" />
            Общая оценка кандидата
          </h3>
          <div className="flex items-center space-x-2">
            <Star className="w-5 h-5 text-yellow-500 fill-current" />
            <span className="text-2xl font-bold text-blue-600">{analysis?.overall_score || 0}/100</span>
          </div>
        </div>
        
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Релевантность профиля</span>
            <span className="text-sm text-gray-600">{analysis?.overall_score || 0}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-3 rounded-full transition-all duration-500" 
              style={{ width: `${analysis?.overall_score || 0}%` }}
            ></div>
          </div>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Резюме анализа</h4>
          <p className="text-blue-800 text-sm leading-relaxed">
            {analysis?.summary || "Анализ кандидата в процессе..."}
          </p>
        </div>

        {/* Рекомендация */}
        {analysis?.recommendations && analysis.recommendations.length > 0 && (
          <div className={`mt-4 p-4 rounded-lg border ${
            analysis.overall_score >= 80 
              ? 'bg-green-50 border-green-200' 
              : analysis.overall_score <= 40
              ? 'bg-red-50 border-red-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-center">
              <div className={`w-3 h-3 rounded-full mr-3 ${
                analysis.overall_score >= 80 
                  ? 'bg-green-500' 
                  : analysis.overall_score <= 40
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`}></div>
              <span className={`font-medium ${
                analysis.overall_score >= 80 
                  ? 'text-green-800' 
                  : analysis.overall_score <= 40
                  ? 'text-red-800'
                  : 'text-yellow-800'
              }`}>
                {analysis.overall_score >= 80 
                  ? 'Рекомендуется к найму' 
                  : analysis.overall_score <= 40
                  ? 'Не рекомендуется'
                  : 'Требует дополнительного рассмотрения'}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* История беседы с кандидатом */}
      {messages.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-900 text-lg mb-4 flex items-center">
            <MessageCircle className="w-5 h-5 mr-3 text-purple-600" />
            История беседы с кандидатом
          </h3>
          <div className="max-h-96 overflow-y-auto space-y-3">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'USER' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'USER' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <div className="text-sm">{message.content}</div>
                  <div className={`text-xs mt-1 ${
                    message.role === 'USER' ? 'text-blue-200' : 'text-gray-500'
                  }`}>
                    {new Date(message.created_at).toLocaleTimeString('ru-RU', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Сильные стороны */}
      {analysis?.strengths && analysis.strengths.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-green-700 text-lg mb-4 flex items-center">
            <svg className="w-5 h-5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Сильные стороны
          </h3>
          <div className="grid gap-3">
            {analysis.strengths.map((strength, index) => (
              <div key={index} className="flex items-start bg-green-50 border border-green-200 rounded-lg p-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-green-800 text-sm">{strength}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Области для улучшения */}
      {analysis?.weaknesses && analysis.weaknesses.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-orange-700 text-lg mb-4 flex items-center">
            <AlertCircle className="w-5 h-5 mr-3" />
            Области для развития
          </h3>
          <div className="grid gap-3">
            {analysis.weaknesses.map((weakness, index) => (
              <div key={index} className="flex items-start bg-orange-50 border border-orange-200 rounded-lg p-3">
                <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span className="text-orange-800 text-sm">{weakness}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Статистика анализа */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <h3 className="font-semibold text-gray-900 text-lg mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-3 text-indigo-600" />
          Статистика анализа
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-indigo-600">{messages.length}</div>
            <div className="text-sm text-gray-600">Сообщений</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-indigo-600">
              {messages.filter(m => m.role === 'USER').length}
            </div>
            <div className="text-sm text-gray-600">Ответов кандидата</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-indigo-600">
              {analysis?.overall_score || 0}
            </div>
            <div className="text-sm text-gray-600">Общая оценка</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-indigo-600">
              {isCompleted ? 'Завершен' : 'В процессе'}
            </div>
            <div className="text-sm text-gray-600">Статус</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderChatTab = () => (
    <div className="space-y-4">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${message.role === 'USER' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[80%] px-4 py-3 rounded-2xl shadow-sm ${
              message.role === 'USER'
                ? 'bg-blue-500 text-white rounded-br-md'
                : message.role === 'ASSISTANT'
                ? 'bg-white text-gray-800 border border-gray-200 rounded-bl-md'
                : 'bg-green-50 text-green-800 border border-green-200'
            }`}
          >
            <p className="text-sm leading-relaxed">{message.content}</p>
            <p className="text-xs mt-2 opacity-70">
              {new Date(message.created_at).toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
        </div>
      ))}
      {isLoading && (
        <div className="flex justify-start">
          <div className="bg-white text-gray-800 px-4 py-3 rounded-2xl rounded-bl-md border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-3">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-sm text-gray-600">SmartBot печатает...</span>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );

  const renderResumeTab = () => {
    if (loadingResume) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Загрузка резюме...</span>
        </div>
      );
    }

    if (!resume) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">Резюме не найдено</p>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        {/* Основная информация */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <User className="w-6 h-6 text-blue-600 mr-3" />
              <h3 className="font-semibold text-gray-900 text-lg">Информация о кандидате</h3>
            </div>
            <button
              onClick={downloadResume}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              <Download className="w-4 h-4 mr-2" />
              Скачать резюме
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <span className="text-sm font-medium text-gray-700 block">Название резюме:</span>
              <span className="text-gray-900">{resume.title}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-700 block">Желаемая позиция:</span>
              <span className="text-gray-900">{resume.desired_position || 'Не указано'}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-700 block">Желаемая зарплата:</span>
              <span className="text-gray-900">
                {resume.desired_salary ? `${resume.desired_salary.toLocaleString()} руб.` : 'Не указано'}
              </span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-700 block">Местоположение:</span>
              <span className="text-gray-900">{resume.location || 'Не указано'}</span>
            </div>
          </div>
        </div>

        {/* Краткое описание */}
        {resume.summary && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">О себе</h3>
            <p className="text-gray-700 leading-relaxed">{resume.summary}</p>
          </div>
        )}

        {/* Опыт работы */}
        {resume.experience && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">Опыт работы</h3>
            <div className="text-gray-700 leading-relaxed whitespace-pre-line">{resume.experience}</div>
          </div>
        )}

        {/* Образование */}
        {resume.education && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">Образование</h3>
            <div className="text-gray-700 leading-relaxed whitespace-pre-line">{resume.education}</div>
          </div>
        )}

        {/* Навыки */}
        {resume.skills && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">Навыки</h3>
            <div className="flex flex-wrap gap-2">
              {resume.skills.split(',').map((skill: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full border border-blue-200"
                >
                  {skill.trim()}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Языки */}
        {resume.languages && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">Языки</h3>
            <div className="text-gray-700 leading-relaxed">{resume.languages}</div>
          </div>
        )}

        {/* Портфолио */}
        {resume.portfolio_url && (
          <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 text-lg mb-4">Портфолио</h3>
            <a
              href={resume.portfolio_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
            >
              <Download className="w-4 h-4 mr-2" />
              Открыть портфолио
            </a>
          </div>
        )}

        {/* Дополнительная информация */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="font-semibold text-gray-900 text-lg mb-4">Дополнительная информация</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Дата создания:</span>
              <span className="ml-2 text-gray-900">
                {new Date(resume.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Последнее обновление:</span>
              <span className="ml-2 text-gray-900">
                {new Date(resume.updated_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
            <div>
              <span className="text-gray-600">Публичное резюме:</span>
              <span className="ml-2 text-gray-900">
                {resume.is_public ? 'Да' : 'Нет'}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={onToggleMinimize}
          className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-colors"
        >
          <Bot className="w-6 h-6" />
        </button>
      </div>
    );
  }

  return (
    <>
      {/* Overlay for mobile/tablet */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-25 z-40 lg:hidden"
        onClick={onClose}
      />
      
      {/* Side Panel */}
      <div className={`fixed top-0 right-0 h-full bg-white shadow-2xl border-l border-gray-200 flex flex-col z-50 transition-all duration-300 ease-in-out ${
        isCollapsed ? 'w-12' : 'w-full lg:w-1/3'
      }`}>
        
        {/* Collapse/Expand Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute left-0 top-1/2 transform -translate-y-1/2 -translate-x-full bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-l-lg shadow-lg transition-colors z-10"
        >
          {isCollapsed ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>

        {isCollapsed ? (
          /* Collapsed State */
          <div className="flex flex-col items-center py-4 space-y-4">
            <Bot className="w-6 h-6 text-blue-600" />
            <div className="writing-vertical text-xs text-gray-600 transform rotate-90 whitespace-nowrap">
              SmartBot
            </div>
          </div>
        ) : (
          /* Expanded State */
          <>
            {/* Header */}
            <div className="bg-blue-600 text-white p-4 flex items-center justify-between border-b">
              <div className="flex items-center space-x-3">
                <Bot className="w-6 h-6" />
                <div>
                  <h2 className="font-semibold text-lg">SmartBot</h2>
                  <p className="text-blue-100 text-sm">Анализ кандидата #{applicationId}</p>
                </div>
                {isCompleted && (
                  <span className="bg-green-500 text-xs px-2 py-1 rounded-full ml-2">Завершено</span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={onToggleMinimize}
                  className="text-white hover:text-blue-200 transition-colors p-1 rounded"
                  title="Свернуть"
                >
                  <Minimize2 className="w-5 h-5" />
                </button>
                <button
                  onClick={onClose}
                  className="text-white hover:text-blue-200 transition-colors p-1 rounded"
                  title="Закрыть"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Tab Navigation */}
            <div className="bg-white border-b border-gray-200">
              <nav className="flex">
                {/* Показываем вкладку "Анализ" только работодателям */}
                {isEmployer && (
                  <button
                    onClick={() => setActiveTab('analysis')}
                    className={`flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'analysis'
                        ? 'border-blue-500 text-blue-600 bg-blue-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <BarChart3 className="w-4 h-4 inline mr-2" />
                    Анализ
                  </button>
                )}
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`${isJobSeeker ? 'w-full' : 'flex-1'} py-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === 'chat'
                      ? 'border-blue-500 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <MessageCircle className="w-4 h-4 inline mr-2" />
                  Чат
                  {messages.length > 0 && (
                    <span className="ml-1 bg-blue-100 text-blue-600 text-xs px-1.5 py-0.5 rounded-full">
                      {messages.length}
                    </span>
                  )}
                </button>
                {/* Показываем вкладку "Резюме" только работодателям */}
                {isEmployer && (
                  <button
                    onClick={() => setActiveTab('resume')}
                    className={`flex-1 py-3 px-4 text-sm font-medium border-b-2 transition-colors ${
                      activeTab === 'resume'
                        ? 'border-blue-500 text-blue-600 bg-blue-50'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <FileText className="w-4 h-4 inline mr-2" />
                    Резюме
                  </button>
                )}
              </nav>
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
              {activeTab === 'analysis' && isEmployer && renderAnalysisTab()}
              {activeTab === 'chat' && renderChatTab()}
              {activeTab === 'resume' && isEmployer && renderResumeTab()}
            </div>

            {/* Input Area - только для вкладки чата */}
            {activeTab === 'chat' && !isCompleted && (
              <div className="p-4 border-t border-gray-200 bg-white">
                <div className="flex space-x-3">
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                    placeholder="Введите ваш ответ..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    className="px-6 py-3 bg-blue-500 text-white rounded-xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
                  >
                    Отправить
                  </button>
                </div>
              </div>
            )}

            {/* Completion Status */}
            {activeTab === 'chat' && isCompleted && (
              <div className="p-4 border-t border-gray-200 bg-gradient-to-r from-green-50 to-emerald-50">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-3">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p className="text-green-800 font-semibold mb-1">
                    Собеседование завершено!
                  </p>
                  <p className="text-sm text-green-600">
                    Анализ кандидата доступен во вкладке "Анализ"
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
};

export default SmartBotWidget;
export { SmartBotWidget };