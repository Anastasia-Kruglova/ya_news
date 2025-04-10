import pytest

from django.conf import settings
from django.urls import reverse


@pytest.mark.parametrize(
    'parametrized_client, form_on_page',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_notes_list_for_different_users(
        parametrized_client, form_on_page, comment_pk
):
    url = reverse('news:detail', args=comment_pk)
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_on_page


@pytest.mark.django_db
def test_news_count_and_order(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, news_pk, date_comments):
    url = reverse('news:detail', args=news_pk)
    response = client.get(url)
    assert 'news' in response.context

    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps
