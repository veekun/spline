<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />

<%def name="title()">Forums</%def>

<h1>Forums</h1>
<table class="forum-list striped-rows">
<thead>
    <tr class="header-row">
        <th class="name">
            <img src="${h.static_uri('spline', 'icons/folders-stack.png')}" alt="">
            Forum
        </th>
        <th class="stats">Volume</th>
        <th class="stats">Activity</th>
    </tr>
</thead>
<tbody>
    % for forum in c.forums:
    <tr>
        <td class="name">
            <a href="${url(controller='forum', action='threads', forum_id=forum.id)}">${forum.name}</a>
            ${forumlib.forum_access_level(forum)}
        </td>
        <td class="stats">xxx</td>
        <td class="stats">xxx</th>
    </tr>
    % endfor
</tbody>
</table>
