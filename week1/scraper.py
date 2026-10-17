from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

headers = {
    "User-Agent": "Mozilla/5.0"
}


# # Standard headers to fetch a website
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
# }


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    # print(type(title))
    # print(title)
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    links = [link.get("href") for link in soup.find_all("a")]
    


    
    if not text.strip():
        text = "Empty"
        raise ValueError("HTML parsing failed: Website is not allowing to parse text. Choose different URL ")
        
    return (title + "\n\n" + text)[:2_000]


# fetch_website_contents("https://www.thewildlifediaries.com")


# def fetch_website_links(url):
#     """
#     Return the links on the webiste at the given url
#     I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
#     Feel free to use a class and optimize it!
#     """
#     response = requests.get(url, headers=headers)
#     soup = BeautifulSoup(response.content, "html.parser")
#     links = [link.get("href") for link in soup.find_all("a")]
#     return [link for link in links if link]


### Updated functions : Crawl over sites and internally checks the links and fetches information from there
### also


def fetch_website_page(url):
    """
    Fetch one page and return:
        text, links
    """

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    title = (
        soup.title.string.strip()
        if soup.title and soup.title.string
        else "No title"
    )

    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()

        text = soup.body.get_text(
            separator="\n",
            strip=True
        )
    else:
        text = ""

    links = []

    for link in soup.find_all("a", href=True):
        href = link["href"]

        # Convert relative URL to absolute URL
        full_url = urljoin(url, href)

        # Only HTTP/HTTPS
        if full_url.startswith(("http://", "https://")):
            links.append(full_url)

    return title, text, links


def fetch_links(seed_url,max_urls = 50):

    """
    Start from seed_url and keep processing newly
    discovered links until there are no unprocessed
    links remaining.
    """

    visited = set()
    to_visit = [seed_url]

    all_text = ""

    # Only crawl the seed website
    seed_domain = urlparse(seed_url).netloc

    while to_visit:

        if len(visited) >= max_urls:
            print(f"Reached limit of {max_urls} URLs. Stopping crawl.")
            break

        # Take one URL that hasn't been processed yet
        current_url = to_visit.pop(0)

        # Skip if already processed
        if current_url in visited:
            continue


        print(f"Fetching [{len(visited) + 1}/{max_urls}]: {current_url}")

        try:
            title, text, links = fetch_website_page(current_url)

        except Exception as e:
            print(f"Failed to fetch {current_url}: {e}")
            continue
        
        visited.add(current_url)  ## Successfully added url

        # Append current page's information
        all_text += f"\n\n===== {title} =====\n"
        all_text += text

        # Process links found on this page
        for link in links:

            # Only stay on the same website
            if urlparse(link).netloc != seed_domain:
                continue

            # Don't add URLs we've already processed
            if link in visited:
                continue

            # Don't add duplicate URLs to the queue
            if link not in to_visit:
                to_visit.append(link)

    return all_text

# text = fetch_links("https://www.oreo.com")

# print(text)


