<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />

<%def name="title()">${c.thread.subject} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li><a href="${url(controller='forum', action='threads', forum_id=c.thread.forum.id)}">${c.thread.forum.name}</a></li>
    <li>${c.thread.subject}</li>
</ul>
</%def>

% if c.thread.post_count == 0:
<p>Something terribly bogus has happened; this thread has no posts.</p>
% else:
${forumlib.posts(c.thread.posts)}
% endif

${forumlib.write_post_form(c.thread)}
