import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Briefcase, Users, MessageCircle, TrendingUp } from 'lucide-react';

const Home: React.FC = () => {
  const { user, isEmployer, isJobSeeker } = useAuth();

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl md:text-6xl">
          Найдите идеальную работу с{' '}
          <span className="text-blue-600">SmartBot</span>
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Платформа для поиска работы с ИИ-помощником, который поможет найти идеальную вакансию 
          или подходящего кандидата
        </p>
        <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
          {!user ? (
            <div className="space-y-3 sm:space-y-0 sm:space-x-3 sm:flex">
              <Link
                to="/register"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
              >
                Начать поиск
              </Link>
              <Link
                to="/jobs"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
              >
                Посмотреть вакансии
              </Link>
            </div>
          ) : (
            <div className="space-y-3 sm:space-y-0 sm:space-x-3 sm:flex">
              <Link
                to="/jobs"
                className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 md:py-4 md:text-lg md:px-10"
              >
                {isJobSeeker ? 'Найти работу' : 'Посмотреть вакансии'}
              </Link>
              {isEmployer && (
                <Link
                  to="/jobs/create"
                  className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-gray-50 md:py-4 md:text-lg md:px-10"
                >
                  Создать вакансию
                </Link>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Features */}
      <div className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:text-center">
            <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">
              Возможности
            </h2>
            <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
              Все для успешного поиска работы
            </p>
          </div>

          <div className="mt-10">
            <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <Briefcase className="h-6 w-6" />
                </div>
                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                  Поиск вакансий
                </p>
                <p className="mt-2 ml-16 text-base text-gray-500">
                  Удобный поиск и фильтрация вакансий по различным критериям
                </p>
              </div>

              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <Users className="h-6 w-6" />
                </div>
                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                  Управление резюме
                </p>
                <p className="mt-2 ml-16 text-base text-gray-500">
                  Создавайте и редактируйте резюме, откликайтесь на вакансии
                </p>
              </div>

              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <MessageCircle className="h-6 w-6" />
                </div>
                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                  SmartBot помощник
                </p>
                <p className="mt-2 ml-16 text-base text-gray-500">
                  ИИ-помощник для консультаций по карьере и поиску работы
                </p>
              </div>

              <div className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white">
                  <TrendingUp className="h-6 w-6" />
                </div>
                <p className="ml-16 text-lg leading-6 font-medium text-gray-900">
                  Аналитика откликов
                </p>
                <p className="mt-2 ml-16 text-base text-gray-500">
                  Отслеживайте статус ваших откликов и получайте обратную связь
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-blue-600 rounded-lg">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Готовы начать?</span>
            <span className="block">Присоединяйтесь к нам сегодня.</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-blue-200">
            Тысячи компаний и соискателей уже используют нашу платформу
          </p>
          {!user && (
            <Link
              to="/register"
              className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-blue-600 bg-white hover:bg-blue-50 sm:w-auto"
            >
              Зарегистрироваться бесплатно
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;