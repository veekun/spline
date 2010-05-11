<%inherit file="/base.mako" />

<%def name="title()">${c.thread.subject} - ${c.thread.forum.name} - Forums</%def>

<ul class="classic-list">
    % for post in c.thread.posts:
    <li><blockquote>${post.content}</blockquote></li>
    % endfor
</ul>
