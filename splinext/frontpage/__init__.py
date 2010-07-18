from collections import namedtuple
import datetime
from pkg_resources import resource_filename
import subprocess

import feedparser

from spline.lib import helpers
from spline.lib.plugin import PluginBase, PluginLink, Priority

import splinext.frontpage.controllers.frontpage

class FrontPageUpdate(object):
    """Base class ('interface') for an updated thing that may appear on the
    front page.

    Subclasses should implement the `time` and `template` properties.
    """
    pass


FrontPageRSS = namedtuple('FrontPageRSS',
    ['time', 'entry', 'template', 'category', 'content', 'icon'])

def rss_hook(limit, url, title, icon=None):
    """Front page handler for news feeds."""
    feed = feedparser.parse(url)

    updates = []
    for entry in feed.entries:
        # Try to find something to show!  Default to the summary, if there is
        # one, or try to generate one otherwise
        content = u''
        if 'summary' in entry:
            content = entry.summary
        elif 'content' in entry:
            content = entry.content[0].value

        content = helpers.literal(content)

        update = FrontPageRSS(
            time = datetime.datetime(*entry.published_parsed[:6]),
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

def git_hook(limit, title, gitweb, repo_paths, repo_names,
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

        # LASTLY, get the date when this tag was actually created
        args = [
            'git',
            'for-each-ref',
            '--format=%(taggerdate:raw)',
            'refs/tags/' + tag,
        ]
        tag_timestamp, _ = subprocess.Popen(args, stdout=subprocess.PIPE) \
            .communicate()
        tag_unixtime, tag_timezone = tag_timestamp.split(None, 1)

        update = FrontPageGit(
            time = datetime.datetime.fromtimestamp(int(tag_unixtime)),
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
