import React, { useState, useEffect, useRef } from 'react';
import { Bot, X, Minimize2, BarChart3, MessageCircle } from 'lucide-react';
import { smartBotAPI, type SmartBotMessage, type CandidateAnalysis } from '../services/api';

interface SmartBotWidgetProps {
  applicationId: number;
  onClose: () => void;
  isMinimized: boolean;
  onToggleMinimize: () => void;
}

const SmartBotWidget: React.FC<SmartBotWidgetProps> = ({ applicationId, onClose, isMinimized, onToggleMinimize }) => {
  const [messages, setMessages] = useState<SmartBotMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isCompleted, setIsCompleted] = useState(false);
  const [analysis, setAnalysis] = useState<CandidateAnalysis | null>(null);
  const [showAnalysis, setShowAnalysis] = useState(false);
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
    <div className="fixed bottom-4 right-4 w-96 h-[500px] bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5" />
          <span className="font-semibold">SmartBot</span>
          {isCompleted && (
            <span className="bg-green-500 text-xs px-2 py-1 rounded-full">Завершено</span>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {analysis && (
            <button
              onClick={() => setShowAnalysis(!showAnalysis)}
              className="text-white hover:text-gray-200 transition-colors"
              title="Показать анализ"
            >
              <BarChart3 className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onToggleMinimize}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages or Analysis */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {showAnalysis && analysis ? (
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
                <BarChart3 className="w-4 h-4 mr-2" />
                Анализ кандидата
              </h3>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-700">Общий балл:</span>
                  <div className="flex items-center mt-1">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${analysis.overall_score}%` }}
                      ></div>
                    </div>
                    <span className="ml-2 text-sm font-semibold text-blue-600">
                      {analysis.overall_score}/100
                    </span>
                  </div>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-700">Резюме:</span>
                  <p className="text-sm text-gray-600 mt-1">{analysis.summary}</p>
                </div>
                
                {analysis.strengths.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-green-700">Сильные стороны:</span>
                    <ul className="text-sm text-green-600 mt-1 list-disc list-inside">
                      {analysis.strengths.map((strength, index) => (
                        <li key={index}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {analysis.weaknesses.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-red-700">Области для улучшения:</span>
                    <ul className="text-sm text-red-600 mt-1 list-disc list-inside">
                      {analysis.weaknesses.map((weakness, index) => (
                        <li key={index}>{weakness}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {analysis.recommendations.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-blue-700">Рекомендации:</span>
                    <ul className="text-sm text-blue-600 mt-1 list-disc list-inside">
                      {analysis.recommendations.map((recommendation, index) => (
                        <li key={index}>{recommendation}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              
              <button
                onClick={() => setShowAnalysis(false)}
                className="mt-3 text-sm text-blue-600 hover:text-blue-800 flex items-center"
              >
                <MessageCircle className="w-4 h-4 mr-1" />
                Вернуться к чату
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'USER' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.role === 'USER'
                      ? 'bg-blue-500 text-white'
                      : message.role === 'ASSISTANT'
                      ? 'bg-gray-200 text-gray-800'
                      : 'bg-green-100 text-green-800 border border-green-300'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {new Date(message.created_at).toLocaleTimeString()}
                  </p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                    <span className="text-sm">SmartBot печатает...</span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      {!isCompleted && (
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Введите ваш ответ..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Отправить
            </button>
          </div>
        </div>
      )}

      {/* Completion Status */}
      {isCompleted && (
        <div className="p-4 border-t border-gray-200 bg-green-50">
          <div className="text-center">
            <p className="text-sm text-green-800 font-medium">
              ✅ Собеседование завершено!
            </p>
            <p className="text-xs text-green-600 mt-1">
              Работодатель получит анализ вашего профиля
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartBotWidget;
export { SmartBotWidget };