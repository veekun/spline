<%inherit file="/base.mako" />

<%def name="title()">${c.forum.name} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li>${c.forum.name}</li>
</ul>
</%def>

<table>
    % for thread in c.threads:
    <tr>
        <td><a href="${url(controller='forum', action='posts', forum_id=c.forum.id, thread_id=thread.id)}">${thread.subject}</a></td>
        <td>${thread.post_count}</td>
    </tr>
    % endfor
</table>
