#!/usr/bin/env python3
"""MAIN: Web Scraper вакансий HH.ru + Pandas анализ"""
print("Запускается Web Scraper вакансий...")

from scraper import scrape_hh_vacancies
from analyze import analyze_vacancies

def main():
    print("Сбор вакансий...")
    # Собираем данные в DataFrame
    df = scrape_hh_vacancies("Python", "Казань", 10)

    # СОХРАНЯЕМ сырые данные в CSV файл
    csv_file = "vacancies_raw.csv"
    df.to_csv(csv_file, index = False)  # index = False - не сохраняем номера строк
    print(f"Сохранено {len(df)} вакансий в {csv_file}")

    print("Анализируются данные...")

    analyze_vacancies(csv_file)
    # analysis_df.to_csv("final_analysis.csv", index = False)

    print("Сохранены файлы:")
    print("- vacancies_raw.csv (сырые данные)")
    print("- vacancies_clean.csv (очищенные)")
    print("- analysis_summary.csv (статистика)")

if __name__ == "__main__":
    main()


