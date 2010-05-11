<%inherit file="/base.mako" />

<%def name="title()">Forums</%def>

<ul class="classic-list">
    % for forum in c.forums:
    <li><a href="${url(controller='forum', action='threads', forum_id=forum.id)}">${forum.name}</a></li>
    % endfor
</ul>
