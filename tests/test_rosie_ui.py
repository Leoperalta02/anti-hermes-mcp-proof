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


def test_production_index_does_not_expose_prototype_portal_surface():
    page = _page()
    assert not re.search(r'href=["\'](?:\./)?portal\.html(?:["\'#?])', page, re.IGNORECASE)
    assert "Executive Client Portal" not in page


def test_ui_handlers_referenced_by_markup_have_live_definitions():
    page = _page()
    inline_handlers = re.findall(r'\bon(?:click|input|change|submit)="([^"]+)"', page)
    referenced = {
        name
        for handler in inline_handlers
        for name in re.findall(r'(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(', handler)
        if name not in {"stopPropagation", "getElementById", "querySelectorAll", "forEach", "rgba", "var"}
    }
    function_defs = set(re.findall(r'function\s+([A-Za-z_$][\w$]*)\s*\(', page))
    window_defs = set(re.findall(r'window\.([A-Za-z_$][\w$]*)\s*=\s*function', page))
    assert referenced <= function_defs | window_defs


def test_filter_pills_do_not_ship_stale_hardcoded_counts():
    page = _page()
    pills = re.findall(r'<button class="filter-pill[^>]*>(.*?)</button>', page)
    assert len(pills) == 4
    assert all(re.search(r'\(\d+\)', pill) is None for pill in pills)


@pytest.mark.skipif(__import__("importlib").util.find_spec("playwright") is None, reason="playwright unavailable")
def test_estate_filter_counts_match_visible_cards_in_browser():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                pytest.skip(f"Chromium binary not available on this host: {e}")
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