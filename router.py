from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Comment
from flask import Flask, request
import html5lib
import re
import  requests
app = Flask(__name__)
port = 8232

@app.before_request
def get_path():
    url = 'https://habr.com' + request.full_path
    page = requests.get(url)
    content_type = page.headers['Content-Type']

    if content_type.find('text/html') == -1:
        return page.text

    soup = bs(page.text, 'html5lib')

    for text_tag in soup.findAll(True):
        for child in text_tag.children:
            if isinstance(child, NavigableString) and not isinstance(child, Comment):
                if text_tag.name != 'script' and text_tag.name != 'style':
                    new_child = re.sub(r'(?P<begin>\W|^)(?P<middle>\w{6})(?P<end>\W|$)', r'\g<begin>\g<middle>™\g<end>', child)
                    child.replace_with(new_child)

    links = soup.findAll('a', href=re.compile(r'^https://habr.com'))

    for link in links:
        link['href'] = re.sub(r'^https://habr.com/', request.host_url, link.get('href'))

    resp = app.make_response(soup.prettify())
    resp.headers = request.headers

    return resp

if __name__ == '__main__':
    app.run(port = port)