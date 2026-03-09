#!/usr/bin/env python3
"""🚀 MAIN: Web Scraper вакансий HH.ru + Pandas анализ"""
print("🤖 Запускаю Web Scraper вакансий...")

from scraper import scrape_hh_vacancies  # Импорт "рук" (Selenium)
from analyze import analyze_vacancies    # Импорт "мозга" (Pandas)

def main():
    print("1️⃣ Собираю вакансии...")
    # Собираем данные в DataFrame
    df = scrape_hh_vacancies("Python", "Казань", 10)

    # СОХРАНЯЕМ сырые данные в CSV файл
    csv_file = "vacancies_raw.csv"
    df.to_csv(csv_file, index = False)  # index = False - не сохраняем номера строк
    print(f"💾 Сохранено {len(df)} вакансий в {csv_file}")

    print("2️⃣ Анализирую...")

    analyze_vacancies(csv_file)
    # analysis_df.to_csv("final_analysis.csv", index = False)

    print("Выполнено! Проверь файлы:")
    print("- vacancies_raw.csv (сырые данные)")
    print("- vacancies_clean.csv (очищенные)")
    print("- analysis_summary.csv (статистика)")

if __name__ == "__main__":
    main()


