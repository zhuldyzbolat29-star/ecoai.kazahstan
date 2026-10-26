"""Небольшой веб-поиск для раздела предприятий."""


from __future__ import annotations

from urllib.parse import quote
from urllib.request import Request, urlopen
from email.utils import parsedate_to_datetime
import xml.etree.ElementTree as ET


class SearchError(RuntimeError):
    """Ошибка получения результатов из внешнего поискового сервиса."""


def search_enterprise(
    plant: str,
    city: str,
    limit: int = 12,
) -> list[dict[str, str]]:
    """Ищет информацию о предприятии и его экологическом воздействии."""

    plant = plant.strip()
    city = city.strip()

    if not plant or not city:
        return []

    searches = [
        (
            "Деятельность и продукция",
            f'"{plant}" "{city}" Казахстан завод производство продукция',
        ),
        (
            "Поставщики, история и достижения",
            f'"{plant}" Казахстан поставщики партнёры история',
        ),
        (
            "Выбросы и жалобы жителей",
            f'"{plant}" "{city}" Казахстан выбросы дым запах серы '
            "жалобы жителей загрязнение воздуха",
        ),
        (
            "Нарушения, проверки и штрафы",
            f'"{plant}" "{city}" Казахстан экологический штраф проверка '
            "нарушения предписание превышение выбросов",
        ),
        (
            "Отходы и экологические отчёты",
            f'"{plant}" "{city}" Казахстан фосфогипс химические отходы '
            "экологический отчёт оценка воздействия окружающую среду",
        ),
    ]

    results: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    category_limit = max(2, limit // len(searches))

    for category, query in searches:
        rss_url = (
            "https://news.google.com/rss/search?q="
            + quote(query)
            + "&hl=ru&gl=KZ&ceid=KZ:ru"
        )

        category_count = 0

        try:
            request = Request(
                rss_url,
                headers={"User-Agent": "Mozilla/5.0"},
            )

            with urlopen(request, timeout=15) as response:
                xml_data = response.read()

            root = ET.fromstring(xml_data)

        except Exception:
            continue

        for item in root.findall("./channel/item"):
            title = item.findtext(
                "title",
                default="Без названия",
            ).strip()
            url = item.findtext("link", default="").strip()
            description = item.findtext(
                "description",
                default="",
            )
            date = item.findtext("pubDate", default="").strip()

            if not url or url in seen_urls:
                continue

            text_to_check = f"{title} {description}".lower()
            plant_words = plant.lower().split()
            city_lower = city.lower()

            mentions_plant = any(
                word in text_to_check
                for word in plant_words
                if len(word) > 2
            )
            mentions_city = city_lower in text_to_check

            if not mentions_plant:
                continue

            
            seen_urls.add(url)

            results.append({
                "title": title,
                "url": url,
                "snippet": description,
                "source": "Google News RSS",
                "date": date,
                "category": category,
            })

            category_count += 1

            if category_count >= category_limit:
                break
    results.sort(
        key=lambda item: parsedate_to_datetime(item["date"]) if item.get("date") else ёёёparsedate_to_datetime("Thu, 01 Jan 1970 00:00:00 +0000"),
        reverse=True,
    )
    return results[:limit]