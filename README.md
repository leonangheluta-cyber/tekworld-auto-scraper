# Tekworld Price & Catalogue Monitor

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-web%20scraping-60A839?logo=scrapy&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-data%20processing-150458?logo=pandas&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-scheduled%20automation-2088FF?logo=githubactions&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram-delivery%20%26%20alerts-26A5E4?logo=telegram&logoColor=white)
![Status](https://img.shields.io/badge/status-completed-brightgreen)

A fully automated pipeline that crawls a multi-category appliance catalog every day and delivers a ready-to-use Excel report straight to Telegram — no server to maintain, no manual export, no one checking pages by hand.

This project simulates a real business need: keeping track of a competitor's or supplier's catalog (pricing, availability, technical specs) over time, automatically. Built on **tekworld.it**, an Italian appliance retailer, it collects and processes data across five categories — washing machines, fridges, dishwashers, hoods and kitchens.

## Why this matters for a business

Manually checking a catalog for price changes, stock updates or new listings doesn't scale, and by the time someone gets around to it the data is already stale. This pipeline runs the whole cycle unattended, every day:

- **Time saved**: the full catalog is re-scraped and re-packaged on a schedule, replacing hours of manual browsing and copy-pasting.
- **Always current**: a fresh report lands automatically, with no one having to remember to run anything.
- **Delivered where you'll see it**: the finished Excel file is pushed to Telegram the moment it's ready — no dashboard to log into.
- **Self-monitoring**: if something breaks (a page structure changes, a field stops being found), a Telegram alert fires so the issue doesn't go unnoticed for days.
- **Extensible**: the same approach adapts to any multi-category e-commerce site, and to a specific competitor or product range on request.

## What it does

1. **Scrape** — a two-level Scrapy spider crawls all 5 categories in a single run: category listing pages (with pagination) → individual product pages, extracting common fields (name, item code, price, availability, energy efficiency class) plus category-specific technical specs (dimensions, capacity, cycle programs, energy/water consumption, etc.).
2. **Verify the technical labels** — each category exposes a different set of spec rows on the site (a washing machine has "Spin speed", a fridge has "Number of shelves"). The label set kept for each category (`labels.py`) was determined by crawling a full sample of real products per category and comparing the resulting label sets, to rule out typos or inconsistent variants before they became columns.
3. **Convert & split** — the raw CSV is turned into a single `.xlsx` file with **one sheet per category**, dropping columns that are entirely empty for that category so each sheet only shows what's relevant.
4. **Schedule & deliver** — a GitHub Actions workflow runs the whole pipeline daily and sends the finished Excel file directly to a Telegram chat, plus keeps it as a downloadable workflow artifact.

## Project structure

```
tekworld/
├── tekworld/
│   ├── spiders/
│   │   ├── tek_file.py      # main spider: crawl + parse logic
│   │   └── labels.py        # per-category technical label sets (verified against real data)
│   └── settings.py          # Scrapy settings, incl. FEED_EXPORT_FIELDS
├── saving_to_excel.ipynb    # converts the raw CSV into the final multi-sheet .xlsx
├── requirements.txt
└── .github/workflows/scraper.yaml   # daily scheduled run
```

## Note on data

The scraper respects `robots.txt` and only collects data already published on the site's own product pages. A sample of the final report is included as `sample_output.xlsx` to show the data structure.

## Tech stack

Python, Scrapy, pandas, openpyxl, GitHub Actions, Telegram Bot API

## How to run

```bash
pip install -r requirements.txt
```

Set `TELEGRAM_BOT` and `CHAT_ID` as environment variables (or GitHub Secrets, for the scheduled workflow) — the bot token and chat ID used to deliver the report and send alerts.

```bash
scrapy crawl tek_file -o outputs/tekworld_output.csv
jupyter nbconvert --to notebook --execute saving_to_excel.ipynb
```

The scheduled workflow (`.github/workflows/scraper.yaml`) runs the same two steps automatically, currently daily at `30 9 * * *` UTC.
