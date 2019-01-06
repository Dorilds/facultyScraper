from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pdb
import pprint
import re

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors.
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def dept_faculty(response):
    '''
    Get the faculty from a specific department and return list of them
    '''

    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        faculty = []
        for h2 in html.find_all('h2', {'class': 'media-heading people_name'}):
            faculty.append(h2.text.strip())
        return faculty

def get_depts():
    '''
    returns list of departments and list of links to depts
    '''
    url = "https://www.swarthmore.edu/academics"
    response = simple_get(url)
    depts = []
    dept_links = []
    if response is not None:
        html = BeautifulSoup(response, 'html.parser')
        for li in html.find_all(class_="first leaf list-group-item"):
            dept_links.append(li.a.get('href'))
            depts.append(li.a.text)
        for li in html.find_all(class_="leaf list-group-item"):
            dept_links.append(li.a.get('href'))
            depts.append(li.a.text)

    return dept_links, depts

def get_images(link):
    '''
    Scrapes images from website url
    '''
    response = requests.get(link)

    soup = BeautifulSoup(response.text, 'html.parser')
    img_tags = soup.find_all('img')

    urls = [img['src'] for img in img_tags]

    filenames = []
    for url in urls:
        filename = re.search(r'/([\w_-]+[.](jpg|gif|png))$', url)
        filenames.append(filename)
        with open(filename.group(1), 'wb') as f:
            if 'http' not in url:
                # sometimes an image source can be relative
                # if it is provide the base url which also happens
                # to be the site variable atm.
                url = '{}{}'.format(site, url)
            response = requests.get(url)
            f.write(response.content)

    return filenames

def main():

    #url = "https://www.swarthmore.edu/classics/faculty-staff"
    url_beginning = "https://www.swarthmore.edu"
    dept_links, depts = get_depts()
    all_faculty = {}
    parsed_faculty = []
    for i,link in enumerate(dept_links):
        url = url_beginning + link + '/faculty-staff'
        response = simple_get(url)
        faculty = dept_faculty(response)
        all_faculty[depts[i]] = faculty
        for f in faculty:
            parsed_faculty += f.lower().replace(" ", "-")
    #for pf in parsed_faculty:
        #url = url_beginning + '/profile'
        #files = get_images(url)

    #pprint.pprint(all_faculty)



main()
