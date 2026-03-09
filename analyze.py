import pandas as pd
import re  # 📚 Библиотека для поиска чисел в тексте

def parse_salary(salary_text):
    """ Вытаскивает ЧИСЛО из текста зарплаты
    'от 100 000 ₽' → 100000 (int)
    'Не указана' → None"""

    if salary_text == "Не указана":
        return None

    # Ищем ВСЕ цифры подряд: 100000₽ → ['100000']
    numbers = re.findall(r'\d+', salary_text.replace(' ', ''))  # Убираем пробелы

    if not numbers:
        return None

    # Берём ПЕРВОЕ число (начало диапазона 'от 100к до 150к')
    return int(numbers[0])  # Преобразуем строку → число

def analyze_vacancies(csv_file = "vacancies_raw.csv"):
    """Анализирует CSV файл с вакансиями:
    - Средняя ЗП, топ компании
    - Создаёт отчёты: vacancies_clean.csv + analysis_summary.csv"""

    print(f"Читаем файл: {csv_file}")

    # Читаем CSV → таблица (DataFrame)
    df = pd.read_csv(csv_file)
    print(f"Найдено {len(df)} вакансий")

    # 💰 Очищаем зарплату: '100 000 ₽' → 100000
    df['salary_numeric'] = df['salary'].apply(parse_salary)  # НОВЫЙ столбец

    # Считаем статистику ЗП (только где есть числа)
    valid_salaries = df['salary_numeric'].dropna()  # Убираем None

    if len(valid_salaries) > 0:
        avg_salary = valid_salaries.mean()
        salary_stats = valid_salaries.describe()

        print("\nСТАТИСТИКА ЗАРПЛАТ")
        print(f"  Средняя ЗП: {avg_salary:,.0f} ₽")
        print(f"  Медиана:    {salary_stats['50%']:,.0f} ₽")
        print(f"  Минимум:    {salary_stats['min']:,.0f} ₽")
        print(f"  Максимум:   {salary_stats['max']:,.0f} ₽")
    else:
        print("Зарплаты не найдены!")
        avg_salary = 0


    print("\nТоп-10 компаний по количеству вакансий")
    top_companies = df['company'].value_counts().head(10)
    print(top_companies)

    # Сохранение отчета
    # 1. Общая статистика в JSON-подобный словарь
    analysis = {
        'total_vacancies': len(df),
        'avg_salary': float(avg_salary),  # Pandas требует float
        'companies': top_companies.to_dict(),
        'vacancies_with_salary': len(valid_salaries)
    }
    pd.DataFrame([analysis]).to_csv("analysis_summary.csv", index = False)

    # 2. Очищенная таблица с новой колонкой зарплаты
    df.to_csv("vacancies_clean.csv", index = False)

    print("Файлы созданы:")
    print("  • vacancies_clean.csv")
    print("  • analysis_summary.csv")

    return df  # Возвращаем изменённую таблицу

if __name__ == "__main__":
    # Тест: запуск без параметров
    analyze_vacancies()

