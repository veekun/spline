<%namespace name="lib" file="/lib.mako" />
<%namespace name="userlib" file="/users/lib.mako" />

<%def name="posts(posts)">
<div class="forum-post-container">
    % for post in posts:
    <div class="forum-post">
        <div class="author">
            <div class="avatar">
                ${userlib.avatar(post.author)}
            </div>
            <div class="name">
                <a href="${url(controller='users', action='profile', id=post.author.id, name=post.author.name)}">
                    ${post.author.name}
                    ${userlib.color_bar(post.author)}
                </a>
            </div>
        </div>
        <div class="meta">
            <time>${post.posted_time}</time>
        </div>
        <div class="content">${post.content}</div>
    </div>
    % endfor
</div>
</%def>

<%def name="write_thread_form(forum)">
% if forum.can_create_thread(c.user):
<h1>Create new thread</h1>
${h.form(url(controller='forum', action='write_thread', forum_id=forum.id))}
<dl class="standard-form">
    ${lib.field('subject', form=c.write_thread_form)}
    ${lib.field('content', form=c.write_thread_form, rows=12, cols=80)}

    <dd><button type="submit">Post!</button></dd>
</dl>
${h.end_form()}
% endif  ## can create post
</%def>

<%def name="write_post_form(thread)">
% if thread.can_create_post(c.user):
<h1>Reply</h1>
${h.form(url(controller='forum', action='write', forum_id=thread.forum.id, thread_id=thread.id))}
<dl class="standard-form">
    ${lib.field('content', form=c.write_post_form, rows=12, cols=80)}

    <dd><button type="submit">Post!</button></dd>
</dl>
${h.end_form()}
% endif  ## can create post
</%def>
