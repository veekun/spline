<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />

<%def name="title()">${c.thread.subject} - Forums</%def>

<%def name="title_in_page()">
<ul id="breadcrumbs">
    <li><a href="${url(controller='forum', action='forums')}">Forums</a></li>
    <li><a href="${url(controller='forum', action='threads', forum_id=c.thread.forum.id)}">${c.thread.forum.name}</a></li>
    <li>${c.thread.subject}</li>
</ul>
</%def>

% if c.thread.post_count == 0:
<p>Something terribly bogus has happened; this thread has no posts.</p>
<% return %>
% endif

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

${forumlib.write_post_form(c.thread)}
