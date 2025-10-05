# backend/scraper.py
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_driver():
    options = Options()
    # use headless for server; change/remove for debugging in dev
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    # prevent some simple detections
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    # small implicit wait
    driver.implicitly_wait(2)
    return driver


def scrape_amazon(product_name, limit=20):
    """
    Returns list of review texts from Amazon.in for the first matching product.
    May return fewer than limit if site blocks or not enough reviews.
    """
    driver = get_driver()
    reviews = []
    try:
        q = product_name.replace(" ", "+")
        search_url = f"https://www.amazon.in/s?k={q}"
        driver.get(search_url)

        # click the first product link (multiple possible selectors)
        try:
            first = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.a-link-normal.s-no-outline, a.a-link-normal.s-link-style"))
            )
            first.click()
        except Exception:
            # fallback: try other link forms
            els = driver.find_elements(By.CSS_SELECTOR, "h2 a.a-link-normal")
            if els:
                els[0].click()
            else:
                return reviews  # nothing we can click

        # ensure new tab
        try:
            WebDriverWait(driver, 8).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        # click "See all reviews" if present
        try:
            rlink = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "See all reviews"))
            )
            rlink.click()
        except Exception:
            # not present — we'll try to read reviews from product page directly
            pass

        # paginate and collect
        while len(reviews) < limit:
            time.sleep(1.2)
            blocks = driver.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body'], div.review-text-content span")
            for b in blocks:
                if len(reviews) >= limit:
                    break
                text = b.text.strip()
                if text and text not in reviews:
                    reviews.append(text)

            # try click next page in reviews
            try:
                nxt = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
                if nxt and nxt.is_displayed():
                    nxt.click()
                    time.sleep(1.2)
                    continue
            except Exception:
                break

    except Exception as e:
        print("Amazon scrape error:", e)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return reviews[:limit]


def scrape_flipkart(product_name, limit=20):
    """
    Returns list of review texts from Flipkart for the first matching product.
    """
    driver = get_driver()
    reviews = []
    try:
        q = product_name.replace(" ", "+")
        search_url = f"https://www.flipkart.com/search?q={q}"
        driver.get(search_url)

        # close any login modal if present (Flipkart shows it sometimes)
        try:
            close_btn = driver.find_element(By.CSS_SELECTOR, "button._2KpZ6l._2doB4z")
            if close_btn:
                close_btn.click()
        except Exception:
            pass

        # click first product (several possible selectors)
        try:
            first = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a._1fQZEK, a.s1Q9rs, a.IRpwTa"))
            )
            first.click()
        except Exception:
            # fallback: other link styles
            links = driver.find_elements(By.CSS_SELECTOR, "a._2rpwqI")
            if links:
                links[0].click()
            else:
                return reviews

        # switch to product tab
        try:
            WebDriverWait(driver, 8).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[-1])
        except Exception:
            pass

        # attempt to open all reviews (Flipkart sometimes has a link)
        # scroll so reviews load
        while len(reviews) < limit:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(1)

            blocks = driver.find_elements(By.CSS_SELECTOR, "div.t-ZTKy, div._6K-7Co, div._16HD7q")
            for b in blocks:
                if len(reviews) >= limit:
                    break
                text = b.text.strip()
                if text and text not in reviews:
                    reviews.append(text)

            # try to click 'Next' for review pages (if present)
            try:
                nxt = driver.find_element(By.CSS_SELECTOR, "a._1LKTO3, a._1LKTO3._3w3zqR")
                if nxt and "Next" in nxt.text:
                    nxt.click()
                    time.sleep(1)
                    continue
            except Exception:
                break

    except Exception as e:
        print("Flipkart scrape error:", e)
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    return reviews[:limit]


# quick local test guard
if __name__ == "__main__":
    print("Amazon sample:", scrape_amazon("poco x3", 5))
    print("Flipkart sample:", scrape_flipkart("poco x3", 5))
