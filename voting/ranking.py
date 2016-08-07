# From: http://possiblywrong.wordpress.com/2011/06/05/reddits-comment-ranking-algorithm/
from django.utils import timezone
from math import log, sqrt


def confidence(ups, downs):
    if ups == 0:
        return -downs
    n = ups + downs
    z = 1.64485  # 1.0 = 85%, 1.6 = 95%
    phat = float(ups) / n
    return (phat + z * z / (2 * n) - z * sqrt(
        (phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)

"""
SQL version of confidence score:
IF(num_likes = 0, -num_dislikes, ((num_likes / (num_likes + num_dislikes)) + 1.64485 * 1.64485 /(2 * (num_likes + num_dislikes)) - 1.64485 * SQRT(((num_likes / (num_likes + num_dislikes)) * (1 - (num_likes / (num_likes + num_dislikes)))+ 1.64485 * 1.64485 / (4* (num_likes + num_dislikes))) / (num_likes + num_dislikes)))/(1 + 1.64485 * 1.64485 / (num_likes + num_dislikes)))

UPDATE commenting_comment_new SET likes_confidence_score = IF(num_likes = 0, -num_dislikes, ((num_likes / (num_likes + num_dislikes)) + 1.64485 * 1.64485 /(2 * (num_likes + num_dislikes)) - 1.64485 * SQRT(((num_likes / (num_likes + num_dislikes)) * (1 - (num_likes / (num_likes + num_dislikes)))+ 1.64485 * 1.64485 / (4* (num_likes + num_dislikes))) / (num_likes + num_dislikes)))/(1 + 1.64485 * 1.64485 / (num_likes + num_dislikes)));

SQL version of hot score:
ROUND((LOG10(IF(ABS(num_likes - num_dislikes) > 1, ABS(num_likes - num_dislikes), 1)) + IF((num_likes - num_dislikes) > 0, 1, IF((num_likes - num_dislikes) < 0, -1, 0)) * (UNIX_TIMESTAMP(created) - 1134028003) / 45000), 7)

UPDATE commenting_comment_new SET likes_hot_score = ROUND((LOG10(IF(ABS(num_likes - num_dislikes) > 1, ABS(num_likes - num_dislikes), 1)) + IF((num_likes - num_dislikes) > 0, 1, IF((num_likes - num_dislikes) < 0, -1, 0)) * (UNIX_TIMESTAMP(created) - 1134028003) / 45000), 7);
"""

# From: http://amix.dk/blog/post/19588
# Rewritten code from /r2/r2/lib/db/_sorts.pyx
epoch = timezone.datetime(1970, 1, 1)


def epoch_seconds(date):
    """Returns the number of seconds from the epoch to date."""
    if timezone.is_aware(date):
        date = timezone.make_naive(date)
    td = date - epoch
    return td.days * 86400 + td.seconds + (float(td.microseconds) / 1000000)


def score(ups, downs):
    return ups - downs


def hot(ups, downs, date):
    """The hot formula. Should match the equivalent function in postgres."""
    """
    Attempt to make it in SQL, its missing the SIGN variable
    select *,
        ROUND((LOG10(ABS(a.num_likes - a.num_dislikes)) +
            IF((num_likes - num_dislikes) > 0, 1, IF((num_likes - num_dislikes) < 0, -1, 0)) * (UNIX_TIMESTAMP(a.created) - 1134028003) / 45000), 7) as hot
    from blog_article a
    order by hot desc
    limit 10;
    """
    s = score(ups, downs)
    order = log(max(abs(s), 1), 10)
    sign = 1 if s > 0 else -1 if s < 0 else 0
    seconds = epoch_seconds(date) - 1134028003
    return round(order + sign * seconds / 45000, 7)
