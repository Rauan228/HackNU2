-- =========================================
-- Тестовые данные для Job Board + SmartBot
-- =========================================

-- Очистка таблиц (если нужно)
-- TRUNCATE TABLE ai_chat_messages, ai_chat_sessions, job_applications, resumes, jobs, users RESTART IDENTITY CASCADE;

-- =========================
-- ПОЛЬЗОВАТЕЛИ
-- =========================

-- 2 работодателя
INSERT INTO users (email, hashed_password, full_name, phone, user_type) VALUES
('employer1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Айгуль Нурланова', '+7 701 123 4567', 'employer'),
('employer2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Данияр Касымов', '+7 702 987 6543', 'employer');

-- 2 соискателя
INSERT INTO users (email, hashed_password, full_name, phone, user_type) VALUES
('jobseeker1@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Асель Токтарова', '+7 705 111 2233', 'job_seeker'),
('jobseeker2@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Ерлан Жумабеков', '+7 707 444 5566', 'job_seeker');

-- =========================
-- ВАКАНСИИ
-- =========================

-- 3 вакансии от работодателей
INSERT INTO jobs (employer_id, title, description, requirements, location, employment_type, experience_level, salary_min, salary_max, remote_work) VALUES
(1, 'Frontend разработчик React', 
 'Ищем опытного Frontend разработчика для работы над современными веб-приложениями. В команде вы будете заниматься разработкой пользовательских интерфейсов, оптимизацией производительности и внедрением новых технологий.',
 'Опыт работы с React 2+ года, знание TypeScript, HTML5, CSS3, опыт работы с REST API',
 'Алматы', 'full_time', 'middle', 350000.00, 500000.00, false),

(1, 'Python Backend разработчик', 
 'Требуется Python разработчик для создания и поддержки серверной части веб-приложений. Работа с базами данных, API, микросервисами.',
 'Python 3.8+, FastAPI/Django, PostgreSQL, Docker, опыт работы с облачными сервисами',
 'Нур-Султан', 'full_time', 'senior', 450000.00, 650000.00, true),

(2, 'UI/UX дизайнер', 
 'Ищем креативного UI/UX дизайнера для работы над мобильными и веб-приложениями. Создание wireframes, прототипов, дизайн-системы.',
 'Figma, Sketch, Adobe Creative Suite, опыт создания дизайн-систем, понимание принципов UX',
 'Шымкент', 'part_time', 'junior', 200000.00, 300000.00, true);

-- =========================
-- РЕЗЮМЕ
-- =========================

-- 2 резюме от соискателей
INSERT INTO resumes (user_id, title, summary, experience, education, skills, languages, desired_position, desired_salary, location) VALUES
(3, 'Frontend разработчик React/TypeScript',
 'Опытный frontend разработчик с 3+ годами коммерческого опыта. Специализируюсь на создании современных веб-приложений с использованием React, TypeScript и современных инструментов разработки.',
 'ТОО "DigitalKZ" (2021-2024) - Frontend разработчик. Разработка SPA приложений, интеграция с REST API, оптимизация производительности. ИП "WebStudio" (2020-2021) - Junior Frontend разработчик.',
 'КазНТУ им. К.И. Сатпаева, Информационные системы, Бакалавр (2016-2020)',
 'React, TypeScript, JavaScript, HTML5, CSS3, SASS, Redux, Next.js, Webpack, Git',
 'Казахский (родной), Русский (свободно), Английский (B2)',
 'Frontend разработчик', 400000.00, 'Алматы'),

(4, 'Fullstack разработчик Python/React',
 'Универсальный разработчик с опытом работы как с frontend, так и с backend технологиями. Имею опыт создания полноценных веб-приложений от проектирования до деплоя.',
 'ТОО "TechSolutions" (2022-2024) - Fullstack разработчик. Разработка веб-приложений на Python/Django + React. Фриланс (2020-2022) - различные проекты на Python и JavaScript.',
 'КБТУ, Компьютерные науки, Бакалавр (2017-2021)',
 'Python, Django, FastAPI, React, JavaScript, PostgreSQL, Docker, AWS, Git, Linux',
 'Казахский (родной), Русский (свободно), Английский (B2+)',
 'Fullstack разработчик', 500000.00, 'Нур-Султан');

-- =========================
-- ОТКЛИКИ
-- =========================

-- 2 отклика
INSERT INTO job_applications (user_id, job_id, resume_id, cover_letter, status) VALUES
(3, 1, 1, 
 'Здравствуйте! Меня заинтересовала ваша вакансия Frontend разработчика. У меня есть 3+ года опыта работы с React и TypeScript, что полностью соответствует вашим требованиям. Готова обсудить детали и показать портфолио.',
 'pending'),

(4, 2, 2,
 'Добрый день! Хочу откликнуться на позицию Python Backend разработчика. Имею опыт работы с FastAPI, PostgreSQL и Docker. Готов к удаленной работе и быстрому старту.',
 'in_review');

-- =========================
-- SMARTBOT СЕССИИ И СООБЩЕНИЯ
-- =========================

-- Создаем сессию SmartBot для первого отклика
INSERT INTO ai_chat_sessions (application_id, lang, started_at, is_completed, relevance_score, summary_text) VALUES
(1, 'ru', NOW() - INTERVAL '2 hours', true, 85.50, 
 'Кандидат демонстрирует высокую релевантность для позиции Frontend разработчика. Опыт работы с React соответствует требованиям, знание TypeScript - преимущество. Локация совпадает с офисом компании. Мотивация высокая, готовность к обучению новым технологиям.');

-- Сообщения диалога для первой сессии
INSERT INTO ai_chat_messages (session_id, role, content, created_at) VALUES
(1, 'system', 'Добро пожаловать в SmartBot! Я помогу оценить вашу релевантность для данной позиции. Отвечайте честно на мои вопросы.', NOW() - INTERVAL '2 hours'),
(1, 'assistant', 'Здравствуйте! Вижу, что вы откликнулись на позицию Frontend разработчика React. Расскажите, пожалуйста, какой у вас опыт работы с React? Сколько лет вы используете эту технологию в коммерческих проектах?', NOW() - INTERVAL '2 hours' + INTERVAL '1 minute'),
(1, 'candidate', 'Здравствуйте! У меня 3 года коммерческого опыта с React. Работал в двух компаниях, создавал SPA приложения, интегрировал с различными API, использовал современные подходы вроде хуков и контекста.', NOW() - INTERVAL '2 hours' + INTERVAL '3 minutes'),
(1, 'assistant', 'Отлично! А как обстоят дела с TypeScript? В требованиях указано знание этой технологии. Используете ли вы TypeScript в своих проектах?', NOW() - INTERVAL '2 hours' + INTERVAL '5 minutes'),
(1, 'candidate', 'Да, активно использую TypeScript уже 2 года. Понимаю систему типов, умею настраивать конфигурацию, использую для типизации компонентов, API ответов и состояния приложения. Это значительно улучшает качество кода.', NOW() - INTERVAL '2 hours' + INTERVAL '7 minutes'),
(1, 'assistant', 'Прекрасно! Последний вопрос касается локации. Вакансия предполагает работу в офисе в Алматы. Готовы ли вы к такому формату работы?', NOW() - INTERVAL '2 hours' + INTERVAL '9 minutes'),
(1, 'candidate', 'Да, я живу в Алматы и готова к работе в офисе. Считаю, что офисная работа способствует лучшему взаимодействию в команде и обмену опытом.', NOW() - INTERVAL '2 hours' + INTERVAL '11 minutes');