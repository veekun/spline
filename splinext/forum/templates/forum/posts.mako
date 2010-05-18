<%inherit file="/base.mako" />

<%def name="title()">${c.thread.subject} - ${c.thread.forum.name} - Forums</%def>

<div class="forum-post-container">
    % for post in c.thread.posts:
    <div class="forum-post">
        <div class="content">${post.content}</div>
    </div>
    % endfor
</div>
