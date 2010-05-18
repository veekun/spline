<%inherit file="/base.mako" />

<%def name="title()">Forums</%def>

<table>
    % for forum in c.forums:
    <tr>
        <td><a href="${url(controller='forum', action='threads', forum_id=forum.id)}">${forum.name}</a></td>
    </tr>
    % endfor
</table>
