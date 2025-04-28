import asyncio
from playwright.async_api import async_playwright
from utils import block_scripts, broadcast_message, get_updates, load_listings, safe_goto, save_listings
import random
from playwright_stealth import stealth_async

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.129 Safari/537.36",
    # (you can add more real user-agents here)
]

# The page to scrape
URL_BOUWINVEST = "https://www.wonenbijbouwinvest.nl/huuraanbod?query=Utrecht&range=15&price=1000-1500&showAvailable=false&page=1&seniorservice=false&order=recent"
URL_FUNDA = "https://www.funda.nl/zoeken/huur?selected_area=[%22provincie-utrecht%22]&price=%22900-1500%22&publication_date=%221%22&availability=[%22available%22]&rooms=%222-%22&sort=%22date_down%22"

async def repeat_crawl():
    print('Crawler start')
    while True:
        try:
            await main()
        except Exception as e:
            print(f"Error during crawl: {e}")
        await asyncio.sleep(30)

async def main():
    print('Fetching..')
    # sync telegram users
    await get_updates()

    old_listings = load_listings()
    current_listings = set()

    # BOUWINVEST CRAWLING
    # async with async_playwright() as p:
    #     random_user_agent = random.choice(USER_AGENTS)

    #     browser = await p.chromium.launch(
    #         headless=True,
    #         args=[
    #         "--no-sandbox",
    #         "--disable-setuid-sandbox",
    #         "--disable-blink-features=AutomationControlled"
    #     ],)

    #     context = await browser.new_context(
    #         user_agent=random_user_agent, 
    #         viewport={"width": 1920, "height": 1080},
    #         locale="en-US"
    #     )

    #     page = await context.new_page()
    #     await safe_goto(page, URL_BOUWINVEST)

    #     while True:
    #         # --- Scrape current page ---
    #         listings = await page.query_selector_all(".projectproperty-tile > a")

    #         for listing in listings:
    #             link = await listing.get_attribute("href")
    #             listing_text = f"{link}"
    #             current_listings.add(listing_text)

    #         # --- Try to find "Next" button ---
    #         next_button = await page.query_selector(".pagination__next")

    #         if next_button:
    #             is_disabled = await next_button.get_attribute("class") or ""
    #             if "disabled" in is_disabled:
    #                 break

    #             await next_button.click()
    #             await page.wait_for_load_state("domcontentloaded")
    #             await asyncio.sleep(2)  # small wait to avoid overload
    #         else:
    #             break

    #     await browser.close()

    # FUNDA CRAWLING
    async with async_playwright() as p:
        random_user_agent = random.choice(USER_AGENTS)

        browser = await p.firefox.launch(
            headless=True,
            args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled",
            "--disable-web-security",
            "--disable-dev-shm-usage",
            "--disable-infobars",
            "--disable-extensions",
            "--window-size=1920,1080",
            "--start-maximized",
        ],)

        context = await browser.new_context(
            user_agent=random_user_agent, 
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            java_script_enabled=True,
        )

        page = await context.new_page()

        await safe_goto(page, URL_FUNDA)

        while True:
            # --- Scrape current page ---
            listings = await page.query_selector_all("h2 a")
            print(listings)
            for listing in listings:
                link = await listing.get_attribute("href")
                listing_text = f"https://www.funda.nl{link}"
                current_listings.add(listing_text)
            break

        await browser.close()

    new_listings = current_listings - old_listings

    if new_listings:
        body = "\n\n".join(new_listings)
        await broadcast_message(
            message=f"🏠 New Rental Listings:\n\n{body}",
        )
       
    save_listings(current_listings)
    print('Fetching completed.')

if __name__ == "__main__":
    asyncio.run(repeat_crawl())
