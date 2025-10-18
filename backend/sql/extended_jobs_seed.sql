-- =========================================
-- Расширенный сидер для тестовых вакансий
-- =========================================

-- Дополнительные работодатели (начинаем с ID 13, так как максимальный ID = 12)
INSERT INTO users (email, hashed_password, full_name, phone, user_type) VALUES
('tech_corp@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'ТехКорп ТОО', '+7 727 555 0001', 'employer'),
('design_studio@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Дизайн Студия Креатив', '+7 727 555 0002', 'employer'),
('marketing_agency@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Маркетинг Агентство Про', '+7 727 555 0003', 'employer'),
('startup_hub@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Стартап Хаб Алматы', '+7 727 555 0004', 'employer'),
('finance_group@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Финансовая Группа Капитал', '+7 727 555 0005', 'employer');

-- Расширенные вакансии (20+ позиций) - используем существующих работодателей (ID 10-12) и новых (ID 13-17)
INSERT INTO jobs (employer_id, title, description, requirements, location, employment_type, experience_level, salary_min, salary_max, remote_work) VALUES

-- IT вакансии
(13, 'Senior Full-Stack разработчик', 
 'Ведущая IT-компания ищет опытного Full-Stack разработчика для работы над крупными проектами. Вы будете участвовать в разработке современных веб-приложений, архитектурных решений и менторстве младших разработчиков.',
 'React, Node.js, TypeScript, PostgreSQL, Docker, AWS, опыт 4+ года, знание архитектурных паттернов',
 'Алматы', 'full_time', 'senior', 600000.00, 900000.00, true),

(13, 'DevOps Engineer', 
 'Требуется DevOps инженер для автоматизации процессов разработки и развертывания. Работа с облачными платформами, контейнеризацией и CI/CD пайплайнами.',
 'Docker, Kubernetes, AWS/GCP, Jenkins/GitLab CI, Terraform, Linux, опыт 3+ года',
 'Нур-Султан', 'full_time', 'middle', 500000.00, 750000.00, true),

(14, 'React Native разработчик', 
 'Мобильная разработка на React Native для iOS и Android. Создание кроссплатформенных приложений с современным UI/UX.',
 'React Native, JavaScript/TypeScript, Redux, REST API, опыт публикации в App Store/Google Play',
 'Алматы', 'full_time', 'middle', 400000.00, 600000.00, false),

(14, 'QA Automation Engineer', 
 'Автоматизация тестирования веб и мобильных приложений. Создание и поддержка автотестов, интеграция в CI/CD.',
 'Selenium, Cypress, Jest, Python/JavaScript, опыт автоматизации 2+ года',
 'Шымкент', 'full_time', 'middle', 350000.00, 500000.00, true),

(15, 'Data Scientist', 
 'Анализ данных, машинное обучение, создание предиктивных моделей для бизнес-задач.',
 'Python, pandas, scikit-learn, TensorFlow, SQL, статистика, опыт с ML 2+ года',
 'Алматы', 'full_time', 'middle', 450000.00, 650000.00, true),

(16, 'iOS разработчик', 
 'Разработка нативных iOS приложений на Swift. Работа с современными фреймворками и архитектурными паттернами.',
 'Swift, UIKit, SwiftUI, Core Data, REST API, опыт 2+ года, знание MVVM/MVP',
 'Нур-Султан', 'full_time', 'middle', 400000.00, 600000.00, false),

(17, 'Android разработчик', 
 'Создание Android приложений на Kotlin. Работа с Material Design, архитектурными компонентами.',
 'Kotlin, Android SDK, Jetpack Compose, Room, Retrofit, опыт 2+ года',
 'Алматы', 'full_time', 'middle', 380000.00, 580000.00, false),

-- Дизайн вакансии
(14, 'Senior UI/UX Designer', 
 'Ведущий дизайнер для создания пользовательских интерфейсов мобильных и веб-приложений. Работа с дизайн-системами и исследованиями пользователей.',
 'Figma, Sketch, Adobe Creative Suite, Principle, опыт UX исследований, дизайн-системы',
 'Алматы', 'full_time', 'senior', 350000.00, 550000.00, true),

(15, 'Graphic Designer', 
 'Графический дизайнер для создания маркетинговых материалов, брендинга и визуального контента.',
 'Adobe Photoshop, Illustrator, InDesign, брендинг, типографика, портфолио',
 'Шымкент', 'part_time', 'junior', 180000.00, 280000.00, true),

(16, 'Motion Designer', 
 'Создание анимированной графики, видео-контента и интерактивных элементов для цифровых продуктов.',
 'After Effects, Cinema 4D, Lottie, анимация, видеомонтаж, креативность',
 'Алматы', 'contract', 'middle', 300000.00, 450000.00, true),

-- Маркетинг и продажи
(14, 'Digital Marketing Manager', 
 'Управление цифровым маркетингом, SEO/SEM, социальные сети, аналитика и оптимизация конверсий.',
 'Google Ads, Facebook Ads, Google Analytics, SEO, контент-маркетинг, опыт 3+ года',
 'Алматы', 'full_time', 'middle', 300000.00, 450000.00, false),

(15, 'Content Manager', 
 'Создание и управление контентом для веб-сайтов, социальных сетей и маркетинговых кампаний.',
 'Копирайтинг, SMM, WordPress, базовые знания HTML/CSS, креативность',
 'Нур-Султан', 'full_time', 'junior', 200000.00, 320000.00, true),

(17, 'Sales Manager B2B', 
 'Продажи IT-решений корпоративным клиентам. Работа с крупными сделками и долгосрочными контрактами.',
 'Опыт B2B продаж 2+ года, знание IT-рынка, CRM системы, переговоры',
 'Алматы', 'full_time', 'middle', 350000.00, 500000.00, true),

-- Менеджмент и управление
(13, 'Project Manager IT', 
 'Управление IT-проектами, координация команд разработки, планирование и контроль выполнения задач.',
 'Agile/Scrum, Jira, управление проектами, опыт в IT 3+ года, сертификация PMP приветствуется',
 'Алматы', 'full_time', 'senior', 400000.00, 600000.00, false),

(14, 'Product Manager', 
 'Управление продуктом от идеи до запуска. Работа с аналитикой, пользовательскими историями и roadmap.',
 'Product management, аналитика, A/B тестирование, SQL, опыт с цифровыми продуктами',
 'Нур-Султан', 'full_time', 'middle', 450000.00, 650000.00, true),

-- Стажировки и джуниор позиции
(15, 'Junior Frontend Developer (Стажировка)', 
 'Стажировка для начинающих разработчиков. Изучение современных технологий под руководством опытных менторов.',
 'Базовые знания HTML, CSS, JavaScript, желание учиться, портфолио проектов',
 'Алматы', 'internship', 'junior', 120000.00, 200000.00, true),

(16, 'Trainee QA Engineer', 
 'Стажировка в области тестирования ПО. Обучение мануальному и автоматизированному тестированию.',
 'Базовые знания тестирования, внимательность, аналитическое мышление',
 'Шымкент', 'internship', 'junior', 100000.00, 180000.00, true),

-- Удаленная работа
(17, 'Remote Full Stack Developer', 
 'Удаленная разработка веб-приложений. Гибкий график, работа с международными проектами.',
 'React, Node.js, MongoDB, опыт удаленной работы, английский язык B2+',
 'Удаленно', 'remote', 'middle', 400000.00, 600000.00, true),

-- Специализированные позиции
(13, 'Blockchain Developer', 
 'Разработка децентрализованных приложений и смарт-контрактов на Ethereum и других блокчейн платформах.',
 'Solidity, Web3.js, Ethereum, DeFi протоколы, криптография, опыт 1+ год',
 'Алматы', 'full_time', 'middle', 500000.00, 800000.00, false),

(14, 'Cybersecurity Specialist', 
 'Обеспечение информационной безопасности, анализ уязвимостей, внедрение защитных мер.',
 'Информационная безопасность, пентестинг, SIEM системы, сертификации CISSP/CEH',
 'Нур-Султан', 'full_time', 'senior', 550000.00, 800000.00, true);

-- Дополнительные соискатели для тестирования (начинаем с ID 5, так как 3-4 уже существуют)
INSERT INTO users (email, hashed_password, full_name, phone, user_type) VALUES
('seeker3@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Алия Сарсенова', '+7 705 777 8899', 'job_seeker'),
('seeker4@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Максат Абдуллаев', '+7 707 666 5544', 'job_seeker'),
('seeker5@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Динара Жакупова', '+7 708 333 2211', 'job_seeker');

-- Дополнительные резюме (используем ID 5-7 для новых соискателей)
INSERT INTO resumes (user_id, title, summary, experience, education, skills, languages, desired_position, desired_salary, location) VALUES
(5, 'UI/UX Designer',
 'Креативный дизайнер с 2+ годами опыта создания пользовательских интерфейсов для мобильных и веб-приложений. Специализируюсь на UX исследованиях и создании дизайн-систем.',
 'ТОО "DesignStudio" (2022-2024) - UI/UX Designer. Создание дизайна мобильных приложений, проведение UX исследований. Фриланс (2021-2022) - дизайн лендингов и интернет-магазинов.',
 'КазГУ им. аль-Фараби, Дизайн, Бакалавр (2017-2021)',
 'Figma, Sketch, Adobe XD, Photoshop, Illustrator, Principle, InVision, пользовательские исследования',
 'Казахский (родной), Русский (свободно), Английский (B1)',
 'UI/UX Designer', 300000.00, 'Алматы'),

(6, 'DevOps Engineer',
 'Опытный DevOps инженер с экспертизой в облачных технологиях и автоматизации. 4+ года опыта работы с AWS, Docker, Kubernetes.',
 'ТОО "CloudTech" (2020-2024) - DevOps Engineer. Настройка CI/CD, управление инфраструктурой в AWS, контейнеризация приложений. ТОО "ITSolutions" (2019-2020) - System Administrator.',
 'КБТУ, Информационные системы, Магистр (2017-2019)',
 'AWS, Docker, Kubernetes, Terraform, Jenkins, GitLab CI, Linux, Python, Bash, Monitoring',
 'Казахский (родной), Русский (свободно), Английский (B2+)',
 'DevOps Engineer', 600000.00, 'Нур-Султан'),

(7, 'Data Scientist',
 'Специалист по анализу данных и машинному обучению. Опыт создания предиктивных моделей и работы с большими данными.',
 'ТОО "DataLab" (2021-2024) - Data Scientist. Создание ML моделей для прогнозирования, анализ клиентских данных. Стажировка в "Analytics Pro" (2020-2021).',
 'КазНУ им. аль-Фараби, Математика и статистика, Магистр (2018-2020)',
 'Python, pandas, scikit-learn, TensorFlow, SQL, Tableau, Jupyter, статистика, машинное обучение',
 'Казахский (родной), Русский (свободно), Английский (B2)',
 'Data Scientist', 500000.00, 'Алматы');

-- Дополнительные отклики для тестирования (используем правильные ID резюме)
INSERT INTO job_applications (user_id, job_id, resume_id, cover_letter, status) VALUES
(5, 8, 3, 
 'Здравствуйте! Меня очень заинтересовала позиция Senior UI/UX Designer. У меня есть 2+ года опыта в создании пользовательских интерфейсов и проведении UX исследований. Готова показать портфолио и обсудить детали.',
 'pending'),

(6, 4, 4,
 'Добрый день! Хочу откликнуться на вакансию DevOps Engineer. Имею 4+ года опыта работы с AWS, Docker и Kubernetes. Готов к удаленной работе и быстрому включению в проекты.',
 'in_review'),

(7, 5, 5,
 'Здравствуйте! Заинтересована в позиции Data Scientist. У меня есть опыт создания ML моделей и работы с большими данными. Готова обсудить конкретные задачи и показать примеры работ.',
 'pending');