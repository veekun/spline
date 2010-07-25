"""Base class for a front page source, as well as a handful of specific
implementations.
"""

from collections import namedtuple
import datetime
import subprocess
from subprocess import PIPE

import feedparser
import lxml.html

from spline.lib import helpers

def max_age_to_datetime(max_age):
    """``max_age`` is specified in config as a number of seconds old.  This
    function takes that number and returns a corresponding datetime object.
    """
    if max_age == None:
        return None

    seconds = int(max_age)



class Source(object):
    """Represents a source to be polled for updates.  Sources are populated
    directly from the configuration file.

    Properties:

    ``title``
        A name to identify this specific source.

    ``icon``
        Name of a Fugue icon to show next to the name.

    ``link``
        A URL where the full history of this source can be found.

    ``limit``
        The maximum number of items from this source to show at a time.
        Optional.

    ``max_age``
        Items older than this age (in seconds) will be excluded.  Optional.

    Additionally, subclasses **must** define a ``template`` property -- a path
    to a Mako template that knows how to render an update from this source.
    The template will be passed one parameter: the update object, ``update``.
    """

    def __init__(self, title, icon, link, limit=None, max_age=None):
        self.title = title
        self.icon = icon
        self.link = link
        self.limit = int(limit)
        self.max_age = max_age_to_datetime(max_age)

    def poll(self, global_limit, global_max_age):
        """Public wrapper that takes care of reconciling global and source item
        limit and max age.

        Subclasses should implement ``_poll``, below.
        """
        # Smallest limit wins
        limit = min(self.limit, global_limit)

        # Latest max age wins.  Note that either could be None, but that's
        # fine, because None is less than everything else
        max_age = max(self.max_age, global_max_age)

        return self._poll(limit, max_age)

    def _poll(self, limit, max_age):
        """Implementation of polling for updates.  Must return an iterable.
        Each element should be an object with ``source`` and ``time``
        properties.  A namedtuple works well.
        """
        raise NotImplementedError


FrontPageRSS = namedtuple('FrontPageRSS', ['source', 'time', 'entry', 'content'])
class FeedSource(Source):
    """Represents an RSS or Atom feed.

    Extra properties:

    ``feed_url``
        URL for the feed.
    """

    template = '/front_page/rss.mako'

    SUMMARY_LENGTH = 1000

    def __init__(self, feed_url, **kwargs):
        kwargs.setdefault('title', None)
        super(FeedSource, self).__init__(**kwargs)

        self.feed_url = feed_url

    def _poll(self, limit, max_age):
        feed = feedparser.parse(self.feed_url)

        if not self.title:
            self.title = feed.feed.title

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
                broken_html = entry.content[0].value[:self.SUMMARY_LENGTH]
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
                source = self,
                time = timestamp,
                content = content,
                entry = entry,
            )
            updates.append(update)

        return updates


FrontPageGit = namedtuple('FrontPageGit', ['source', 'time', 'log', 'tag'])
FrontPageGitCommit = namedtuple('FrontPageGitCommit',
    ['hash', 'author', 'time', 'subject', 'repo'])

class GitSource(Source):
    """Represents a git repository.

    The main repository is checked for annotated tags, and an update is
    considered to be the list of commits between them.  If any other
    repositories are listed and have the same tags, their commits will be
    included as well.

    Extra properties:

    ``repo_paths``
        Space-separated list of repositories.  These must be repository PATHS,
        not arbitrary git URLs.  Only the first one will be checked for the
        list of tags.

    ``repo_names``
        A list of names for the repositories, in parallel with ``repo_paths``.
        Used for constructing gitweb URLs and identifying the repositories.

    ``gitweb``
        Base URL to a gitweb installation, so commit ids can be linked to the
        commit proper.

    ``tag_pattern``
        Optional.  A shell glob pattern used to filter the tags.
    """

    template = '/front_page/git.mako'

    def __init__(self, repo_paths, repo_names, gitweb, tag_pattern=None, **kwargs):
        kwargs.setdefault('title', None)
        super(GitSource, self).__init__(**kwargs)

        # Repo stuff can be space-delimited lists
        self.repo_paths = repo_paths.split()
        self.repo_names = repo_names.split()

        self.gitweb = gitweb
        self.tag_pattern = tag_pattern

    def _poll(self, limit, max_age):
        # Fetch the main repo's git tags
        git_dir = '--git-dir=' + self.repo_paths[0]
        args = [
            'git',
            git_dir,
            'tag', '-l',
        ]
        if self.tag_pattern:
            args.append(self.tag_pattern)

        git_output, _ = subprocess.Popen(args, stdout=PIPE).communicate()
        tags = git_output.strip().split('\n')

        # Tags come out in alphabetical order, which means earliest first.  Reverse
        # it to make the slicing easier
        tags.reverse()
        # Only history from tag to tag is actually interesting, so get the most
        # recent $limit tags but skip the earliest
        interesting_tags = tags[:-1][:limit]

        updates = []
        for tag, since_tag in zip(interesting_tags, tags[1:]):
            # Get the date when this tag was actually created.
            # 'raw' format gives unixtime followed by timezone offset
            args = [
                'git',
                git_dir,
                'for-each-ref',
                '--format=%(taggerdate:raw)',
                'refs/tags/' + tag,
            ]
            tag_timestamp, _ = subprocess.Popen(args, stdout=PIPE).communicate()
            tag_unixtime, tag_timezone = tag_timestamp.split(None, 1)
            tagged_timestamp = datetime.datetime.fromtimestamp(int(tag_unixtime))

            if max_age and tagged_timestamp < max_age:
                break

            commits = []

            for repo_path, repo_name in zip(self.repo_paths, self.repo_names):
                # Grab an easily-parsed history: fields delimited by nulls.
                # Hash, author's name, commit timestamp, subject.
                git_log_args = [
                    'git',
                    '--git-dir=' + repo_path,
                    'log',
                    '--pretty=%h%x00%an%x00%at%x00%s',
                    "{0}..{1}".format(since_tag, tag),
                ]
                proc = subprocess.Popen(git_log_args, stdout=PIPE)
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
                source = self,
                time = tagged_timestamp,
                log = commits,
                tag = tag,
            )
            updates.append(update)

        return updates
