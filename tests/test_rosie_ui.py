import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
ROSIE = ROOT / "public_sites" / "rosie" / "index.html"


def _page():
    return ROSIE.read_text(encoding="utf-8")


def test_estate_filter_counts_are_derived_from_cards_and_handlers_are_wired():
    page = _page()
    cards = re.findall(r'class="estate-card"[^>]*data-category="([^"]+)"', page)
    assert len(cards) == 6
    assert page.count('class="filter-pill') == 4
    assert 'function updateEstateFilterCounts()' in page
    assert 'updateEstateFilterCounts();' in page
    assert 'const estateCards = document.querySelectorAll(\'.estate-card\');' in page
    assert 'const cards = estateCards;' in page
    assert 'data-label="All Estates"' in page
    assert 'All Estates (5)' not in page
    assert 'onclick="openEstateModal(' in page
    assert 'window.openEstateModal = function(estateId)' in page
    assert 'estateNextBtn.addEventListener' in page
    assert 'estatePrevBtn.addEventListener' in page
    assert 'btn.addEventListener(\'click\'' in page


@pytest.mark.skipif(__import__("importlib").util.find_spec("playwright") is None, reason="playwright unavailable")
def test_estate_filter_counts_match_visible_cards_in_browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(ROSIE.as_uri(), wait_until="domcontentloaded")

        def visible_cards():
            return page.locator(".estate-card:visible").count()

        def chip_count(filter_name):
            text = page.locator(f'.filter-pill[data-filter="{filter_name}"]').inner_text()
            return int(re.search(r"\((\d+)\)", text).group(1))

        assert visible_cards() == chip_count("all") == 6
        assert chip_count("for_sale") == 3
        assert chip_count("under_contract") == 1
        assert chip_count("sold") == 2

        for filter_name in ("for_sale", "under_contract", "sold", "all"):
            page.locator(f'.filter-pill[data-filter="{filter_name}"]').click()
            page.wait_for_timeout(300)
            assert chip_count("all") == visible_cards()

        page.locator('.estate-card[data-id="estate-pelican-sound"]').click()
        assert page.locator("#estateModal").evaluate("el => el.classList.contains('is-active')")
        page.locator("#closeEstateModalBtn").click()
        assert not page.locator("#estateModal").evaluate("el => el.classList.contains('is-active')")
        browser.close()