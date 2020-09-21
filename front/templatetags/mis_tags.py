from django import template

register = template.Library()

# General.
@register.filter
def clean_hashtag(hashtag):
    hashtag = hashtag.replace('#', '%23')
    if (' ' in hashtag):
        hashtag = '"{}"'.format(hashtag)
    return hashtag

