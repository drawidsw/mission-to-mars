# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        'hemispheres': mars_imgs(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


def mars_imgs(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    # 3.1: Create a soup object.
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # 3.2: Use this anchor to get the parent object: <div class="collapsible results">
    parent_div = img_soup.find('div', class_='collapsible results')

    # 3.3: Get the individual divs using this anchor: <div class="item">
    children_divs = parent_div.find_all('div', class_='item')

    # 3.4: Look over the children divs.
    for div in children_divs:
    
        try:
            # 3.5: Drill down to the div with class = description: <div class="description">
            desc_div = div.find('div', class_='description')
    
            # 3.6: Get the href link:
            href_link = desc_div.find('a').get('href')
    
            # 3.7: Get the title.
            title = desc_div.find('a').find('h3').text.strip()
        
            # 3.8: Construct a full image link.
            full_img_link = f'{url}{href_link}'
        
            # 3.9: Create a new browser by visiting the full image URL
            browser.visit(full_img_link)
        
            # 3.10: Parse the html again and create a new soup object.
            html = browser.html
            img_soup = soup(html, 'html.parser')
        
            # 3.11: To find the sample image, start with <div class="downloads">
            full_img_href = img_soup.find('div', class_='downloads').\
                                     find('ul').\
                                     find_all('li')[0].\
                                     find('a').\
                                     get('href')
                            
            # 3.12: Insert a dictionary element in the list.
            hemisphere_image_urls.append({'img_url': f'{url}{full_img_href}',
                                      'title': title})

    
        except Exception as e:
            print (f'Raised exception {e}')

    return hemisphere_image_urls


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())