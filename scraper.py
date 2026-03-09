import re
import pandas as pd  # Для создания DataFrame (таблицы)
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def scrape_hh_vacancies(vacancy_name: str, city: str, max_pages: int):
    """
    Собирает вакансии с HH.ru и возвращает таблицу pandas
    Аргументы:
    - vacancy_name: что ищем (например: "Python junior" или "QA automation")
    - city: город
    - max_pages: сколько страниц парсим (1 страница = ~50 вакансий)
    """

    # Создаём настройки Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")             # Chrome без GUI
    chrome_options.add_argument("--no-sandbox")               # Для стабильности, убираем песочницу
    chrome_options.add_argument("--disable-dev-shm-usage")    # "Не проверяй память!"
    chrome_options.add_argument("--disable-gpu")              # Отключаем GPU
    chrome_options.add_argument("--window-size=1920,1080")    # Размер окна
    chrome_options.add_argument("--disable-extensions")       # Без расширений
    chrome_options.add_argument("--disable-logging")          # Без логов
    chrome_options.add_argument("--silent")                   # Тишина

    # Скачиваем ChromeDriver автоматически и запускаем браузер
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service = service, options = chrome_options)

    vacancies = []  # Пустой список для всех вакансий
    wait = WebDriverWait(browser, 10)  # Ждём до 10 сек появления элементов

    city_area_codes = {
        "Москва": 1,
        "Санкт-Петербург": 2,
        "Казань": 88,
        "Нижнекамск": 1642,
        "Елабуга": 1633,
        "Нижний Новгород": 66,
        "Бугульма": 1631,
        "Набережные Челны": 1641,
        "Зеленодольск": 1635
    }

    try:
        # Формируем URL поиска HH.ru с кодом региона
        area_code = city_area_codes.get(city, 1624) # 1624 - весь Татарстан
        base_url = f"https://hh.ru/search/vacancy?text={vacancy_name.replace(' ', '+')}&area={area_code}"
        print(f"🔍 Ищем: вакансии {vacancy_name} в г.{city}")

        for page in range(max_pages):
            try:
                print(f"📄 Парсим страницу {page + 1}...")
                browser.get(f"{base_url}&page={page}")

                # Ждём появления блоков с вакансиями на странице
                vacancy_blocks = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy"]')))

                # 🔥 ПРОВЕРКА: страница пуста?
                if not vacancy_blocks:  # len(vacancy_blocks) == 0
                    print(f"⚠️  Страница {page} пуста — больше вакансий нет!")
                    break

                print(f"✅ {len(vacancy_blocks)} вакансий на стр. {page + 1}")

        # for page in range(max_pages):
        #     print(f"📄 Парсим страницу {page + 1}...")
        #     browser.get(f"{base_url}&page={page}")
        #     time.sleep(2)
        #
        #     # Ждём появления блоков с вакансиями на странице
        #     vacancy_blocks = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-qa="vacancy-serp__vacancy"]')))

            # Проходим по каждому блоку с вакансией на странице
                for block in vacancy_blocks:
                    try:
                        # Название вакансии и ссылка
                        title_elem = block.find_element(By.CSS_SELECTOR, "[data-qa='serp-item__title-text']")
                        title = title_elem.text

                        # Ссылка на вакансию
                        vacancy_link = block.find_element(By.CSS_SELECTOR, "a.magritte-link___b4rEM_7-1-5")
                        vacancy_url = vacancy_link.get_attribute("href")

                        # Компания
                        company_elem = block.find_element(By.CSS_SELECTOR, "[data-qa='vacancy-serp__vacancy-employer-text']")
                        company = company_elem.text

                        # Зарплата
                        salary = "Не указана"

                        # Не во всех блоках в нужном месте указана зарплата, ищем все текстовые элементы в блоке вакансии
                        text_elements = block.find_elements(By.XPATH, ".//*[text()]")

                        for elem in text_elements:
                            try:
                                elem_text = elem.text.strip()

                                # Ищем числа + ₽/$ в тексте элемента
                                salary_match = re.search(r'(\d[\d\s,]*[₽$])', elem_text)

                                if salary_match:
                                    salary_raw = salary_match.group(1)

                                    # Очистка: пробелы → один пробел, убираем запятые
                                    salary_clean = re.sub(r'[  ,]+', ' ', salary_raw).strip()
                                    salary = salary_clean
                                    break

                            except (StaleElementReferenceException, AttributeError):  # Например, если elem.text = None
                                continue
                            except Exception as e:  # Ловим другие исключения, если они возникнут
                                print(f'Произошла ошибка: {e}')
                                continue

                        # print(f"💰 {salary}")  # Для проверки

                    except Exception as e:
                        print(f"❌ Ошибка вакансии: {e}")
                        title = "Неизвестно"
                        company = "Неизвестно"
                        salary = "Не указана"  # ← Безопасное значение!
                        vacancy_url = "Не найден"

                    # Сохраняем данные
                    vacancy_data = {
                        "title": title,
                        "company": company,
                        "salary": salary,
                        "url": vacancy_url
                    }
                    vacancies.append(vacancy_data)

            except TimeoutException:
                print(f"⏰ Таймаут на странице {page + 1}, нет вакансий")
                break  # Выходим из цикла

    finally:
        browser.quit()

    # Превращаем список словарей в таблицу pandas
    vacancies_df = pd.DataFrame(vacancies)
    print(f"✅ Собрано {len(vacancies_df)} вакансий!")
    return vacancies_df

if __name__ == "__main__":
    # Тест: собираем вакансии
    df = scrape_hh_vacancies("Python", "Казань", 3)
    df.to_csv("vacancies_raw.csv", index = False)  # Сохраняем сырые данные
