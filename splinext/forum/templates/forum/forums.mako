<%inherit file="/base.mako" />

<%def name="title()">Forums</%def>

<h1>Forums</h1>
<table class="forum-list striped-rows">
<thead>
    <tr class="header-row">
        <th class="name">Forum</th>
        <th class="stats">Volume</th>
        <th class="stats">Activity</th>
    </tr>
</thead>
<tbody>
    % for forum in c.forums:
    <tr>
        <td class="name"><a href="${url(controller='forum', action='threads', forum_id=forum.id)}">${forum.name}</a></td>
        <td class="stats">xxx</td>
        <td class="stats">xxx</th>
    </tr>
    % endfor
</tbody>
</table>
