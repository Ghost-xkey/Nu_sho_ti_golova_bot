import random
import re
from typing import List, Dict, Optional


class ChastushkaGenerator:
    """Генератор саркастических частушек в стиле Гриши"""
    
    def __init__(self):
        self.toxicity_levels = {
            0: "мягкий", 1: "средний", 2: "острый", 3: "яд"
        }
        
        # Базовые шаблоны частушек
        self.chastushka_templates = [
            # Про жизнь
            "Жизнь как зебра — полосатая,\n{target} как {comparison},\n{action} — дело святое,\n{result} — вот это да!",
            
            "На работе {work_situation},\n{target} {work_action},\n{result} — не беда,\n{philosophy} — всегда!",
            
            # Про отношения
            "Любовь как {love_comparison},\n{target} {love_action},\n{result} — не проблема,\n{philosophy} — тема!",
            
            # Про деньги
            "Деньги {money_situation},\n{target} {money_action},\n{result} — не вопрос,\n{philosophy} — вопрос!",
            
            # Про здоровье
            "Здоровье {health_situation},\n{target} {health_action},\n{result} — не беда,\n{philosophy} — всегда!",
            
            # Про технологии
            "Технологии {tech_situation},\n{target} {tech_action},\n{result} — не проблема,\n{philosophy} — тема!",
        ]
        
        # Словари для заполнения шаблонов
        self.targets = [
            "ты", "он", "она", "мы", "вы", "они", "все", "никто", "каждый", "любой"
        ]
        
        self.comparisons = [
            "как старая батарейка", "как сломанный будильник", "как пустой кошелек", 
            "как дырявый зонт", "как сгоревшая лампочка", "как ржавый гвоздь",
            "как прокисшее молоко", "как увядший цветок", "как сдувшийся шарик"
        ]
        
        self.work_situations = [
            "как на каторге", "как в тюрьме", "как в аду", "как в кошмаре",
            "как в ловушке", "как в клетке", "как в болоте", "как в тупике"
        ]
        
        self.work_actions = [
            "трудишься как пчелка", "пашешь как лошадь", "вкалываешь как раб",
            "работаешь как вол", "трудишься как муравей", "пашешь как трактор"
        ]
        
        self.love_comparisons = [
            "как роза с шипами", "как мед с ядом", "как солнце с тучами",
            "как радуга с дождем", "как огонь с водой", "как лед с пламенем"
        ]
        
        self.love_actions = [
            "влюбляешься как дурак", "страдаешь как романтик", "мечтаешь как поэт",
            "страдаешь как герой", "влюбляешься как подросток", "мечтаешь как идеалист"
        ]
        
        self.money_situations = [
            "как вода в песок", "как дым в небо", "как снег на солнце",
            "как песок сквозь пальцы", "как ветер в поле", "как дождь в море"
        ]
        
        self.money_actions = [
            "тратишь как миллионер", "считаешь как бухгалтер", "экономишь как скряга",
            "тратишь как транжира", "считаешь как банкир", "экономишь как мышь"
        ]
        
        self.health_situations = [
            "как хрупкий фарфор", "как тонкая нить", "как стеклянный шар",
            "как бумажный кораблик", "как мыльный пузырь", "как песочный замок"
        ]
        
        self.health_actions = [
            "заботишься как врач", "лечишься как пациент", "бережешь как сокровище",
            "заботишься как мать", "лечишься как больной", "бережешь как реликвию"
        ]
        
        self.tech_situations = [
            "как вирус в системе", "как баг в программе", "как глюк в игре",
            "как ошибка в коде", "как сбой в сети", "как зависание компьютера"
        ]
        
        self.tech_actions = [
            "разбираешься как хакер", "используешь как юзер", "настраиваешь как админ",
            "разбираешься как программист", "используешь как новичок", "настраиваешь как мастер"
        ]
        
        self.actions = [
            "жить", "работать", "любить", "мечтать", "страдать", "радоваться",
            "грустить", "смеяться", "плакать", "думать", "говорить", "молчать"
        ]
        
        self.results = [
            "получилось", "не получилось", "вышло", "не вышло", "сработало", "не сработало",
            "удалось", "не удалось", "повезло", "не повезло", "получилось", "не получилось"
        ]
        
        self.philosophies = [
            "главное — не сдаваться", "все будет хорошо", "время лечит", "жизнь продолжается",
            "все проходит", "надежда умирает последней", "терпение и труд все перетрут",
            "что не убивает — делает сильнее", "все к лучшему", "все имеет свой смысл"
        ]
        
        # Токсичные фразы для разных уровней
        self.toxic_phrases = {
            0: [],  # Мягкий - без токсичности
            1: ["но ты все равно дурак", "но ты не понимаешь", "но ты не умеешь"],
            2: ["а ты как всегда тупой", "а ты как обычно глупый", "а ты как всегда неудачник"],
            3: ["ты полный идиот", "ты абсолютный дебил", "ты тупой как пробка", "ты глупый как валенок"]
        }
        
        # Матерные слова (опционально)
        self.profanity_words = [
            "блин", "черт", "елки-палки", "японский городовой", "твою мать",
            "блин", "черт возьми", "елки-палки", "японский городовой"
        ]

    def generate_chastushka(self, topic: str, toxicity: int = 1, use_profanity: bool = False) -> str:
        """
        Генерирует частушку на заданную тему
        
        Args:
            topic: Тема для частушки
            toxicity: Уровень токсичности (0-3)
            use_profanity: Использовать ли мат
            
        Returns:
            Сгенерированная частушка
        """
        # Выбираем случайный шаблон
        template = random.choice(self.chastushka_templates)
        
        # Заполняем шаблон
        chastushka = self._fill_template(template, topic, toxicity, use_profanity)
        
        # Добавляем токсичность если нужно
        if toxicity > 0 and random.random() < 0.3:  # 30% шанс добавить токсичную фразу
            toxic_phrase = random.choice(self.toxic_phrases[toxicity])
            chastushka += f"\n{toxic_phrase}"
        
        return chastushka

    def _fill_template(self, template: str, topic: str, toxicity: int, use_profanity: bool) -> str:
        """Заполняет шаблон частушки"""
        # Базовые замены
        replacements = {
            'target': random.choice(self.targets),
            'comparison': random.choice(self.comparisons),
            'action': random.choice(self.actions),
            'result': random.choice(self.results),
            'philosophy': random.choice(self.philosophies),
            'work_situation': random.choice(self.work_situations),
            'work_action': random.choice(self.work_actions),
            'love_comparison': random.choice(self.love_comparisons),
            'love_action': random.choice(self.love_actions),
            'money_situation': random.choice(self.money_situations),
            'money_action': random.choice(self.money_actions),
            'health_situation': random.choice(self.health_situations),
            'health_action': random.choice(self.health_actions),
            'tech_situation': random.choice(self.tech_situations),
            'tech_action': random.choice(self.tech_actions),
        }
        
        # Применяем замены
        result = template
        for key, value in replacements.items():
            result = result.replace(f'{{{key}}}', value)
        
        # Добавляем тему если есть
        if topic:
            result = self._incorporate_topic(result, topic)
        
        # Добавляем мат если нужно
        if use_profanity and random.random() < 0.2:  # 20% шанс
            profanity = random.choice(self.profanity_words)
            result = result.replace("блин", profanity)
        
        return result

    def _incorporate_topic(self, text: str, topic: str) -> str:
        """Включает тему в текст частушки"""
        # Простые замены для популярных тем
        topic_replacements = {
            'работа': ['на работе', 'в офисе', 'на службе'],
            'деньги': ['с деньгами', 'с финансами', 'с бюджетом'],
            'любовь': ['в любви', 'с чувствами', 'в отношениях'],
            'здоровье': ['со здоровьем', 'с самочувствием', 'с организмом'],
            'технологии': ['с техникой', 'с гаджетами', 'с интернетом'],
            'погода': ['с погодой', 'с климатом', 'с природой'],
            'политика': ['с политикой', 'с властью', 'с государством'],
            'спорт': ['со спортом', 'с тренировками', 'с фитнесом'],
        }
        
        topic_lower = topic.lower()
        for key, replacements in topic_replacements.items():
            if key in topic_lower:
                replacement = random.choice(replacements)
                # Заменяем первое подходящее место
                text = text.replace('в жизни', replacement, 1)
                break
        
        return text

    def get_random_chastushka(self) -> str:
        """Возвращает случайную частушку"""
        topics = ['работа', 'деньги', 'любовь', 'здоровье', 'технологии', 'погода']
        topic = random.choice(topics)
        toxicity = random.randint(0, 2)
        return self.generate_chastushka(topic, toxicity, use_profanity=False)


# Пример использования
if __name__ == "__main__":
    generator = ChastushkaGenerator()
    
    print("=== Примеры частушек ===")
    print("\n1. Мягкая частушка:")
    print(generator.generate_chastushka("работа", toxicity=0))
    
    print("\n2. Средняя токсичность:")
    print(generator.generate_chastushka("деньги", toxicity=1))
    
    print("\n3. Острая токсичность:")
    print(generator.generate_chastushka("любовь", toxicity=2))
    
    print("\n4. Случайная частушка:")
    print(generator.get_random_chastushka())
