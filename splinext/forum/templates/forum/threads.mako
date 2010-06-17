<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />

<%def name="title()">${c.forum.name} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li>${c.forum.name}</li>
</ul>
</%def>

<table class="forum-list striped-rows">
<thead>
    <tr class="header-row">
        <th class="name">Thread</th>
        <th class="stats">Posts</th>
    </tr>
</thead>
<tbody>
    % for thread in c.threads:
    <tr>
        <td class="name"><a href="${url(controller='forum', action='posts', forum_id=c.forum.id, thread_id=thread.id)}">${thread.subject}</a></td>
        <td class="stats">${thread.post_count}</td>
    </tr>
    % endfor
</tbody>
</table>

${forumlib.write_thread_form(c.forum)}
