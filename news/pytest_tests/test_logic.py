import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
    author_client, author, form_data, new, news_pk
):
    url = reverse('news:detail', args=news_pk)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == new


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news_pk):
    url = reverse('news:detail', args=news_pk)
    client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_use_bad_words(author_client, news_pk):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=news_pk)
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment_pk):
    url = reverse('news:delete', args=comment_pk)
    response = author_client.delete(url)
    url_to_comments = reverse('news:detail', args=comment_pk)
    assertRedirects(response, f'{url_to_comments}#comments')

    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(
    not_author_client, comment_pk
):
    url = reverse('news:delete', args=comment_pk)
    response = not_author_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    author_client, form_data, comment_pk, comment
):
    url = reverse('news:edit', args=comment_pk)
    response = author_client.post(url, data=form_data)
    url_to_comments = reverse('news:detail', args=comment_pk)
    assertRedirects(response, f'{url_to_comments}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment_pk, form_data, comment
):
    url = reverse('news:edit', args=comment_pk)
    response = not_author_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
