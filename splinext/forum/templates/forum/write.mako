<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />

<%def name="title()">Reply to ${c.thread.subject} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li><a href="${url(controller='forum', action='threads', forum_id=c.thread.forum.id)}">${c.thread.forum.name}</a></li>
    <li><a href="${url(controller='forum', action='posts', thread_id=c.thread.id, forum_id=c.thread.forum.id)}">${c.thread.subject}</a></li>
    <li>Reply</li>
</ul>
</%def>

${forumlib.write_post_form(c.thread)}
