<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />
<%namespace name="lib" file="/lib.mako" />

<%def name="title()">${c.thread.subject} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li><a href="${url(controller='forum', action='threads', forum_id=c.thread.forum.id)}">${c.thread.forum.name}</a></li>
    <li>${c.thread.subject}</li>
</ul>
</%def>

<h1>Posts</h1>
${forumlib.hierarchy(c.thread.forum, c.thread)}

% if c.thread.post_count == 0:
<p>Something terribly bogus has happened; this thread has no posts.</p>
% else:
${lib.pager(c.skip, c.per_page, c.thread.post_count, dict(controller='forum', action='posts', forum_id=c.thread.forum_id, thread_id=c.thread.id))}
${forumlib.posts(c.posts)}
${lib.pager(c.skip, c.per_page, c.thread.post_count, dict(controller='forum', action='posts', forum_id=c.thread.forum_id, thread_id=c.thread.id))}
% endif

${forumlib.write_post_form(c.thread)}
