# Приложение "calm&mind"
Приложение будет предназначено для поддержания ментального здоровья. 
Приложение будет содержать: медитации, дыхательные практики, аудио для хорошего сна, сеансы осознанности по конкретным практикам, которые могут помочь улучшить отношения с самим собой или отпустить тяжелый день. А также несколько практик для эффективного тайм-менеджмента.
Преимущества перед конкурентами - обширное количество техник + оно будет бесплатное.

# JOB STORY
### 1. Когда вокруг происходит хаос и на меня накатывает приступ необъяснимой тревоги, я хочу взять себя в руки и спокойно продолжать заниматься своими делами, чтобы жить счастливой жизнью.
Краткое описание: воспользоваться техникой дыхания
Участник: Не зарегистрированный пользователь
Предусловие: Скачал приложение - открыта страница с регистрацией
Постусловие: Пользователь воспользовался необходимым функционалом
1. Система выдала форму регистрации, состоящей из "почта, логин, имя".
2. Пользователь заполнил данную форму и нажал кнопку регистрации
3. Система проверяет корректность, наличие в базе. Если всё ок - отправляет ссылку на почту для активации аккаунта.
Иначе:
3.1. Если почта есть в базе - ошибка
3.2. Если почта есть, но аккаунт не активирован - продолжается текущий юзеркейс
4. Пользователь открывает почту и переходит по ссылке - далее система активирует аккаунт
5. Система открывает основной экран и пользователь переходит на экран с активностями. Далее выбирает "breathe focus". Далее открывается экран с дыхательными практиками, пользователь выбирает одну из них.

### 2. Когда на учёбе у меня много проектов и я не могу сконцентрироваться, я хочу эффективно выполнять задачи при меньших затратах времени, чтобы не попасть в список на отчисление.
Краткое описание: воспользоваться техникой помидора
Участник: Зарегистрированный пользователь, но не авторизован
Предусловие: Открыта страница с входом
Постусловие: Пользователь воспользовался необходимым функционалом
1. Система выдала форму входа, состоящей из "логин, пароль".
2.Пользователь заполнил данную форму и нажал кнопку входа.
3. Система проверяет корректность, наличие в базе. Если всё ок - вход в аккаунт.
3.1. Иначе: Неверный пароль/логин - ошибка - уведомление проверить правильность введены данных.
4. Система открывает основной экран
5. Пользователь переходит на экран с активностями. Далее выбирает "pomodoro".
6. Система открывает экран с техникой помидора.

### 3. Когда я просыпаюсь утром и занимаюсь медитацией, я хочу узнать совет себе на день и получить дополнительную мотивацию, чтобы знать, что мои усилия окупятся сторицей это будет своего рода терапевтическим моментом.
Краткое описание: получить предсказание (совет)
Участник: Авторизованный пользователь
Предусловие: Закрыто приложение
Постусловие: получил предсказание
1. Пользователь открыл приложение
2. Система открыла главный экран с советом, рекомендациями и окном заполнения текущего настроения. Система выдала предсказание - совет.

### 4. Когда у меня нет времени на поиск необходимых практик/мелодий для медитаций, которые могут мне понравится, я хочу получать их подборку, основанную на моих интересах и потребностях, чтобы облегчить процесс поддержания ментального спокойствия/здоровья за счет изначально релевантных и персонализированных предложений.
Краткое описание: получить подборку практик
Участник: Авторизованный пользователь.
Предусловие: Закрыто приложение
Постусловие: получил подборку
1. Пользователь открыл приложение
2. Система открыла главный экран с советом, рекомендациями и окном заполнения текущего настроения. Система выдала предсказание - совет.
3. Система выдала подборку на основе оценок пользователя другим практикам
Иначе: Если пользователь не оставлял рейтинг - сообщение с просьбой оценить понравившиеся практики, для получение персонализированной подборки.

