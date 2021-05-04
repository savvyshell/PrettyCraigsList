from django.shortcuts import render
import requests
from requests.compat import quote_plus
from bs4 import BeautifulSoup
from . import models

BASE_CRAIGSLIST_URL = 'https://toronto.craigslist.org/search/?query={}'
BASE_IMAGE_URL = 'https://images.craigslist.org/{}_300x300.jpg'


def home(request):
    return render(request, 'base.html')


def new_search(request):
    search = request.POST.get('search')
    models.Search.objects.create(search=search)

    final_url = BASE_CRAIGSLIST_URL.format(quote_plus(search))
    res = requests.get(final_url)
    data = res.text

    soup = BeautifulSoup(data, features='html.parser')
    post_listings = soup.find_all('li', {'class': 'result-row'})

    all_postings = []

    for post in post_listings:
        post_title = post.find(class_='result-title').text
        post_url = post.find('a').get('href')

        elem_result_price = post.find(class_='result-price')
        if elem_result_price:
            post_price = elem_result_price.text
            if post_price == '$0':
                post_price = "N/A"
        else:
            post_price = 'N/A'

        if post.find(class_='result-image').get('data-ids'):
            post_image_id = post.find(class_='result-image').get('data-ids').split(',')[0].split(':')[1]
            post_image_url = BASE_IMAGE_URL.format(post_image_id)
        else:
            post_image_url = 'https://craigslist.org/images/peace.jpg'

        all_postings.append({
            'title': post_title,
            'url': post_url,
            'price': post_price,
            'image': post_image_url
        })

    pack = {
        'search': search,
        'all_postings': all_postings
    }
    return render(request, 'my_app/new_search.html', pack)

