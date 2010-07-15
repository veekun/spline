<%page args="update" />
<%namespace name="userlib" file="/users/lib.mako" />

<div class="frontpage-update">
    <div class="header">
        <div class="category"><img src="${h.static_uri('spline', 'icons/newspapers.png')}" alt=""> ${config['spline.site_title']} news:</div>
        <div class="title">
            <a href="${url(controller='forum', action='posts', forum_id=update.post.thread.forum.id, thread_id=update.post.thread.id)}">
                ${update.post.thread.subject}
            </a>
        </div>
        <div class="date">${update.post.posted_time}</div>
    </div>
    <div class="avatar">
        <a href="${url(controller='users', action='profile', id=update.post.author.id, name=update.post.author.name)}">
            ${userlib.avatar(update.post.author, size=48)}
        </a>
    </div>
    <div class="content">${update.post.content}</div>
    <div class="comments">
        <a href="${url(controller='forum', action='posts', forum_id=update.post.thread.forum.id, thread_id=update.post.thread.id)}">
            ${update.post.thread.post_count - 1} comment${'' if update.post.thread.post_count == 2 else 's'}
        </a>
    </div>
</div>
