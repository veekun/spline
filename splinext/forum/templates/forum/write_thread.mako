<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />

<%def name="title()">Create a thread in ${c.forum.name} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li><a href="${url(controller='forum', action='threads', forum_id=c.forum.id)}">${c.forum.name}</a></li>
    <li>Create a thread</li>
</ul>
</%def>

${forumlib.write_thread_form(c.forum)}
