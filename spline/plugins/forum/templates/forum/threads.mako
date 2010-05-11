<%inherit file="/base.mako" />

<%def name="title()">${c.forum.name} - Forums</%def>

<ul class="classic-list">
    % for thread in c.forum.threads:
    <li><a href="${url(controller='forum', action='posts', forum_id=c.forum.id, thread_id=thread.id)}">${thread.subject}</a></li>
    % endfor
</ul>
