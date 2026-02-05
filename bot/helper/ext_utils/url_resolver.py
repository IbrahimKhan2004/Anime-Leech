import aiohttp
import logging

# Set up logging to track the URL resolution process
logger = logging.getLogger(__name__)

async def resolve_final_url(start_url: str) -> str:
    """
    Follows redirects to find the final destination URL server-side.

    This function:
    1. Accepts the initial shortened URL.
    2. Uses a fake User-Agent to mimic a real browser (preventing blocking).
    3. Follows HTTP redirects up to a limit.
    4. Returns the final effective URL.
    5. Fails safe: returns the original URL if resolution errors occur.
    """
    if not start_url:
        return start_url

    try:
        # Mimic a standard Chrome browser on Windows to pass basic bot checks
        # Many shortener sites block requests with default python-aiohttp User-Agents
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5"
        }

        # Use aiohttp to follow redirects asynchronously
        async with aiohttp.ClientSession(headers=headers) as session:
            # We use GET because some shorteners block HEAD requests.
            # allow_redirects=True is default, but explicit is better.
            # Timeout is critical to prevent hanging the request if the shortener is slow/down.
            timeout = aiohttp.ClientTimeout(total=10)

            async with session.get(start_url, allow_redirects=True, timeout=timeout) as response:
                # response.url contains the final URL after following all redirects
                final_url = str(response.url)
                logger.info(f"Resolved URL: {start_url} -> {final_url}")
                return final_url

    except Exception as e:
        # If resolution fails (timeout, connection error, DNS issues),
        # log the error and return the original URL.
        # This ensures the user can at least attempt to visit the link directly
        # rather than getting a 500 error page.
        logger.error(f"Error resolving URL {start_url}: {e}")
        return start_url