# Концептуальная модель
Объект
Атрибут
Действие
Пользователь
 ▪ name
 ▪ login
 ▪ email
 ▪ dateReg
 ▪ userId
Зарегистрировать, авторизовать, показать статистику, показать совет
Статистика пользователя
 ▪ userId
 ▪ calm_mins
 ▪ ratings
Отобразить статистику, отобразить рейтинги, добавить минуты спокойствия
Категория продукта
 ▪ prodId

Продукт
 ▪ categoryType
 ▪ prodId
 ▪ prodName
 ▪ techniques

Техника продукта
 ▪ techId
 ▪ name
 ▪ description
 ▪ effect
 ▪ example
Начать упражнение техникой, оценить технику
Настроение пользователя
 ▪ userId
 ▪ date
 ▪ mood
Добавить настроение
Диаграммы С4
Context    
Container
Component

# Сценарии использования через SD

Кейс 1:

                  
--------------------------------------------


Кейс 2:

В идеале должно работать так, но у меня заглушка.
--------------------------------------------



Кейс 3:

--------------------------------------------



Кейс 4:

--------------------------------------------
Иерархия экранов + несколько эскизов экранов для лучшего восприятия того, как оно будет работать/выглядеть.

Таким образом:
1)Различные практики-активности ("breathe focus", "mnemonics" и тд) я буду самостоятельно добавлять в базу данных с помощью API. Там, где нет информации будет реализована заглушка - то есть если находятся данные - они выводятся, если нет, то выходит сообщение "Section is in progress".
2)Метод помидора будет возвращать эту технику, но таймер запускаться не будет, то есть будет реализована заглушка.
3)Совет на день будет реализован с помощью готового API.
4)Рекомендательная модель будет реализована на основе оценок активностей пользователя и оценок активностей других пользователей. Данные будут браться из реальной БД, чтобы они там появились я создам ≈50 пользователей и всем пользователям проставлю рейтинги - оценки на техники-активности (понимаю, что таким образом качество модели может быть не точное, но мне хотелось сделать всё с нуля, т.ч. и дата сет). В случае, если оценок пользователя будет недостаточно или их совсем не будет буду возвращать сообщение о необходимости оставить больше оценок, чтобы мы смогли создать подборку для пользователя.
5)Из п.4 следует, что также в сервисе будет возможность оценивать активности.
6)Настроение пользователь будет оценивать по шкале 1-5 с помощью эмодзи, где 1 -- очень плохо, а 5 -- очень хорошо.Это будет своего рода ментальный прием, благодаря которому некоторые пользователи будут заходить каждый день, чтобы отмечать свое настроение и видеть как оно меняется с неделями, месяцами, годами и тд.
7)С помощью отчета jinja будет выводится личная информация пользователя на 3 экране - "Profile".
8)Также будет идти подсчет времени в приложении - для отображения минут спокойствия. Это также ментальный прием.
Код
Код представлен в colab, также там лежит документ с полным кодом по API одним файлом под названием "app.py".
Так как в колабе не получается создавать и хранить файлы csv для демонстрации используются заготовки, а код который представлен в самом конце кода 2 экрана - создаёт и готовит таблицу для создания модели. 
Заготовки, которые я создала из своей БД лежат в colab - это два файла csv для рекомендательной модели под названиями "prod.csv" и  "recomendation.csv" на случай если слетит что-то в коде, также дублирую эти файлы тут.

prod.csv


recomendation.csv



Подтверждение работы API по юзкейсам
1 юзкейс -- регистрация -> основной экран(main) -> переходит на экран с практиками("activities") -> выбирает "breathe focus" -> открывает экран со всеми дыхательными практиками -> выбирает одну из них
1) регистрация
 

2) для того, чтобы показать работу api пропускаю main экран - в коде есть, далее в кейсах также будет.
3) все техники-активности на экране "activities"
 

4) все техники в "breathe focus"

5) выбор определенной техники из "breathe focus"

2 юзкейс -- вход -> основной
