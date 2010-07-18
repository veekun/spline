from collections import namedtuple
import datetime
from pkg_resources import resource_filename
import subprocess

import feedparser
import lxml.html

from spline.lib import helpers
from spline.lib.plugin import PluginBase, PluginLink, Priority

import splinext.frontpage.controllers.frontpage

class FrontPageUpdate(object):
    """Base class ('interface') for an updated thing that may appear on the
    front page.

    Subclasses should implement the `time` and `template` properties.
    """
    pass


RSS_SUMMARY_LENGTH = 1000

FrontPageRSS = namedtuple('FrontPageRSS',
    ['time', 'entry', 'template', 'category', 'content', 'icon'])

def rss_hook(limit, max_age, url, title=None, icon=None):
    """Front page handler for news feeds."""
    feed = feedparser.parse(url)

    if not title:
        title = feed.feed.title

    updates = []
    for entry in feed.entries[:limit]:
        # Grab a date -- Atom has published, RSS usually just has updated.
        # Both come out as time tuples, which datetime.datetime() can read
        try:
            timestamp_tuple = entry.published_parsed
        except AttributeError:
            timestamp_tuple = entry.updated_parsed
        timestamp = datetime.datetime(*timestamp_tuple[:6])

        if max_age and timestamp < max_age:
            # Entries should be oldest-first, so we can bail after the first
            # expired entry
            break

        # Try to find something to show!  Default to the summary, if there is
        # one, or try to generate one otherwise
        content = u''
        if 'summary' in entry:
            # If there be a summary, cheerfully trust that it's actually a
            # summary
            content = entry.summary
        elif 'content' in entry:
            # Full content is way too much, especially for my giant blog posts.
            # Cut this down to some arbitrary number of characters, then feed
            # it to lxml.html to fix tag nesting
            broken_html = entry.content[0].value[:RSS_SUMMARY_LENGTH]
            fragment = lxml.html.fromstring(broken_html)

            # Insert an ellipsis at the end of the last node with text
            last_text_node = None
            last_tail_node = None
            # Need to find the last node with a tail, OR the last node with
            # text if it's later
            for node in fragment.iter():
                if node.tail:
                    last_tail_node = node
                    last_text_node = None
                elif node.text:
                    last_text_node = node
                    last_tail_node = None

            if last_text_node is not None:
                last_text_node.text += '...'
            if last_tail_node is not None:
                last_tail_node.tail += '...'

            # Serialize
            content = lxml.html.tostring(fragment)

        content = helpers.literal(content)

        update = FrontPageRSS(
            time = timestamp,
            entry = entry,
            template = '/front_page/rss.mako',
            category = title,
            content = content,
            icon = icon,
        )
        updates.append(update)

    return updates


FrontPageGit = namedtuple('FrontPageGit',
    ['time', 'gitweb', 'log', 'tag', 'template', 'category', 'icon'])
FrontPageGitCommit = namedtuple('FrontPageGitCommit',
    ['hash', 'author', 'time', 'subject', 'repo'])

def git_hook(limit, max_age, title, gitweb, repo_paths, repo_names,
    tag_pattern=None, icon=None):

    """Front page handler for repository history."""
    # Repo stuff can be space-delimited lists...
    repo_paths = repo_paths.split()
    repo_names = repo_names.split()

    # Fetch the main repo's git tags
    args = [
        'git',
        '--git-dir=' + repo_paths[0],
        'tag', '-l',
    ]
    if tag_pattern:
        args.append(tag_pattern)

    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    git_output, _ = proc.communicate()
    tags = git_output.strip().split('\n')

    # Tags come out in alphabetical order, which means earliest first.  Reverse
    # it to make the slicing easier
    tags.reverse()
    # Only history from tag to tag is actually interesting, so get the most
    # recent $limit tags but skip the earliest
    interesting_tags = tags[:-1][:limit]

    updates = []
    for tag, since_tag in zip(interesting_tags, tags[1:]):
        # Get the date when this tag was actually created
        args = [
            'git',
            '--git-dir=' + repo_paths[0],
            'for-each-ref',
            '--format=%(taggerdate:raw)',
            'refs/tags/' + tag,
        ]
        tag_timestamp, _ = subprocess.Popen(args, stdout=subprocess.PIPE) \
            .communicate()
        tag_unixtime, tag_timezone = tag_timestamp.split(None, 1)
        tagged_timestamp = datetime.datetime.fromtimestamp(int(tag_unixtime))

        if max_age and tagged_timestamp < max_age:
            break

        commits = []

        for repo_path, repo_name in zip(repo_paths, repo_names):
            # Grab an easily-parsed history: fields delimited by nulls.
            # Hash, author's name, commit timestamp, subject.
            git_log_args = [
                'git',
                '--git-dir=' + repo_path,
                'log',
                '--pretty=%h%x00%an%x00%at%x00%s',
                "{0}..{1}".format(since_tag, tag),
            ]
            proc = subprocess.Popen(git_log_args, stdout=subprocess.PIPE)
            for line in proc.stdout:
                hash, author, time, subject = line.strip().split('\x00')
                commits.append(
                    FrontPageGitCommit(
                        hash = hash,
                        author = author,
                        time = datetime.datetime.fromtimestamp(int(time)),
                        subject = subject,
                        repo = repo_name,
                    )
                )

        update = FrontPageGit(
            time = tagged_timestamp,
            gitweb = gitweb,
            log = commits,
            template = '/front_page/git.mako',
            category = title,
            tag = tag,
            icon = icon,
        )
        updates.append(update)

    return updates


def add_routes_hook(map, *args, **kwargs):
    """Hook to inject some of our behavior into the routes configuration."""
    map.connect('/', controller='frontpage', action='index')


class FrontPagePlugin(PluginBase):
    def controllers(self):
        return dict(
            frontpage = splinext.frontpage.controllers.frontpage.FrontPageController,
        )

    def template_dirs(self):
        return [
            (resource_filename(__name__, 'templates'), Priority.FIRST)
        ]

    def hooks(self):
        return [
            ('routes_mapping',          Priority.NORMAL,    add_routes_hook),
            ('frontpage_updates_rss',   Priority.NORMAL,    rss_hook),
            ('frontpage_updates_git',   Priority.NORMAL,    git_hook),
        ]
