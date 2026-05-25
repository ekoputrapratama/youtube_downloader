import logging
import requests

from bs4 import BeautifulSoup

log = logging.getLogger("ytdlp")


def getSiteTitle(url):
  """
  Fetches the title of a webpage from a given URL.
  """
  try:
    # Send a GET request to the URL
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    # Raise an exception for bad status codes (4xx or 5xx)
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <title> tag and get its text
    title_tag = soup.find('title')

    if title_tag:
      # Return the stripped text of the title tag
      return title_tag.get_text(strip=True)
    else:
      return "No title found"

  except requests.exceptions.RequestException as e:
    return f"Error fetching the page: {e}"
