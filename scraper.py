from urllib.parse import quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


NEWS_SOURCE = "Ars Technica"
BASE_URL = "https://arstechnica.com/"
SEARCH_URL = "https://arstechnica.com/search/?q="


def create_driver():
    options = Options()
    options.binary_location = "/usr/bin/chromium"

    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1365,900")

    service = Service("/usr/bin/chromedriver")

    return webdriver.Chrome(
        service=service,
        options=options
    )


def get_first_article(keyword):
    driver = create_driver()

    try:
        driver.set_page_load_timeout(40)
        driver.get(SEARCH_URL + quote_plus(keyword))

        wait = WebDriverWait(driver, 25)

        wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        links = driver.find_elements(
            By.CSS_SELECTOR,
            'a[href*="arstechnica.com/"]'
        )

        article_url = None

        for link in links:
            href = link.get_attribute("href") or ""

            if (
                href.startswith(BASE_URL)
                and href.rstrip("/") != BASE_URL.rstrip("/")
                and "/search/" not in href
                and "/about/" not in href
                and "/civis/" not in href
                and link.text.strip()
            ):
                article_url = href
                break

        if not article_url:
            raise RuntimeError(
                "No article found. Check the search page URL "
                "and its HTML selectors."
            )

        driver.get(article_url)

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "article")
                )
            )
        except TimeoutException:
            raise RuntimeError(
                "The article content did not load."
            )

        paragraphs = driver.find_elements(
            By.CSS_SELECTOR,
            "article p"
        )

        article_text = "\n".join(
            paragraph.text.strip()
            for paragraph in paragraphs
            if paragraph.text.strip()
        )

        if not article_text:
            raise RuntimeError(
                "Article found, but no paragraph text was extracted."
            )

        return {
            "newssource": NEWS_SOURCE,
            "url": article_url,
            "article_text": article_text
        }

    finally:
        driver.quit()
