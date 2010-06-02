<%inherit file="/base.mako" />

<%def name="title()">${c.thread.subject} - ${c.thread.forum.name} - Forums</%def>

<div class="forum-post-container">
    % for post in c.thread.posts:
    <div class="forum-post">
        <div class="author">
            ${post.author.name}
        </div>
        <div class="meta">
            <time>${post.posted_time}</time>
        </div>
        <div class="content">${post.content}</div>
    </div>
    % endfor
</div>
