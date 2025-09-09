import aiohttp
import base64
import logging
from typing import Dict, Any, List, Optional
from config import GOOGLE_VISION_API_KEY

class GoogleVisionAnalyzer:
    """Анализатор изображений через Google Vision API"""
    
    def __init__(self):
        self.api_key = GOOGLE_VISION_API_KEY
        self.base_url = "https://vision.googleapis.com/v1/images:annotate"
    
    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """Анализирует изображение через Google Vision API"""
        
        # Кодируем изображение в base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Формируем запрос
        request_body = {
            "requests": [{
                "image": {
                    "content": image_base64
                },
                "features": [
                    {
                        "type": "LABEL_DETECTION",
                        "maxResults": 10
                    },
                    {
                        "type": "FACE_DETECTION",
                        "maxResults": 10
                    },
                    {
                        "type": "TEXT_DETECTION",
                        "maxResults": 10
                    },
                    {
                        "type": "OBJECT_LOCALIZATION",
                        "maxResults": 10
                    },
                    {
                        "type": "LANDMARK_DETECTION",
                        "maxResults": 5
                    },
                    {
                        "type": "LOGO_DETECTION",
                        "maxResults": 5
                    }
                ]
            }]
        }
        
        # URL с API ключом
        url = f"{self.base_url}?key={self.api_key}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_body) as response:
                    if response.status == 200:
                        result = await response.json()
                        return self.parse_analysis_result(result)
                    else:
                        error_text = await response.text()
                        logging.error(f"Google Vision API error: {response.status} - {error_text}")
                        return None
        except Exception as e:
            logging.error(f"Error calling Google Vision API: {e}")
            return None
    
    def parse_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Парсит результат анализа Google Vision API"""
        
        if not result or 'responses' not in result:
            return None
        
        response = result['responses'][0]
        parsed = {
            'labels': [],
            'faces': [],
            'text': [],
            'objects': [],
            'landmarks': [],
            'logos': []
        }
        
        # Извлекаем метки (labels)
        if 'labelAnnotations' in response:
            for label in response['labelAnnotations']:
                parsed['labels'].append({
                    'description': label['description'],
                    'confidence': label['score']
                })
        
        # Извлекаем лица
        if 'faceAnnotations' in response:
            for face in response['faceAnnotations']:
                emotions = []
                if 'joyLikelihood' in face:
                    emotions.append(f"радость: {face['joyLikelihood']}")
                if 'sorrowLikelihood' in face:
                    emotions.append(f"грусть: {face['sorrowLikelihood']}")
                if 'angerLikelihood' in face:
                    emotions.append(f"злость: {face['angerLikelihood']}")
                if 'surpriseLikelihood' in face:
                    emotions.append(f"удивление: {face['surpriseLikelihood']}")
                
                parsed['faces'].append({
                    'emotions': emotions,
                    'detection_confidence': face.get('detectionConfidence', 0)
                })
        
        # Извлекаем текст
        if 'textAnnotations' in response:
            for text in response['textAnnotations']:
                parsed['text'].append(text['description'])
        
        # Извлекаем объекты
        if 'localizedObjectAnnotations' in response:
            for obj in response['localizedObjectAnnotations']:
                parsed['objects'].append({
                    'name': obj['name'],
                    'confidence': obj['score']
                })
        
        # Извлекаем достопримечательности
        if 'landmarkAnnotations' in response:
            for landmark in response['landmarkAnnotations']:
                parsed['landmarks'].append({
                    'description': landmark['description'],
                    'confidence': landmark['score']
                })
        
        # Извлекаем логотипы
        if 'logoAnnotations' in response:
            for logo in response['logoAnnotations']:
                parsed['logos'].append({
                    'description': logo['description'],
                    'confidence': logo['score']
                })
        
        return parsed

class GrishaPhotoCommenter:
    """Генератор токсичных комментариев Гриши для фотографий"""
    
    def __init__(self):
        # Фирменные подколы по авто-брендам
        self.brand_roasts = {
            'bmw': [
                "BMW как мечта — обычно чужая",
                "Баварская надёжность: до первого бордюра",
                "M-настроение, а едет в режимах ‘пробка’ и ‘посторонитесь’",
                "Повороты любит. Владелец — понты ещё больше"
            ],
            'bmw_m': [
                "М-пакет говорит громко, здравый смысл — шёпотом",
                "M в шильдике, ‘мда’ — в динамике",
                "Спортсиденья спасают от грусти, не от фактов"
            ],
            'mercedes': [
                "Мерс солиден. Водитель — как получится",
                "Комфортный корабль. Капитан — с TikTok-правами",
                "Хром блестит, ответственность — матовая"
            ],
            'amg': [
                "AMG шипит. А ты шепчешь ‘ну пожалуйста’ светофорам",
                "AMG на шильдике, АМ… ну ты понял — в навыках",
                "Звук зверя, трек — в навигаторе"
            ],
            'audi': [
                "Audi ровная, как твои отговорки",
                "Quattro держит. Ты — нет",
                "Фары злые, намерения добрые — к парковке у входа"
            ],
            'audi_rs': [
                "RS на бампере, ‘рассрочка’ в душе",
                "RS-планы, SV-реальность",
                "Launch включён, аргументы — нет"
            ],
            'porsche': [
                "Порше — сильный ход. Жалко, дальше — ты",
                "911 на фото, 1-1-1 в счёте разуму",
                "Тормоза честные, пилот — посмотрим"
            ],
            'ferrari': [
                "Феррари краснеет не только из‑за краски",
                "Кобыл много, всадник — условный",
                "Вид на миллион. Манеры — на подписку"
            ],
            'lamborghini': [
                "Ламба орёт, как твой будильник: эффектно, бесполезно",
                "Двери вверх, аргументы вниз",
                "Уголки острее, чем твой вкус"
            ],
            'tesla': [
                "Тесла быстрый телефон на колёсах",
                "Автопилот просит рулить, здравый смысл — тоже",
                "Разгон как твои обещания: первый рывок — и тишина"
            ],
            'toyota': [
                "Тойота вечная. Нервная система — нет",
                "Супра в мечтах, парковка у ТЦ — в реале",
                "Надёжность как алиби"
            ],
            'nissan': [
                "Ниссан бодр, особенно в разговорах",
                "GTR в легендах, Skyline — на наклейке",
                "Из стока в стон — три болта и форум"
            ],
            'subaru': [
                "Субару шьёт поворот, владелец — дыры в бюджете",
                "Boxer рычит, аргументы свистят",
                "STI на капоте, ОТС на душе"
            ],
            'honda': [
                "Хонда честная. Владелец — нет",
                "VTEC включается, социальные навыки — позже",
                "Type R в мечтах, тип R — разговоров"
            ],
        }
        # Сценарные шаблоны (заточены под конкретные сюжеты)
        self.scenario_templates = {
            'fishing': [
                "Рыбалка? А чем хвалиться — я вчера вдвое больше поймал",
                "Снасти мощные, истории ещё мощнее",
                "Поймал момент, а не рыбу — тоже результат",
                "Удочка длинная, терпение — короче",
                "Рассказ про улов уже весит больше самого улова",
                "Поклёвка была? Отлично. Остальное дорисуешь словами",
                "Сеть легенд — улов побольше реального"
            ],
            'male_group': [
                "Класс, пацаны, как отдохнули без женщин",
                "Мужской совет: решений ноль, уверенности тонна",
                "Лица бодрые, планы сомнительные — идеальный вечер",
                "Банда в сборе. Ответственный — никто",
                "Тестостерон на максимум, дистанция до разума — побольше",
                "Коллектив сильный, дисциплина — в отпуске"
            ],
            'female_group': [
                "Сияете. Остальным остаётся догонять",
                "Глянец на фото, железобетон в характере",
                "Собрались, чтобы мир немного напрягся",
                "Красиво и слаженно — будто это легко",
                "Фотогеничность 100%. Терпение окружающих — посмотрим",
                "Стильно, резко, по делу. Хлопаем молча"
            ],
            'mixed_group': [
                "Микс настроений: кто смеётся — тот ещё не в теме",
                "Состав разный, история общая. Фотографу — медаль",
                "Смешали людей и ожидания — получилось как всегда",
                "Кто-то уже пожалел, что пришёл. Но поздно",
                "Команда разношёрстная, цель — как получится",
                "Кому весело, а кому это всё ещё объяснять"
            ],
            'party': [
                "Праздник идёт по плану: завтра будет больно смотреть в календарь",
                "Веселитесь от души, счёт возьмёт завтра",
                "Танцы включены, память — как повезёт",
                "Музыка орёт, аргументы молчат",
                "Ночь обещает, утро всё спишет"
            ],
            'alcohol': [
                "Стекло звенит, аргументы падают — классика",
                "Тосты крепнут, решения слабеют",
                "Бутылки говорят убедительнее вас",
                "Градусы растут, мудрость — на паузе",
                "Праздник идёт, ответственность ждёт в коридоре"
            ],
            'wedding': [
                "Свадьба: обещают навсегда, платят сегодня",
                "Жених уверен, невеста светится — счёт плачет",
                "Фото на века. Пусть хотя бы оно продержится",
                "Красиво. Теперь к сложному — жить вместе",
                "Обеты громкие, логистика — громче"
            ],
            'gym': [
                "Железо движется, эго растёт — держи баланс",
                "Селфи в зале — половина тренировки. Вторая — лайки",
                "Тяга серьёзная, техника спорная — но уважение есть",
                "Гриф тяжелее самооценки — прогресс",
                "Памп есть, дисциплина придёт с опозданием"
            ],
            'car': [
                "Супер пушка гонка. На практике — маршрутка с амбициями",
                "Корыто для лошадей. А ты тут зачем — седлом работать?",
                "Лошадей заявлено много, бегают по очереди",
                "Пушка-гонка, и тут закончился бюджет",
                "Звук спорткара, скорость автобуса",
                "Капот блестит, а харизма — матовая",
                "Обвес орёт, мотор шепчет",
                "Литьё сияет, резина — эпоха динозавров",
                "Трек видел только в навигаторе",
                "Наклейка Sport лошадей не добавляет",
                "Спойлер выше самооценки",
                "Выхлоп как чайник: шуму море, толку чайная ложка",
                "До сотни — если ветер попутный и горка вниз",
                "Салон мечты: тесно, громко, пахнет химией и надеждой",
                "Пацаны заценят, гаишники — быстрее",
                "Кредитный болид. Платёж быстрее, чем разгон",
                "Цвет кричит, лошади шепчут",
                "Пушка-гонка-ну почти",
                "Батин гараж не одобряет. И правильно",
                "Дворники быстрее мотора",
                "Тормоза верят в чудо, а ты — в себя",
                "Нулевик — нулевой результат",
                "Карбон наклеен, карбон в печали",
                "Ламба на аватарке, Лада в кадре",
                "БМВ мечты… соседа",
                "Тесла без розетки — как ты без идей",
                "Руль спортивный, маршрут стандартный: дом—ТЦ—дом",
                "Глушак гремит, совесть молчит",
                "Динамика бодрая. На словах",
                "Диски шире кругозора",
                "Фаркоп для души, багажник для эго",
                "Суточный пробег — до шиномонтажа и обратно",
                "Ксенон светит в пустоту — как твои планы",
                "Вижу «пушка». Слышу «пожалейте уши»",
                "Кузов кричит «гонка», под капотом «я старался»",
                "Зимняя резина круглый год — стиль страдания",
                "Чип-тюнинг для самооценки",
                "Шумка снаружи, тишина внутри",
                "Зеркала огромные — чтобы любоваться собой на обочине",
                "Тормоза тормозят, но не тебя",
                "Седан мечты: твой, чужой и полицейский",
                "Салон кожа-зам, поведение — тоже",
                "Багажник глубокий, мысли — нет",
                "Двигатель шепчет: «отпусти»",
                "Порог выше принципов",
                "Пневма подняла, но не тебя",
                "Рулёжка — как разговоры: много крутить, мало ехать",
                "Пушка-гонка, пока не включишь кондиционер",
                "Стритрейсер парковки ТЦ",
                "Шильдик AMG, характер AM… ну ты понял",
                "RS в мечтах, «Рассрочка» в реале",
                "M-пакет на теле, М-отказ от здравого смысла",
                "Спойлер спасёт. От вкуса — нет",
                "Ксенон в глаза, аргументы в никуда",
                "Колхоз-спорт высшей пробы",
                "Пушка? Пук. Гонка? Гоняешь себя",
                "Тюнинг по подписке на форум",
                "Давление в шинах выше, чем в логике",
                "Бампер ниже настроения",
                "Руль крут, пилот — посмотрим",
                "Сцепление просит мира, ты — лайков",
                "Номер красивый, всё остальное — комедия"
            ],
            'beach': [
                "Море спокойно, ты — нет. Честный кадр",
                "Песок везде, идеи — где-то рядом",
                "Пляж хорош, загар делает вид, что помогает",
                "Шум волн заглушил внутренний голос — наконец-то",
                "Релакс поставлен на паузу уведомлениями"
            ],
            'kids': [
                "Ребёнок тащит кадр, взрослые — статисты",
                "Главный тут — он. Смиритесь",
                "Взгляд серьёзный. У тебя такого не было даже на защите",
                "Малой — 10/10. Остальные просто рядом",
                "Мелкий справляется с атмосферой лучше взрослых"
            ],
            'dog': [
                "Пёс красавец. Хозяин старается не мешать — и правильно",
                "Верность в кадре. Остальное — как получится",
                "Собака — 10/10. Человек — для масштаба",
                "Хороший мальчик. Хозяин — попробуй дотянуться",
                "Пёс держит планку. Люди — как получится"
            ],
            'cat': [
                "Кот смотрит, как на несдачу. И где-то прав",
                "Кошка фотогенична, персонал — старается",
                "Пушистый босс, люди — по углам",
                "Властитель дивана разрешил кадр. Пользуйся",
                "Кошачий презрительный взгляд — главный свет в кадре"
            ],
            'food': [
                "На тарелке праздник, на душе — диета",
                "Выглядит вкусно. Жаль, лайки не насыщают",
                "Композиция сильная, выдержка — у пояса",
                "Еда топ, совесть — потом",
                "Повар старался, камера справилась, ты — посмотрим"
            ],
            'landmark': [
                "Туристический чек-ин принят. Местные уже устали",
                "Достопримечательность на месте. Чувство меры — в пути",
                "Фото для ""я тут был"". Верим",
                "Классика маршрута. Ставь галочку",
                "Вид открыток, глубина — на вынос"
            ],
            'landscape': [
                "Природа делает красиво, ты хотя бы не мешал",
                "Свежий воздух — лучший фильтр",
                "Вид сильный, мысли подтянутся",
                "Тут и без тебя хорошо. Но ты попробовал",
                "Горизонт ровный, а вот характер — как получится"
            ],
            'text': [
                "Надпись громкая, дела тихие",
                "Текст уверенный. Выполнение — как обычно",
                "Слова бодрые. Привычки — нет",
                "Читается легко, живётся сложно",
                "Лозунг бодрый, реалити — сезон отменён"
            ],
            'selfie': [
                "Лицо старается, харизма — в пути",
                "Селфи бодрое, обаяние ещё грузится",
                "Грим, фильтр, надежды — а получился ты",
                "Портрет есть, портретности нет",
                "Свет старается, ты — через раз"
            ],
            'group': [
                "Групповая стойка: улыбаемся, будто всё под контролем",
                "Людей много, внимания мало — особенно к сути",
                "Командой вы смелее, чем по одному",
                "Единство ради кадра — уже неплохо",
                "Синхрон по улыбкам есть, по целям — позже"
            ],
            'default': [
                "Кадр уверенный. Смысл подтянется",
                "Снято небездарно. Дальше будет сложнее",
                "Картинка дышит. Ты — попробуй тоже",
                "Неплохо. Неожиданно честно",
                "Амбиции слышны, факты в пути"
            ]
        }

        # Доп. «специи» — короткие фразы для подмешивания вариативности (без техдеталей)
        self.spice_templates = {
            'selfie': [
                "камера терпит, мы держимся",
                "смотришь уверенно, как на лёгкие решения",
                "свет работал больше, чем ты"
            ],
            'group': [
                "каждый герой, сценария нет",
                "улыбки по команде, характер — как получится",
                "кто-то уже жалеет об этом кадре"
            ],
            'fishing': [
                "улов рассказами уже перевешивает",
                "рыба бы отпустила тебя — будь выбор"
            ],
            'party': [
                "завтра голова пришлёт счёт",
                "весело? посмотри истории утром"
            ],
            'alcohol': [
                "бутылки смелее аргументов",
                "причины забудутся, фото напомнит"
            ],
            'wedding': [
                "обещания на максимум, терпение — посмотрим",
                "красивая авантюра начинается"
            ],
            'gym': [
                "железо честнее лайков",
                "селфи засчитано, подход — нет"
            ],
            'car': [
                "выхлоп громче фактов",
                "шильдик кричит, лошади шепчут",
                "трек в навигаторе — это не то же самое"
            ],
            'outfit': [
                "кроссовки громкие, походка — нет",
                "часы блестят, пунктуальность — нет",
                "тату громче аргументов",
                "костюм уверенный, содержание — в пути",
                "брендов много, вкуса поровну"
            ],
            'beach': [
                "песок справится с фильтрами лучше тебя",
                "ветер делает укладку честной"
            ],
            'kids': [
                "главный в кадре — тот, кто не читает чаты",
                "малыш держит атмосферу один"
            ],
            'dog': [
                "хвост — метронôm радости",
                "верность — без фильтров"
            ],
            'cat': [
                "взгляд на миллион, усилия людей — на сдачу",
                "позволил себя снять — цените момент"
            ],
            'food': [
                "вилка дрожит от ожиданий",
                "калории уже празднуют"
            ],
            'landmark': [
                "открытка удалась, впечатления — как получится",
                "турист спокоен, местный — уже нет"
            ],
            'landscape': [
                "природа всё сделала за тебя",
                "воздух чище аргументов"
            ],
            'text': [
                "лозунг орёт, совесть шепчет",
                "буквы бодрые, привычки устали"
            ],
            'default': [
                "форма громче содержания",
                "смело снято, скромно прожито",
                "настроение есть, смысл догонит"
            ]
        }
        # Наборы вариаций без эмодзи и без тех. деталей
        self.comment_variants = {
            'selfie': [
                "Лицо старается, а харизма — нет",
                "Селфи удалась, вот бы с характером так же",
                "Ты снова смотришь в камеру, как в бездну — и она отвечает взаимностью",
                "Грим, фильтр, надежды — а получилось все равно ты",
                "Снимок уверенный, как твои слабые оправдания",
                "Селфи приличное, хотя твой внутренний редактор опять прогулял",
                "Лицо в кадре одно, а эго на весь экран",
                "Портрет есть, портретности нет. Зато старание заметно",
                "Селфи бодрое, но обаяние еще грузится",
                "Хороший свет. Жаль, что на характер он не влияет",
                "Ракурс ищет тебя лучшего. Пока безуспешно",
                "Настроение на фото — как твой Wi‑Fi: то есть, то нет"
            ],
            'food': [
                "Еда выглядит так, будто ей страшно оказаться у тебя дома",
                "На тарелке праздник, на душе — студень",
                "Аппетитно. Главное — не испортить разговорами",
                "Красиво подано. Надеюсь, на вкус не как твои идеи",
                "Если это ты готовил — тогда респект тому, кто выжил",
                "Шик, блеск, калории. Твоя совесть уже вышла из чата",
                "Еда топ, репутация под вопросом",
                "Сфоткал, значит съел. Инстинкты сильнее эстетики",
                "Десерт милый. Почти как твои попытки быть серьезным",
                "Композиция сильная, диета сломалась ещё сильнее",
                "Это выглядит вкусно. Жаль, лайки не насыщают",
                "Кулинарный перфоманс уровня: спасайся кто может"
            ],
            'pet': [
                "Питомец хорош. Ты стараешься не мешать — и это мудро",
                "Животное милое. На его фоне ты почти человек",
                "Кот берет харизмой. Тебе пока не продают",
                "Собака верная. В отличие от твоего режима дня",
                "Зверь очарователен. Постарайся не учить его своим привычкам",
                "Это животное — главная причина, почему фото стоит смотреть",
                "Лапки прекрасные. Хозяин — рабочая версия",
                "Питомец фотогеничен. Ты рядом для масштаба",
                "Хозяин старался, но звезда — не он",
                "Вы оба милые. Он — по факту, ты — по заявке",
                "Пушистик — 10/10. Хозяин — попросим выйти из кадра",
                "Глазки у зверя умные. Возьми контакт тренера"
            ],
            'landscape': [
                "Природа постаралась. Ты пока только сфоткал",
                "Красиво. Даже ты это не испортил — уже достижение",
                "Пейзаж сильный, автор слабее, но амбициозен",
                "Горы держатся молодцом, а ты — за телефон",
                "Спокойный кадр. На твой характер не похоже",
                "Воздух чистый, мысли — посмотрим",
                "Тут красиво без фильтров. Заметил?",
                "Композиция сработала. Теперь бы с жизнью так же",
                "Природа — редактор лучше любого приложения",
                "Пейзаж вдохновляет. Тебе бы тоже начать",
                "Глазам приятно. Эго — помолчи",
                "Место мощное. Ты пока статист"
            ],
            'group': [
                "Толпа улыбается. Значит, кто-то уже сдался",
                "Групповое фото: все заняты тем, чтобы казаться лучше",
                "Лиц много, внимания мало. Особенно к сути",
                "Дружно стоите, дружно устаете",
                "Тут весело по сценарию. А вживую как?",
                "Команда есть. Теперь бы план",
                "Энергии много, синхронизации — как получится",
                "Группой вы выглядите смелее, чем по одному",
                "Кто-то на фото думает о еде. И это лучший план",
                "Людей много — объектив страдает",
                "Съёмка корпоративная по духу, даже если это не так",
                "Химия есть. Только не перегрейте"
            ],
            'text': [
                "Надпись на фото тонко намекает, что пора взять себя в руки",
                "Текст громкий, смысл в отпуске",
                "Надпись уверена, что это важно. Убедила?",
                "Лозунг бодрый. Привычки — нет",
                "Слова прямо в кадре. И все равно мимо сути",
                "Текст старается, читатель — как получится",
                "Подпись серьезная, жизнь — мем",
                "Если следовать написанному, сюрпризов будет меньше",
                "Текст на месте, выводов нет",
                "Надпись кричит, совесть шепчет",
                "Слова не плохие. Выполнение традиционно страдает",
                "Читается легко, выполняется тяжело"
            ],
            'default': [
                "Кадр уверенный, смысла в нем примерно как в твоих оправданиях",
                "Снято небездарно. Дальше будет сложнее",
                "Фото живое. Постарайся не заглушить",
                "Композиция пытается, ты мешаешь чуть меньше обычного",
                "Снимок норм. С характером поработаем позже",
                "В этом кадре есть настроение. Тебе бы такое",
                "Получилось на удивление сносно",
                "Неплохо. Неожиданно честно",
                "Слегка драматично. Как твоя самооценка по утрам",
                "Смотришь — и вроде хочется верить, что ты стараешься",
                "Дерзко сфоткал. Осталось жить в том же стиле",
                "Картинка дышит. Ты — попробуй тоже"
            ]
        }
    
    async def generate_comment(self, analysis: Dict[str, Any]) -> str:
        """Генерирует токсичный, но естественный комментарий по контексту фото.
        Без тех. деталей, только одна короткая реплика."""
        
        if not analysis:
            return "Не получилось понять, что на фото. Попробуй другое — и без ужасов, ладно"
        
        # Сначала пытаемся определить сценарии и говорить конкретнее
        seed = self._build_seed(analysis)
        scenarios = self.detect_scenarios(analysis)
        result = None
        for sc in scenarios:
            if sc == 'car':
                # Бренд и оценка тюнинга
                brand_key = self._detect_car_brand(analysis)
                base_options = (self.brand_roasts.get(brand_key) or []) + self.scenario_templates.get('car', [])
                base = self._pick_variant(base_options, seed, 71)
                rating = self._rate_tuning(analysis, seed)
                result = self._compose_comment(base, rating)
                break
            options = self.scenario_templates.get(sc)
            if options:
                result = self._pick_variant(options, seed, 71)
                break
        
        # Фолбэк по типу (на случай нераспознанного сюжета)
        if not result:
            photo_type = self.determine_photo_type(analysis)
            base_set = (self.comment_variants.get(photo_type)
                        or self.comment_variants.get('default'))
            result = self._pick_variant(base_set, seed, 17)
        
        # Добавим «специю» иногда, для разнообразия (не всегда)
        # Добавим специи (включая «оценку образа», если уместно)
        outfit_spice = self._build_outfit_spice(analysis, seed)
        spice = outfit_spice or self._pick_spice(scenarios, analysis, seed)
        if spice:
            result = self._compose_comment(result, spice)

        # Фильтрация заезженных фраз
        banned = [
            "О, еще одно селфи",
            "Красиво, но не так красиво, как мой код",
            "Фильтры работают, а вот твоя логика - нет",
            "Текст есть, а смысла нет",
            "Текст на фото умнее тебя",
            "Групповое фото - это когда все притворяются, что им весело",
            "в кадре деталей достаточно, осталось навести на смысл",
            "на фото один герой, и ему бы отдохнуть",
            "надпись уверенно делает вид, что так и задумано"
        ]
        lower = result.lower()
        if any(p.lower() in lower for p in banned):
            alt = self._pick_variant(self.scenario_templates.get('default') or self.comment_variants.get('default'), seed, 911)
            result = alt if alt else result
        return result

    def generate_comparison_comment(self, analysis_a: Dict[str, Any], analysis_b: Dict[str, Any]) -> str:
        """Едкая реплика по двум фото: что изменилось."""
        try:
            seed = (self._build_seed(analysis_a) ^ self._build_seed(analysis_b)) & 0xFFFFFFFF
            diffs = []
            a_faces = len(analysis_a.get('faces') or [])
            b_faces = len(analysis_b.get('faces') or [])
            if a_faces != b_faces:
                diffs.append("лиц стало «%d → %d»" % (a_faces, b_faces))
            a_text = bool(analysis_a.get('text'))
            b_text = bool(analysis_b.get('text'))
            if a_text != b_text:
                diffs.append("текст «%s → %s»" % ("есть" if a_text else "нет", "есть" if b_text else "нет"))
            a_tokens = set(self._extract_tokens(analysis_a))
            b_tokens = set(self._extract_tokens(analysis_b))
            gained = list((b_tokens - a_tokens))[:3]
            lost = list((a_tokens - b_tokens))[:3]
            if gained:
                diffs.append("прибавилось: " + ', '.join(gained))
            if lost:
                diffs.append("пропало: " + ', '.join(lost))
            base_set = [
                "Сравнил. Стало иначе, лучше — спорно",
                "Разница есть, но смысл всё ещё в пути",
                "Фото сменились, привычки — нет",
                "Второе бодрее. Или просто ты устал на первое смотреть",
                "Эволюция заметна, интеллект — под вопросом"
            ]
            import random
            base = random.Random(seed + 909).choice(base_set)
            tail = ''
            if diffs:
                text = '; '.join(diffs[:2])
                tail = text
            comment = self._compose_comment(base, tail)
            return comment
        except Exception:
            return "Два кадра — один вывод: ты всё ещё ты"

    def _detect_car_brand(self, analysis: Dict[str, Any]) -> str:
        tokens = self._extract_tokens(analysis)
        joined = ' '.join(tokens)
        l = joined.lower()
        if any(k in l for k in ['amg', 'mercedes', 'benz']):
            if 'amg' in l:
                return 'amg'
            return 'mercedes'
        if any(k in l for k in ['rs ', ' rs', 'audi']):
            if ' rs' in l or 'rs' in l:
                return 'audi_rs'
            return 'audi'
        if any(k in l for k in ['bmw', 'm3', 'm4', 'm5']):
            if any(k in l for k in ['m3','m4','m5']):
                return 'bmw_m'
            return 'bmw'
        if 'porsche' in l or '911' in l or 'carrera' in l:
            return 'porsche'
        if 'ferrari' in l:
            return 'ferrari'
        if 'lamborghini' in l or 'huracan' in l or 'aventador' in l:
            return 'lamborghini'
        if 'tesla' in l:
            return 'tesla'
        if 'toyota' in l or 'supra' in l:
            return 'toyota'
        if 'nissan' in l or 'gtr' in l or 'skyline' in l:
            return 'nissan'
        if 'subaru' in l or 'sti' in l or 'wrx' in l:
            return 'subaru'
        if 'honda' in l or 'civic' in l or 'type r' in l:
            return 'honda'
        return ''

    def _rate_tuning(self, analysis: Dict[str, Any], seed: int) -> str:
        """Грубая оценка «пушка/корыто» по признакам тюнинга/состояния."""
        tokens = [t.lower() for t in self._extract_tokens(analysis)]
        score = 0
        pos = ['spoiler', 'wing', 'diffuser', 'carbon', 'widebody', 'lip', 'splitter', 'coilover', 'brembo', 'forged', 'roll cage', 'bucket seat']
        neg = ['rust', 'dent', 'scratch', 'crack', 'damage', 'dirty', 'mud', 'tape', 'primer']
        flex = ['exhaust', 'muffler', 'straight pipe', 'neon', 'sticker', 'vinyl', 'stance', 'camber']
        wheels = ['rim', 'rims', 'alloy wheel', 'wheel', 'spoke', 'wheel hub']
        for t in tokens:
            if any(k in t for k in pos):
                score += 2
            if any(k in t for k in neg):
                score -= 2
            if any(k in t for k in flex):
                score += 1
            if any(k in t for k in wheels):
                score += 1
        import random
        rnd = random.Random(seed + 606)
        score += rnd.choice([-1, 0, 0, 1])
        if score >= 4:
            return "пушка, но не для ушей"
        if score >= 2:
            return "почти пушка — ещё мозг подтянуть"
        if score <= -2:
            return "корыто на стиле"
        return "колхоз‑спорт премиум-сегмента"

    def _build_outfit_spice(self, analysis: Dict[str, Any], seed: int) -> str:
        """Короткий roast по образу: одежда/часы/кроссовки/тату."""
        tokens = [t.lower() for t in self._extract_tokens(analysis)]
        cues = 0
        clothing = ['clothing', 'apparel', 'shirt', 't-shirt', 'hoodie', 'jacket', 'suit', 'tie', 'dress', 'jeans']
        watch = ['watch', 'wristwatch', 'rolex', 'omega', 'audemars', 'patek']
        sneaker = ['sneaker', 'shoe', 'nike', 'adidas', 'yeezy', 'new balance', 'jordan', 'reebok', 'puma']
        tattoo = ['tattoo', 'ink', 'sleeve']
        brand_fashion = ['gucci', 'lv', 'louis vuitton', 'supreme', 'balenciaga', 'prada', 'dior']
        if any(k in ' '.join(tokens) for k in clothing):
            cues += 1
        if any(k in ' '.join(tokens) for k in watch):
            cues += 1
        if any(k in ' '.join(tokens) for k in sneaker):
            cues += 1
        if any(k in ' '.join(tokens) for k in tattoo):
            cues += 1
        if any(k in ' '.join(tokens) for k in brand_fashion):
            cues += 1
        if cues == 0:
            return ""
        pool = self.spice_templates.get('outfit', [])
        return self._pick_variant(pool, seed, 515) if pool else ""

    def _pick_spice(self, scenarios: list, analysis: Dict[str, Any], seed: int) -> str:
        """Выбирает короткую «специйную» фразу по сценарию или общую, с вероятностью ~60%."""
        import random
        rnd = random.Random(seed + 222)
        if rnd.random() > 0.6:
            return ""
        # Берём первый распознанный сценарий с доступными специями
        for sc in scenarios:
            opts = self.spice_templates.get(sc)
            if opts:
                return self._pick_variant(opts, seed, 333)
        # Иначе — общую
        return self._pick_variant(self.spice_templates['default'], seed, 444)

    def _compose_comment(self, base: str, spice: str) -> str:
        """Аккуратно объединяет базовую фразу и специйную часть в одну строчку."""
        if not spice:
            return base
        # Стараемся держать это одной строкой, без эмодзи и техдеталей
        # Выбираем разделитель детерминированно
        import random
        sep = random.Random(len(base) + len(spice)).choice([' — ', '; ', '. '])
        # Избегаем удвоенной точки
        base = base.rstrip('.;!?, ')
        spice = spice.lstrip('.;!?, ')
        return f"{base}{sep}{spice}"
    
    def determine_photo_type(self, analysis: Dict[str, Any]) -> str:
        """Определяет тип фото на основе анализа"""
        
        # Проверяем наличие лиц
        if analysis.get('faces'):
            face_count = len(analysis['faces'])
            if face_count == 1:
                return 'selfie'
            else:
                return 'group'
        
        # Проверяем метки
        labels = [label['description'].lower() for label in analysis.get('labels', [])]
        
        # Еда
        food_keywords = ['food', 'meal', 'dish', 'restaurant', 'cooking', 'kitchen', 'pizza', 'burger', 'sandwich']
        if any(keyword in ' '.join(labels) for keyword in food_keywords):
            return 'food'
        
        # Животные
        pet_keywords = ['dog', 'cat', 'pet', 'animal', 'puppy', 'kitten', 'bird', 'fish']
        if any(keyword in ' '.join(labels) for keyword in pet_keywords):
            return 'pet'
        
        # Пейзажи
        landscape_keywords = ['landscape', 'nature', 'mountain', 'forest', 'beach', 'sky', 'tree', 'water']
        if any(keyword in ' '.join(labels) for keyword in landscape_keywords):
            return 'landscape'
        
        # Текст
        if analysis.get('text'):
            return 'text'
        
        return 'default'

    def detect_scenarios(self, analysis: Dict[str, Any]) -> list:
        """Возвращает список вероятных сценариев по приоритету."""
        tokens = self._extract_tokens(analysis)
        faces = len(analysis.get('faces') or [])
        scenarios = []
        add = scenarios.append

        def has_any(words):
            lw = [w.lower() for w in words]
            return any(any(w in t for t in tokens) for w in lw)

        # Рыбалка
        if has_any(['fishing', 'fisherman', 'angling', 'fish', 'rod', 'recreational fishing', 'bait', 'hook', 'tackle', 'boat', 'river', 'lake']):
            add('fishing')

        # Группы
        is_group = faces >= 3 or has_any(['group', 'crowd', 'team', 'squad'])
        if is_group:
            male = has_any(['man', 'men', 'male', 'boy', 'boys', 'gentleman', 'gentlemen'])
            female = has_any(['woman', 'women', 'female', 'girl', 'girls', 'lady', 'ladies', 'bride'])
            if male and not female:
                add('male_group')
            elif female and not male:
                add('female_group')
            else:
                add('mixed_group')

        # Свадьба / вечеринка / алкоголь
        if has_any(['wedding', 'bride', 'groom', 'wedding dress', 'tuxedo', 'veil', 'bouquet', 'ceremony']):
            add('wedding')
        if has_any(['party', 'celebration', 'nightclub', 'festival', 'dance', 'birthday']):
            add('party')
        if has_any(['beer', 'wine', 'champagne', 'vodka', 'whiskey', 'brandy', 'bottle', 'glass', 'alcohol', 'bar', 'pub']):
            add('alcohol')

        # Бич / зал / авто
        if has_any(['beach', 'sea', 'ocean', 'sand', 'shore', 'coast']):
            add('beach')
        if has_any(['gym', 'fitness', 'dumbbell', 'barbell', 'workout', 'weightlifting']):
            add('gym')
        if has_any(['car', 'vehicle', 'automobile', 'sports car', 'sedan', 'suv', 'supercar', 'motorcar', 'convertible', 'coupe', 'hatchback', 'wagon', 'pickup', 'truck', 'race car', 'racing']):
            add('car')
        # Логотипы авто брендов тоже считаем как сценарий "car"
        if has_any(['bmw', 'mercedes', 'amg', 'audi', 'rs', 'm3', 'm5', 'm4', 's3', 's4', 's5', 'rs6', 'rs7', 'porsche', '911', 'carrera', 'taycan', 'ferrari', 'lamborghini', 'huracan', 'aventador', 'bugatti', 'chirons', 'pagani', 'koenigsegg', 'tesla', 'model s', 'model 3', 'model x', 'model y', 'toyota', 'supra', 'nissan', 'gtr', 'skyline', 'subaru', 'sti', 'wrx', 'honda', 'civic', 'type r', 'ford', 'mustang', 'shelby', 'focus rs', 'chevrolet', 'camaro', 'corvette', 'dodge', 'challenger', 'charger', 'hellcat', 'lexus', 'is f', 'rc f', 'jaguar', 'mclaren', 'aston martin', 'bentley', 'rolls-royce', 'maserati', 'alfa romeo', 'vag']):
            add('car')

        # Дети / питомцы
        if has_any(['baby', 'child', 'kid', 'toddler', 'newborn', 'infant']):
            add('kids')
        if has_any(['dog', 'puppy', 'canine']):
            add('dog')
        if has_any(['cat', 'kitten', 'feline']):
            add('cat')

        # Еда / достопримечательности / пейзаж / текст
        if has_any(['food', 'meal', 'dish', 'cuisine', 'pizza', 'burger', 'sushi', 'salad', 'cake', 'dessert', 'coffee']):
            add('food')
        if has_any(['landmark', 'tower', 'cathedral', 'bridge', 'castle', 'monument', 'plaza', 'square', 'church']):
            add('landmark')
        if has_any(['landscape', 'mountain', 'forest', 'lake', 'river', 'sky', 'cloud', 'sunset', 'sunrise', 'tree', 'nature']):
            add('landscape')
        if analysis.get('text'):
            add('text')

        # Селфи / группа в конец, если не распознали специфики
        if faces == 1:
            add('selfie')
        if is_group and all(s not in scenarios for s in ['male_group','female_group','mixed_group','group']):
            add('group')

        # Всегда завершаем default
        add('default')
        return scenarios

    def _extract_tokens(self, analysis: Dict[str, Any]) -> list:
        """Собирает токены из labels/objects для эвристик."""
        tokens = []
        for l in (analysis.get('labels') or [])[:15]:
            d = (l.get('description') or '').lower()
            if d:
                tokens.append(d)
        for o in (analysis.get('objects') or [])[:15]:
            n = (o.get('name') or '').lower()
            if n:
                tokens.append(n)
        for lg in (analysis.get('logos') or [])[:10]:
            ld = (lg.get('description') or '').lower()
            if ld:
                tokens.append(ld)
        return tokens

    def _build_seed(self, analysis: Dict[str, Any]) -> int:
        """Строит детерминированное семя на основе содержимого, чтобы разные фото давали разные фразы."""
        try:
            import hashlib
            parts = []
            for lbl in (analysis.get('labels') or [])[:5]:
                parts.append(lbl.get('description', ''))
            for obj in (analysis.get('objects') or [])[:5]:
                parts.append(obj.get('name', ''))
            if analysis.get('text'):
                parts.append((analysis['text'][0] or '')[:32])
            raw = '|'.join(parts) or 'fallback'
            h = hashlib.sha256(raw.encode('utf-8')).hexdigest()
            return int(h[:12], 16)
        except Exception:
            import time
            return int(time.time() * 1000) & 0xFFFFFFFF

    def _pick_variant(self, options, seed: int, salt: int) -> str:
        """Выбирает вариант из списка детерминированно от seed."""
        import random
        rnd = random.Random(seed + salt)
        return rnd.choice(options)

    def _build_tail(self, analysis: Dict[str, Any], seed: int) -> str:
        """Строит короткий хвост-комментарий по контексту (лица/текст/объекты), без тех. деталей."""
        phrases = []
        face_count = len(analysis.get('faces') or [])
        if face_count == 1:
            phrases.append("на фото один герой, и ему бы отдохнуть")
        elif face_count > 3:
            phrases.append("людей много — внимания мало")
        elif face_count > 1:
            phrases.append("компания дружная, но нервы у камеры на пределе")
        
        # Если есть текст — упомянуть без цитирования
        if analysis.get('text'):
            extra = [
                "надпись уверенно делает вид, что так и задумано",
                "текст обещает больше, чем реальность",
                "подпись старается звучать умно — пусть так и будет",
                "слова в кадре громкие, выводы — тише"
            ]
            phrases.append(self._pick_variant(extra, seed, 101))
        
        # Если найдены объекты/метки — намекнуть на насыщенность
        has_objects = bool(analysis.get('objects'))
        has_labels = bool(analysis.get('labels'))
        if has_objects and has_labels:
            phrases.append("в кадре деталей достаточно, осталось навести на смысл")
        elif has_objects:
            phrases.append("предметов хватает — а вот идеи бы добавить")
        elif has_labels:
            phrases.append("настроение считывается, даже если ты его не планировал")
        
        # Слегка перемешать и сократить до 1-2 фраз
        if phrases:
            import random
            rnd = random.Random(seed + 313)
            rnd.shuffle(phrases)
            return ' '.join(phrases[:2])
        return ""
    
    def get_analysis_details(self, analysis: Dict[str, Any]) -> str:
        """Возвращает детали анализа для комментария"""
        
        details = []
        
        # Метки
        if analysis.get('labels'):
            top_labels = [label['description'] for label in analysis['labels'][:3]]
            details.append(f"Вижу: {', '.join(top_labels)}")
        
        # Лица
        if analysis.get('faces'):
            face_count = len(analysis['faces'])
            if face_count == 1:
                details.append("Одно лицо на фото")
            else:
                details.append(f"{face_count} лиц на фото")
        
        # Текст
        if analysis.get('text'):
            text_preview = analysis['text'][0][:50] + "..." if len(analysis['text'][0]) > 50 else analysis['text'][0]
            details.append(f"Текст: '{text_preview}'")
        
        # Объекты
        if analysis.get('objects'):
            objects = [obj['name'] for obj in analysis['objects'][:3]]
            details.append(f"Объекты: {', '.join(objects)}")
        
        return " | ".join(details) if details else ""
