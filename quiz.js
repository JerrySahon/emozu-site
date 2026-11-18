/* Emozu next-step quiz.
   Privacy boundary: answers stay in memory in this tab. No localStorage, cookies or analytics.
   The existing contact form receives only the adult's stated intent and, when applicable, the invite type, never quiz answers about a child. */
(function () {
  'use strict';

  var CAMPAIGN_URL = '';
  var root = document.documentElement;
  var shell = document.getElementById('quiz');
  if (!shell) return;

  var stage = document.getElementById('quizStage');
  var title = document.getElementById('quizTitle');
  var kicker = document.getElementById('quizKicker');
  var help = document.getElementById('quizHelp');
  var optionsBox = document.getElementById('quizOptions');
  var note = document.getElementById('quizNote');
  var back = document.getElementById('quizBack');
  var skip = document.getElementById('quizSkip');
  var next = document.getElementById('quizNext');
  var close = document.getElementById('quizClose');
  var progressText = document.getElementById('quizProgressText');
  var progressBar = document.getElementById('quizProgressBar');

  var query = new URLSearchParams(location.search);
  var lang = query.get('lang') === 'ru' ? 'ru' : 'en';
  var requestedRef = query.get('ref');
  var refType = requestedRef === 'friend' || requestedRef === 'investor' ? requestedRef : '';
  var PUBLIC_ROOT = 'https://emozu.kids/';
  var li = function () { return lang === 'ru' ? 1 : 0; };
  var tx = function (pair) { return Array.isArray(pair) ? pair[li()] : pair; };
  var answers = new Map();
  var trail = ['route'];
  var lastFocus = null;

  var common = {
    privateKicker: ['Private in this tab', 'Приватно в этой вкладке'],
    adultPurpose: [
      'This helps an adult choose a relevant next step: pilot interest, research, updates or future support. Answers are not saved or sent.',
      'Этот квиз помогает взрослому выбрать следующий шаг: интерес к пилоту, исследованию, новостям или будущей поддержке. Ответы не сохраняются и не отправляются.'
    ],
    back: ['Back', 'Назад'],
    skip: ['Skip', 'Пропустить'],
    cont: ['Continue', 'Продолжить'],
    question: ['Question', 'Вопрос'],
    about: ['of about', 'примерно из'],
    optional: ['Optional', 'Необязательно'],
    noSave: [
      '<strong>Nothing here is enrollment.</strong> Participation is voluntary, does not depend on donating, and a family can stop at any time.',
      '<strong>Это не запись в исследование.</strong> Участие добровольное, не зависит от пожертвований, и семья может прекратить его в любой момент.'
    ],
    friendArrival: [
      'A friend invited you to see Emozu. You choose what, if anything, happens next.',
      'Друг пригласил вас посмотреть Emozu. Только вы решаете, нужен ли вам следующий шаг.'
    ],
    investorArrival: [
      'Someone thought Emozu may fit your work or support. Choose the professional or support path if it is relevant.',
      'Кто-то решил, что Emozu может быть связан с вашей работой или поддержкой. Если это актуально, выберите профессиональный путь или поддержку.'
    ]
  };

  function o(value, en, ru, subEn, subRu, nextId) {
    return { value: value, label: [en, ru], sub: subEn ? [subEn, subRu] : null, next: nextId };
  }
  function q(id, en, ru, opts, cfg) {
    var item = cfg || {};
    item.id = id;
    item.title = [en, ru];
    item.options = opts || [];
    return item;
  }

  var Q = {};
  function add(item) { Q[item.id] = item; }

  add(q('route', 'Which path fits you today?', 'Какой путь вам сейчас ближе?', [
    o('family', 'I am a parent or family member', 'Я родитель или член семьи', 'Explore the six-family pilot, updates or co-design.', 'Узнать о пилоте на шесть семей, новостях или совместной разработке.'),
    o('professional', 'I work in research, care or technology', 'Я работаю в исследованиях, помощи или технологиях'),
    o('support', 'I may sponsor or support the research', 'Я могу поддержать или спонсировать исследование'),
    o('other', 'I am curious or want to share Emozu', 'Мне интересно или я хочу рассказать об Emozu')
  ], { kicker: common.privateKicker, help: common.adultPurpose, required: true, next: 'adult' }));

  add(q('adult', 'Are you 18 or older?', 'Вам уже исполнилось 18 лет?', [
    o('yes', 'Yes', 'Да'),
    o('no', 'No', 'Нет', 'You can still read the public Emozu site.', 'Вы всё равно можете читать открытый сайт Emozu.')
  ], { required: true, next: function () {
    if (answers.get('adult') === 'no') return 'underage';
    return { family: 'family_location', professional: 'pro_type', support: 'support_type', other: 'other_goal' }[answers.get('route')];
  } }));

  /* Family route: 27 unique questions, with a short path and an optional full profile. */
  add(q('family_location', 'Where does your family live?', 'Где живёт ваша семья?', [
    o('yerevan', 'Yerevan', 'Ереван'), o('armenia', 'Elsewhere in Armenia', 'Другой город Армении'),
    o('outside', 'Outside Armenia', 'За пределами Армении'), o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { next: 'family_goal' }));
  add(q('family_goal', 'What would be useful today?', 'Что вам было бы полезно сейчас?', [
    o('pilot', 'Be considered for the six-family pilot', 'Рассмотреть участие в пилоте на шесть семей'),
    o('design', 'Give practical feedback', 'Дать практическую обратную связь'),
    o('updates', 'Get project updates', 'Получать новости проекта'),
    o('support', 'Hear when fundraising opens', 'Узнать о старте сбора')
  ], { next: 'family_age' }));
  add(q('family_age', 'Which broad age range is relevant?', 'Какая общая возрастная группа актуальна?', [
    o('3-5', '3 to 5', '3–5'), o('6-8', '6 to 8', '6–8'), o('9-12', '9 to 12', '9–12'),
    o('13-17', '13 to 17', '13–17'), o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { next: 'family_context' }));
  add(q('family_context', 'Which broad context feels accurate?', 'Какой общий контекст подходит?', [
    o('autism', 'Autism is part of our family context', 'Аутизм является частью контекста семьи'),
    o('assessment', 'Assessment or support needs are being explored', 'Идёт оценка или подбор поддержки'),
    o('sensory', 'Sensory needs are the main concern', 'Главное — сенсорные потребности'),
    o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { help: ['No diagnosis, history or child name is needed.', 'Диагноз, история болезни и имя ребёнка не нужны.'], next: 'family_depth' }));
  add(q('family_depth', 'How much would you like to answer?', 'Насколько подробно вы хотите ответить?', [
    o('quick', 'Keep it short', 'Короткий путь', 'Go straight to your role and next step.', 'Сразу перейти к роли и следующему шагу.'),
    o('full', 'Explore the full family profile', 'Пройти полный семейный профиль', 'Optional practical questions about daily life and study fit.', 'Необязательные практические вопросы о быте и удобстве участия.')
  ], { next: function () { return answers.get('family_depth') === 'full' ? 'family_comm' : 'family_role'; } }));
  add(q('family_comm', 'How does communication usually work?', 'Как обычно происходит коммуникация?', [
    o('conversation', 'Conversation', 'Разговорная речь'), o('phrases', 'Short words or phrases', 'Короткие слова или фразы'),
    o('aac', 'AAC or communication device', 'AAC или устройство коммуникации'), o('gestures', 'Gestures, sounds or behaviour', 'Жесты, звуки или поведение'),
    o('varies', 'It varies', 'По-разному'), o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { next: 'family_sensory' }));
  add(q('family_sensory', 'Which situations can be difficult?', 'Какие ситуации могут быть сложными?', [
    o('noise', 'Noise', 'Шум'), o('crowds', 'Crowds', 'Людные места'), o('transition', 'Transitions', 'Смена занятий'),
    o('light', 'Bright light', 'Яркий свет'), o('touch', 'Touch or clothing', 'Прикосновения или одежда'),
    o('unknown', 'It is hard to tell', 'Пока трудно понять')
  ], { multi: true, help: ['Choose any. This stays in this tab.', 'Можно выбрать несколько. Ответ останется в этой вкладке.'], next: 'family_frequency' }));
  add(q('family_frequency', 'How often are difficult overload moments noticeable?', 'Как часто заметны сложные моменты перегрузки?', [
    o('rare', 'Less than monthly', 'Реже раза в месяц'), o('monthly', 'A few times a month', 'Несколько раз в месяц'),
    o('weekly', 'About weekly', 'Примерно раз в неделю'), o('often', 'Several times a week', 'Несколько раз в неделю'),
    o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { next: 'family_signs' }));
  add(q('family_signs', 'Can an adult usually notice early signs?', 'Обычно взрослый замечает ранние признаки?', [
    o('often', 'Often', 'Часто'), o('sometimes', 'Sometimes', 'Иногда'), o('sudden', 'It usually feels sudden', 'Обычно это кажется внезапным'), o('unsure', 'Not sure yet', 'Пока не уверен(а)')
  ], { next: 'family_tracking' }));
  add(q('family_tracking', 'Do you track patterns today?', 'Вы сейчас отслеживаете закономерности?', [
    o('none', 'No', 'Нет'), o('paper', 'Paper notes', 'Бумажные заметки'), o('phone', 'Notes or calendar on a phone', 'Заметки или календарь в телефоне'),
    o('wearable', 'A wearable or health app', 'Часы или приложение здоровья'), o('other', 'Another way', 'Другой способ')
  ], { next: 'family_wearable' }));
  add(q('family_wearable', 'How does wearing something on the wrist usually go?', 'Как обычно получается носить что-то на запястье?', [
    o('comfortable', 'Usually comfortable', 'Обычно комфортно'), o('short', 'Only for short periods', 'Только недолго'),
    o('no', 'Tried, but it was not tolerated', 'Пробовали, но это было некомфортно'), o('never', 'Never tried', 'Не пробовали')
  ], { next: 'family_watch' }));
  add(q('family_watch', 'Is there already a smartwatch in the family?', 'В семье уже есть умные часы?', [
    o('galaxy', 'Samsung Galaxy Watch', 'Samsung Galaxy Watch'), o('other', 'Another smartwatch', 'Другие умные часы'),
    o('no', 'No', 'Нет'), o('unsure', 'Not sure', 'Не уверен(а)')
  ], { next: 'family_android' }));
  add(q('family_android', 'Is an Android phone available for study use?', 'Для исследования доступен Android-телефон?', [
    o('yes', 'Yes', 'Да'), o('maybe', 'Maybe', 'Возможно'), o('no', 'No', 'Нет'), o('unsure', 'Not sure', 'Не уверен(а)')
  ], { help: ['The current Watch8 plan needs Android compatibility. A loaner phone is included in the draft budget where needed.', 'Текущий план с Watch8 требует совместимости с Android. При необходимости в черновой смете предусмотрен телефон во временное пользование.'], next: 'family_setting' }));
  add(q('family_setting', 'Where would wearing the watch be easiest to try?', 'Где проще всего попробовать носить часы?', [
    o('home', 'At home', 'Дома'), o('school', 'School or day program', 'В школе или дневной программе'),
    o('travel', 'During outings or travel', 'На прогулках или в поездках'), o('mixed', 'A mix', 'В разных местах')
  ], { next: 'family_duration' }));
  add(q('family_duration', 'What test period sounds realistic?', 'Какой срок пробы кажется реалистичным?', [
    o('3days', 'Three days', 'Три дня'), o('week', 'One week', 'Одна неделя'), o('2weeks', 'Two weeks', 'Две недели'), o('unsure', 'Not sure', 'Пока не знаю')
  ], { next: 'family_notes' }));
  add(q('family_notes', 'Could an adult add a short note after a difficult moment?', 'Сможет ли взрослый добавить короткую заметку после сложного момента?', [
    o('yes', 'Yes, usually', 'Да, обычно'), o('sometimes', 'Sometimes', 'Иногда'), o('no', 'Probably not', 'Скорее нет'), o('unsure', 'Not sure', 'Не уверен(а)')
  ], { help: ['The first stage is retrospective. It sends no live alerts.', 'Первый этап ретроспективный. Живых уведомлений не будет.'], next: 'family_time' }));
  add(q('family_time', 'How much setup time feels reasonable?', 'Сколько времени на настройку кажется приемлемым?', [
    o('10', 'About 10 minutes', 'Около 10 минут'), o('30', 'Up to 30 minutes', 'До 30 минут'), o('hour', 'Up to one hour with help', 'До часа с поддержкой'), o('unsure', 'Not sure', 'Пока не знаю')
  ], { next: 'family_charging' }));
  add(q('family_charging', 'What charging routine would be easiest?', 'Какой режим зарядки был бы удобнее?', [
    o('night', 'At night', 'Ночью'), o('day', 'A short daytime break', 'Короткий перерыв днём'),
    o('swap', 'Swap devices if provided', 'Менять устройства, если их дадут'), o('unsure', 'Not sure', 'Пока не знаю')
  ], { next: 'family_privacy' }));
  add(q('family_privacy', 'What privacy point matters most?', 'Что важнее всего в вопросе приватности?', [
    o('location', 'No location tracking', 'Не отслеживать геолокацию'), o('audio', 'No audio or video', 'Без аудио и видео'),
    o('control', 'Clear delete and stop controls', 'Понятное удаление данных и право остановиться'),
    o('access', 'Know exactly who can see data', 'Точно знать, кто видит данные'), o('all', 'All of these', 'Всё перечисленное')
  ], { next: 'family_data' }));
  add(q('family_data', 'Which data setup would feel acceptable to review?', 'Какой вариант данных вы готовы рассмотреть?', [
    o('signals', 'Watch signals only', 'Только сигналы часов'), o('labels', 'Brief adult notes only', 'Только короткие заметки взрослого'),
    o('both', 'Signals plus brief notes', 'Сигналы и короткие заметки'), o('unsure', 'I need more information first', 'Сначала нужна дополнительная информация')
  ], { next: 'family_comp' }));
  add(q('family_comp', 'Would compensation affect the decision?', 'Повлияет ли компенсация на решение?', [
    o('no', 'No', 'Нет'), o('helpful', 'It would help', 'Это помогло бы'), o('important', 'It is important', 'Это важно'), o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { next: 'family_stop' }));
  add(q('family_stop', 'Is the right to stop at any time clear?', 'Понятно ли право прекратить участие в любой момент?', [
    o('yes', 'Yes', 'Да'), o('question', 'I would want to discuss it first', 'Я хочу сначала это обсудить')
  ], { help: ['A family can stop without giving a reason. Participation is separate from money.', 'Семья может остановиться без объяснения причины. Участие не связано с деньгами.'], next: 'family_barrier' }));
  add(q('family_barrier', 'What could make participation impractical?', 'Что может сделать участие неудобным?', [
    o('wearing', 'Wearing the watch', 'Ношение часов'), o('charging', 'Charging', 'Зарядка'), o('notes', 'Writing notes', 'Заметки'),
    o('privacy', 'Privacy', 'Приватность'), o('time', 'Time', 'Время'), o('other', 'Something else', 'Другое')
  ], { next: 'family_feedback' }));
  add(q('family_feedback', 'How would you prefer to give feedback?', 'Как удобнее давать обратную связь?', [
    o('form', 'A short form', 'Короткая форма'), o('chat', 'Messages', 'Сообщения'), o('call', 'A short call', 'Короткий звонок'), o('mixed', 'A mix', 'Комбинация')
  ], { next: 'family_role' }));
  add(q('family_role', 'Which role feels right?', 'Какая роль вам подходит?', [
    o('participant', 'Consider my family for the pilot', 'Рассмотреть мою семью для пилота'),
    o('codesign', 'Invite me to give product feedback', 'Пригласить меня дать обратную связь'),
    o('updates', 'Updates only', 'Только новости'), o('support', 'Tell me when fundraising opens', 'Сообщить о старте сбора')
  ], { next: 'family_result' }));

  /* Professional route. */
  add(q('pro_type', 'Which role is closest?', 'Какая роль ближе?', [
    o('clinician', 'Clinician or psychiatrist', 'Клиницист или психиатр'), o('research', 'Research or ethics', 'Исследования или этика'),
    o('signal', 'ML, signal or data', 'ML, сигналы или данные'), o('hardware', 'Hardware or wearable technology', 'Аппаратная часть или носимые устройства'),
    o('community', 'Parent community or care organization', 'Родительское сообщество или организация помощи')
  ], { next: 'pro_focus' }));
  add(q('pro_focus', 'Where could your perspective help?', 'Где ваш опыт может быть полезен?', [
    o('protocol', 'Study protocol', 'Протокол исследования'), o('ethics', 'Consent, ethics or privacy', 'Согласие, этика или приватность'),
    o('signals', 'Signal access or analysis', 'Доступ к сигналам или анализ'), o('devices', 'Devices or compatibility', 'Устройства или совместимость'),
    o('family', 'Family experience and burden', 'Опыт семьи и нагрузка')
  ], { next: 'pro_stage' }));
  add(q('pro_stage', 'What level of involvement fits?', 'Какой уровень участия подходит?', [
    o('review', 'Review a short outline', 'Посмотреть короткий план'), o('call', 'A 20-minute call', '20-минутный звонок'),
    o('ongoing', 'Explore an ongoing role', 'Обсудить постоянную роль'), o('updates', 'Updates only', 'Только новости')
  ], { next: 'pro_location' }));
  add(q('pro_location', 'Where are you based?', 'Где вы находитесь?', [
    o('armenia', 'Armenia', 'Армения'), o('region', 'Nearby region', 'Соседний регион'), o('other', 'Elsewhere', 'Другая страна'), o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { next: 'pro_time' }));
  add(q('pro_time', 'When might a first conversation be realistic?', 'Когда реалистичен первый разговор?', [
    o('week', 'Within a week', 'В течение недели'), o('month', 'Within a month', 'В течение месяца'), o('later', 'Later', 'Позже'), o('updates', 'Updates first', 'Сначала новости')
  ], { next: 'pro_result' }));

  /* Support route, deliberately separate from participation. */
  add(q('support_type', 'How might you support the research?', 'Как вы могли бы поддержать исследование?', [
    o('individual', 'Individual contribution', 'Личный взнос'), o('sponsor', 'Company or foundation sponsorship', 'Спонсорство компании или фонда'),
    o('devices', 'Devices or logistics', 'Устройства или логистика'), o('share', 'Share the campaign', 'Рассказать о сборе')
  ], { next: 'support_goal' }));
  add(q('support_goal', 'What do you want next?', 'Какой следующий шаг вам нужен?', [
    o('waitlist', 'Tell me when fundraising opens', 'Сообщить о старте сбора'),
    o('sponsor', 'Discuss sponsorship now', 'Обсудить спонсорство сейчас'),
    o('donate', 'Review the future contribution plan', 'Посмотреть план будущих взносов'),
    o('updates', 'Project updates only', 'Только новости проекта')
  ], { next: function () { return answers.get('support_goal') === 'donate' || answers.get('support_goal') === 'sponsor' ? 'support_amount' : 'support_update'; } }));
  add(q('support_amount', 'Which range is useful for planning?', 'Какой диапазон полезен для планирования?', [
    o('10-49', '$10 to $49', '$10–49'), o('50-249', '$50 to $249', '$50–249'), o('250-999', '$250 to $999', '$250–999'),
    o('1000+', '$1,000 or more', '$1 000 и более'), o('private', 'Prefer not to say', 'Предпочитаю не отвечать')
  ], { help: ['This is not a pledge or payment.', 'Это не обещание и не платёж.'], next: 'support_update' }));
  add(q('support_update', 'What would you want to see before supporting?', 'Что вы хотите увидеть до поддержки?', [
    o('budget', 'Final itemized budget', 'Финальную подробную смету'), o('recipient', 'Named fund recipient and terms', 'Получателя средств и условия'),
    o('protocol', 'Protocol and consent approach', 'Протокол и подход к согласию'), o('report', 'How results will be reported', 'Как будут опубликованы результаты')
  ], { multi: true, next: 'support_result' }));

  /* General visitor route. */
  add(q('other_goal', 'What brought you here?', 'Что привело вас сюда?', [
    o('learn', 'Learn how Emozu works', 'Понять, как работает Emozu'), o('share', 'Share it with someone', 'Поделиться с кем-то'),
    o('updates', 'Get updates', 'Получать новости'), o('campaign', 'Hear when fundraising opens', 'Узнать о старте сбора')
  ], { next: 'other_result' }));

  function routeName() { return answers.get('route') || 'other'; }
  function maxSteps() {
    if (answers.get('adult') === 'no') return 3;
    if (routeName() === 'family') return answers.get('family_depth') === 'full' ? 29 : 10;
    if (routeName() === 'professional') return 9;
    if (routeName() === 'support') return 8;
    return 5;
  }
  function currentId() { return trail[trail.length - 1]; }
  function isResult(id) { return /_result$/.test(id) || id === 'underage' || id === 'handoff'; }

  function nextIdFor(item, value) {
    var chosen = item.options.filter(function (x) { return x.value === value; })[0];
    if (chosen && chosen.next) return chosen.next;
    return typeof item.next === 'function' ? item.next() : item.next;
  }
  function pruneAfterBack() {
    var keep = new Set(trail);
    Array.from(answers.keys()).forEach(function (id) { if (!keep.has(id)) answers.delete(id); });
  }
  function go(id) {
    if (!id) return;
    trail.push(id);
    render();
  }
  function advance() {
    var item = Q[currentId()];
    var value = answers.get(item.id);
    go(nextIdFor(item, value));
  }

  function setProgress() {
    var n = Math.min(trail.length, maxSteps());
    var max = maxSteps();
    progressText.textContent = tx(common.question) + ' ' + n + ' ' + tx(common.about) + ' ' + max;
    progressBar.style.width = Math.min(100, Math.max(6, n / max * 100)) + '%';
  }

  function addLanguageSwitch() {
    var box = document.createElement('div');
    box.className = 'quiz-lang';
    [['en', 'English'], ['ru', 'Русский']].forEach(function (pair) {
      var b = document.createElement('button');
      b.type = 'button';
      b.textContent = pair[1];
      b.className = lang === pair[0] ? 'on' : '';
      b.addEventListener('click', function () { lang = pair[0]; render(); });
      box.appendChild(b);
    });
    var invite = document.createElement('button');
    invite.type = 'button';
    invite.className = 'quiz-invite-entry';
    invite.textContent = lang === 'ru' ? 'Пригласить кого-то' : 'Invite someone';
    invite.addEventListener('click', function () { go('invite_choose'); });
    box.appendChild(invite);
    stage.appendChild(box);
  }

  function optionButton(item, opt) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'quiz-option';
    var selected = item.multi ? (answers.get(item.id) || []).indexOf(opt.value) > -1 : answers.get(item.id) === opt.value;
    if (selected) b.classList.add('selected');
    b.setAttribute('aria-pressed', selected ? 'true' : 'false');
    b.innerHTML = '<span>' + tx(opt.label) + '</span>' + (opt.sub ? '<small>' + tx(opt.sub) + '</small>' : '');
    b.addEventListener('click', function () {
      if (item.multi) {
        var values = (answers.get(item.id) || []).slice();
        var at = values.indexOf(opt.value);
        if (at > -1) values.splice(at, 1); else values.push(opt.value);
        answers.set(item.id, values);
        render();
      } else {
        answers.set(item.id, opt.value);
        if (item.id === 'handoff') {
          if (opt.value === 'yes') handoffToForm(); else finishPrivately();
          return;
        }
        window.setTimeout(advance, 110);
      }
    });
    return b;
  }

  function setBase(k, h, body) {
    stage.querySelectorAll('.quiz-lang').forEach(function (switcher) { switcher.remove(); });
    kicker.textContent = k;
    title.textContent = h;
    help.textContent = body || '';
    optionsBox.innerHTML = '';
    note.className = 'quiz-note';
    note.innerHTML = '';
    next.hidden = true;
    skip.hidden = true;
    back.hidden = trail.length <= 1;
    back.textContent = tx(common.back);
    skip.textContent = tx(common.skip);
    next.textContent = tx(common.cont);
  }

  function renderQuestion(item) {
    var body = tx(item.help || '');
    if (item.id === 'route' && refType) {
      body = tx(refType === 'friend' ? common.friendArrival : common.investorArrival) + ' ' + tx(common.adultPurpose);
    }
    setBase(tx(item.kicker || common.optional), tx(item.title), body);
    item.options.forEach(function (opt) { optionsBox.appendChild(optionButton(item, opt)); });
    skip.hidden = item.required === true;
    if (item.multi) {
      next.hidden = false;
      next.disabled = !(answers.get(item.id) || []).length;
      next.onclick = advance;
    }
    if (item.id.indexOf('family_') === 0) {
      note.className = 'quiz-note show';
      note.innerHTML = tx(common.noSave);
    }
    if (item.id === 'route') addLanguageSwitch();
  }

  function summaryButton(label, action, ghost) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'btn' + (ghost ? ' ghost' : '');
    b.textContent = label;
    b.addEventListener('click', action);
    return b;
  }

  function addInviteActions(box) {
    var invite = document.createElement('div');
    invite.className = 'quiz-invite-actions';
    var label = document.createElement('p');
    label.textContent = lang === 'ru' ? 'Необязательно: передать Emozu дальше' : 'Optional: pass Emozu on';
    invite.appendChild(label);
    invite.appendChild(summaryButton(lang === 'ru' ? 'Пригласить друга' : 'Invite a friend', function () { go('invite_friend'); }, true));
    invite.appendChild(summaryButton(lang === 'ru' ? 'Познакомить с инвестором' : 'Introduce to an investor', function () { go('invite_investor'); }, true));
    box.appendChild(invite);
  }

  function inviteUrl(type, local) {
    var base = local ? location.origin + '/' : PUBLIC_ROOT;
    var params = [];
    if (lang === 'ru') params.push('lang=ru');
    params.push('ref=' + type);
    return base + '?' + params.join('&') + '#quiz';
  }

  function inviteText(type) {
    if (type === 'friend') {
      return lang === 'ru'
        ? 'Мне кажется, тебе может быть интересен Emozu: исследовательский проект о том, можно ли раньше замечать перегрузку по сигналам мягкого браслета. Короткий квиз поможет выбрать подходящий следующий шаг.'
        : 'I thought you might want to see Emozu, a research project testing whether a soft wearable can help adults notice overload earlier. The short quiz helps you choose a relevant next step.';
    }
    return lang === 'ru'
      ? 'Можно познакомлю вас с Юрой из Emozu? Команда готовит домашний пилот с шестью семьями в Армении: хотят проверить, что видно по записи с часов до сенсорной перегрузки. Плановый бюджет — $20 000. Если тема вам близка, я вас познакомлю.'
      : 'May I introduce you to Yury at Emozu? His team is planning a home study with six families in Armenia to see what watch signals can tell caregivers about sensory overload. The proposed budget is $20,000. If that sounds relevant, I’d be happy to connect you.';
  }

  function isLocalPreview() {
    return location.hostname === '127.0.0.1' || location.hostname === 'localhost' || location.hostname === '[::1]';
  }

  function renderInvite(type) {
    var friend = type === 'friend';
    setBase(
      lang === 'ru' ? 'Добровольное приглашение' : 'Optional introduction',
      friend ? (lang === 'ru' ? 'Пригласить друга' : 'Invite a friend') : (lang === 'ru' ? 'Познакомить с инвестором' : 'Introduce to an investor'),
      friend
        ? (lang === 'ru' ? 'Короткое личное сообщение без данных из квиза.' : 'A short personal note with no quiz data attached.')
        : (lang === 'ru' ? 'Короткое тёплое интро без обещаний и данных из квиза.' : 'A short warm intro with no promises or quiz data attached.')
    );
    progressText.textContent = lang === 'ru' ? 'Необязательное приглашение' : 'Optional invitation';
    progressBar.style.width = '100%';
    skip.hidden = true;

    var publicUrl = inviteUrl(type, false);
    var payload = inviteText(type) + '\n' + publicUrl;
    var panel = document.createElement('div');
    panel.className = 'quiz-share';

    if (isLocalPreview()) {
      var preview = document.createElement('p');
      preview.className = 'quiz-preview-note';
      preview.innerHTML = lang === 'ru'
        ? '<strong>Локальная проверка.</strong> Публичная ссылка ниже станет доступна только после слияния этой ветки.'
        : '<strong>Local preview.</strong> The public link below becomes available only after this branch is merged.';
      panel.appendChild(preview);
    }

    var area = document.createElement('textarea');
    area.className = 'quiz-share-text';
    area.readOnly = true;
    area.rows = friend ? 5 : 7;
    area.value = payload;
    area.setAttribute('aria-label', lang === 'ru' ? 'Текст приглашения' : 'Invitation text');
    panel.appendChild(area);

    var actions = document.createElement('div');
    actions.className = 'quiz-share-buttons';
    var status = document.createElement('p');
    status.className = 'quiz-share-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');

    if (navigator.share) {
      actions.appendChild(summaryButton(
        isLocalPreview() ? (lang === 'ru' ? 'Поделиться будущей ссылкой' : 'Share planned public link') : (lang === 'ru' ? 'Поделиться' : 'Share invitation'),
        function () {
          navigator.share({ title: 'Emozu', text: inviteText(type), url: publicUrl }).catch(function () {});
        }
      ));
    }

    actions.appendChild(summaryButton(
      isLocalPreview() ? (lang === 'ru' ? 'Скопировать будущую ссылку' : 'Copy planned invitation') : (lang === 'ru' ? 'Скопировать' : 'Copy invitation'),
      function () {
        var fallback = function () {
          area.focus(); area.select();
          var copied = false;
          try { copied = document.execCommand('copy'); } catch (e) {}
          status.textContent = copied
            ? (lang === 'ru' ? 'Скопировано.' : 'Copied.')
            : (lang === 'ru' ? 'Текст выделен. Скопируйте его вручную.' : 'Text selected. Copy it manually.');
        };
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(payload).then(function () {
            status.textContent = lang === 'ru' ? 'Скопировано.' : 'Copied.';
          }).catch(fallback);
        } else fallback();
      },
      true
    ));
    panel.appendChild(actions);

    if (isLocalPreview()) {
      var test = document.createElement('a');
      test.className = 'quiz-test-link';
      test.href = inviteUrl(type, true);
      test.target = '_blank';
      test.rel = 'noopener';
      test.textContent = lang === 'ru' ? 'Проверить приглашение на этом Mac' : 'Test this invite on this Mac';
      panel.appendChild(test);
    }

    var fallbackText = document.createElement('p');
    fallbackText.className = 'quiz-share-help';
    fallbackText.textContent = lang === 'ru' ? 'Если системное меню недоступно, выделите текст выше и скопируйте вручную.' : 'If the system share menu is unavailable, select the text above and copy it manually.';
    panel.appendChild(fallbackText);
    panel.appendChild(status);
    optionsBox.appendChild(panel);
  }

  function renderInviteChoice() {
    setBase(
      lang === 'ru' ? 'Добровольное приглашение' : 'Optional introduction',
      lang === 'ru' ? 'Кого вы хотите пригласить?' : 'Who would you like to invite?',
      lang === 'ru' ? 'Приглашение не содержит ответы квиза, контакты или личные данные.' : 'The invitation contains no quiz answers, contacts or personal data.'
    );
    progressText.textContent = lang === 'ru' ? 'Необязательное приглашение' : 'Optional invitation';
    progressBar.style.width = '100%';
    skip.hidden = true;
    optionsBox.appendChild(summaryButton(lang === 'ru' ? 'Друга или знакомого' : 'A friend or someone I know', function () { go('invite_friend'); }));
    optionsBox.appendChild(summaryButton(lang === 'ru' ? 'Инвестора или партнёра' : 'An investor or partner', function () { go('invite_investor'); }, true));
  }

  function renderResult(id) {
    var copy = {
      family_result: {
        k: ['Your next step', 'Ваш следующий шаг'],
        h: ['Choose what happens next.', 'Выберите, что делать дальше.'],
        p: ['Your family answers remain only in this tab. If you continue, the public contact form will receive only your contact, a short statement of intent and, if applicable, the invitation type.', 'Ответы о семье останутся только в этой вкладке. Если продолжить, открытая форма получит только ваш контакт, короткое описание намерения и, если применимо, тип приглашения.']
      },
      pro_result: {
        k: ['A relevant introduction', 'Подходящий контакт'],
        h: ['Continue with only your professional intent.', 'Передайте только профессиональное намерение.'],
        p: ['The contact form will not include your quiz answers. It will contain a short request to connect and, if applicable, the invitation type.', 'Форма не получит ответы квиза. В ней будет только короткая просьба связаться и, если применимо, тип приглашения.']
      },
      support_result: {
        k: ['Support is separate from participation', 'Поддержка отделена от участия'],
        h: [CAMPAIGN_URL ? 'Review the live campaign.' : 'Get the launch link when it is ready.', CAMPAIGN_URL ? 'Посмотрите действующую страницу сбора.' : 'Получите ссылку, когда сбор откроется.'],
        p: [CAMPAIGN_URL ? 'The verified external page contains the current recipient and payment terms.' : 'There is no verified payment URL yet. Nothing is charged here.', CAMPAIGN_URL ? 'На проверенной внешней странице указаны получатель и условия оплаты.' : 'Проверенной платёжной ссылки пока нет. Здесь ничего не списывается.']
      },
      other_result: {
        k: ['Thanks for taking a look', 'Спасибо за интерес'],
        h: ['Choose a simple next step.', 'Выберите простой следующий шаг.'],
        p: ['You can return to the site, share Emozu, or leave only your contact, update intent and, if applicable, the invitation type.', 'Можно вернуться на сайт, поделиться Emozu или оставить только контакт, намерение получать новости и, если применимо, тип приглашения.']
      },
      underage: {
        k: ['For adults only', 'Только для взрослых'],
        h: ['Please ask an adult to contact Emozu.', 'Попросите взрослого связаться с Emozu.'],
        p: ['You can still read the public site. Do not send personal or medical information here.', 'Открытый сайт можно читать. Не отправляйте сюда личную или медицинскую информацию.']
      }
    }[id];
    setBase(tx(copy.k), tx(copy.h), tx(copy.p));
    skip.hidden = true;
    var box = document.createElement('div');
    box.className = 'quiz-summary';

    if (id === 'support_result') {
      var money = document.createElement('div');
      money.className = 'quiz-money';
      money.innerHTML = '<span><b>$20,000</b>' + (lang === 'ru' ? 'цель сбора' : 'fundraising goal') + '</span><span><b>$10+</b>' + (lang === 'ru' ? 'плановый взнос' : 'planned contribution') + '</span>';
      box.appendChild(money);
      if (CAMPAIGN_URL) {
        var a = document.createElement('a');
        a.className = 'btn'; a.href = CAMPAIGN_URL; a.target = '_blank'; a.rel = 'noopener';
        a.textContent = lang === 'ru' ? 'Открыть страницу сбора' : 'Open campaign page';
        box.appendChild(a);
      } else {
        box.appendChild(summaryButton(lang === 'ru' ? 'Сообщить мне о старте' : 'Tell me when it opens', function () { go('handoff'); }));
      }
    } else if (id !== 'underage') {
      box.appendChild(summaryButton(lang === 'ru' ? 'Продолжить только с моим намерением' : 'Continue with only my intent', function () { go('handoff'); }));
    }
    if (id !== 'underage') addInviteActions(box);
    box.appendChild(summaryButton(lang === 'ru' ? 'Закончить приватно' : 'Finish privately', finishPrivately, true));
    var privacy = document.createElement('p');
    privacy.className = 'quiz-privacy';
    privacy.textContent = lang === 'ru' ? 'Ответы удалятся при закрытии или обновлении вкладки. Мы не записываем имя ребёнка и медицинскую историю.' : 'Answers disappear when this tab closes or reloads. We do not ask for a child’s name or medical history.';
    box.appendChild(privacy);
    optionsBox.appendChild(box);
  }

  function renderHandoff() {
    setBase(lang === 'ru' ? 'Явное согласие' : 'Clear consent', lang === 'ru' ? 'Подготовить контактную форму?' : 'Prepare the contact form?', lang === 'ru' ? 'Если выбрать «Да», мы заполним только вашу роль, намерение и тип приглашения, если вы пришли по нему. Вы сами добавите контакт, проверите текст и нажмёте «Отправить». Ответы о ребёнке не передаются.' : 'If you choose Yes, we prefill only your role and intent, plus the invitation type if you arrived through one. You add your own contact, review the text and press Send. No answers about a child are passed on.');
    var item = q('handoff', '', '', [
      o('yes', 'Yes, prepare the form', 'Да, подготовить форму'),
      o('no', 'No, finish privately', 'Нет, закончить приватно')
    ], { required: true });
    item.options.forEach(function (opt) { optionsBox.appendChild(optionButton(item, opt)); });
    skip.hidden = true;
  }

  function render() {
    setProgress();
    var id = currentId();
    if (id === 'invite_choose') renderInviteChoice();
    else if (id === 'invite_friend' || id === 'invite_investor') renderInvite(id === 'invite_friend' ? 'friend' : 'investor');
    else if (id === 'handoff') renderHandoff();
    else if (isResult(id)) renderResult(id);
    else renderQuestion(Q[id]);
    window.setTimeout(function () { title.focus({ preventScroll: true }); }, 0);
  }

  function intentForForm() {
    var route = routeName();
    var en, ru, role;
    if (route === 'family') {
      role = 'Parent or family';
      var f = answers.get('family_role') || answers.get('family_goal');
      if (f === 'support') {
        en = 'I am an adult and would like the Emozu fundraising launch link. I understand support is separate from study participation.';
        ru = 'Я взрослый человек и хочу получить ссылку на сбор Emozu после запуска. Я понимаю, что поддержка не связана с участием в исследовании.';
      } else if (f === 'participant' || f === 'pilot') {
        en = 'I am an adult and would like to hear about possible participation in the voluntary six-family Emozu pilot. I understand this is not enrollment and that a family can stop at any time.';
        ru = 'Я взрослый человек и хочу узнать о возможном добровольном участии в пилоте Emozu на шесть семей. Я понимаю, что это не запись и семья может остановиться в любой момент.';
      } else if (f === 'codesign' || f === 'design') {
        en = 'I am an adult family member and would like to give practical feedback on the Emozu pilot.';
        ru = 'Я взрослый член семьи и хочу дать практическую обратную связь о пилоте Emozu.';
      } else {
        en = 'I am an adult family member and would like project updates.';
        ru = 'Я взрослый член семьи и хочу получать новости проекта.';
      }
    } else if (route === 'professional') {
      var pt = answers.get('pro_type');
      role = pt === 'clinician' ? 'Clinician or psychiatrist' : pt === 'research' ? 'Research group' : pt === 'hardware' ? 'Hardware engineer' : pt === 'signal' ? 'ML or signal' : 'Partner';
      en = 'I am interested in connecting about a professional contribution to the Emozu research pilot.';
      ru = 'Я хочу обсудить профессиональный вклад в исследовательский пилот Emozu.';
    } else if (route === 'support') {
      role = answers.get('support_type') === 'sponsor' ? 'Partner' : 'Other';
      en = answers.get('support_goal') === 'sponsor' ? 'I am interested in discussing sponsorship for the Emozu research pilot.' : 'Please send me the Emozu fundraising launch link when it is ready. I understand nothing is charged by this form.';
      ru = answers.get('support_goal') === 'sponsor' ? 'Я хочу обсудить спонсорство исследовательского пилота Emozu.' : 'Пожалуйста, пришлите мне ссылку на сбор Emozu после запуска. Я понимаю, что эта форма ничего не списывает.';
    } else {
      role = 'Other';
      en = 'I would like to receive Emozu project updates.';
      ru = 'Я хочу получать новости проекта Emozu.';
    }
    var message = lang === 'ru' ? ru : en;
    if (refType) {
      message += lang === 'ru' ? '\nТип приглашения: ' + (refType === 'friend' ? 'друг.' : 'инвестор.') : '\nInvitation type: ' + refType + '.';
    }
    return { role: role, message: message };
  }

  function handoffToForm() {
    var form = document.getElementById('writeForm');
    if (!form) return;
    var intent = intentForForm();
    var role = form.querySelector('input[name="role"][value="' + intent.role.replace(/"/g, '\\"') + '"]');
    if (role) {
      role.checked = true;
      role.dispatchEvent(new Event('change', { bubbles: true }));
    }
    form.elements.message.value = intent.message;
    closeQuiz(false);
    history.replaceState(null, '', location.pathname + location.search + '#write');
    document.getElementById('write').scrollIntoView({ block: 'start', behavior: root.classList.contains('motion') ? 'smooth' : 'auto' });
    window.setTimeout(function () { form.elements.contact.focus({ preventScroll: true }); }, 450);
  }

  function finishPrivately() { closeQuiz(true); }
  function resetQuiz() { answers.clear(); trail = ['route']; }
  function openQuiz(push) {
    if (!shell.classList.contains('open')) lastFocus = document.activeElement;
    shell.classList.add('open');
    shell.setAttribute('aria-hidden', 'false');
    document.body.classList.add('quiz-open');
    if (push && location.hash !== '#quiz') history.pushState(null, '', location.pathname + location.search + '#quiz');
    render();
  }
  function closeQuiz(reset) {
    shell.classList.remove('open');
    shell.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('quiz-open');
    if (location.hash === '#quiz') history.replaceState(null, '', location.pathname + location.search);
    if (reset) resetQuiz();
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus({ preventScroll: true });
  }

  document.querySelectorAll('a[href="#quiz"]').forEach(function (a) {
    a.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); openQuiz(true); }, true);
  });
  close.addEventListener('click', function () { closeQuiz(true); });
  back.addEventListener('click', function () {
    if (trail.length <= 1) return;
    var removed = trail.pop();
    answers.delete(removed);
    pruneAfterBack();
    render();
  });
  skip.addEventListener('click', function () { answers.set(currentId(), null); advance(); });
  addEventListener('hashchange', function () {
    if (location.hash === '#quiz') openQuiz(false);
    else if (shell.classList.contains('open')) closeQuiz(false);
  });
  document.addEventListener('keydown', function (e) {
    if (!shell.classList.contains('open')) return;
    if (e.key === 'Escape') { e.preventDefault(); closeQuiz(true); return; }
    if (e.key !== 'Tab') return;
    var focusable = Array.prototype.slice.call(shell.querySelectorAll('button:not([hidden]):not([disabled]),a[href]')).filter(function (el) { return el.offsetParent !== null; });
    if (!focusable.length) return;
    var first = focusable[0], last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
  });

  if (location.hash === '#quiz') openQuiz(false);
})();
