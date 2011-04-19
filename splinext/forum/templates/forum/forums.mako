<%inherit file="/base.mako" />
<%namespace name="forumlib" file="/forum/lib.mako" />
<%namespace name="userlib" file="/users/lib.mako" />

<%def name="title()">Forums</%def>

<h1>Forums</h1>
<table class="forum-list striped-rows">
<thead>
    <tr class="header-row">
        <th class="name">
            <img src="${h.static_uri('spline', 'icons/folders-stack.png')}" alt="">
            Forum
        </th>
        <th class="last-post">Last post</th>
        <th class="stats">Volume</th>
        <th class="stats">Activity</th>
    </tr>
</thead>
<tbody>
    % for forum in c.forums:
    <tr>
        <td class="name">
            <a href="${url(controller='forum', action='threads', forum_id=forum.id)}">${forum.name}</a>
            ${forumlib.forum_access_level(forum)}
            % if forum.description:
            <div class="forum-description">
                ${forum.description}
            </div>
            % endif
        </td>

        <td class="last-post">
            <% last_post = c.last_post.get(forum.id, None) %> \
            % if last_post:
            ## XXX should do direct post link
            <a href="${url(controller='forum', action='posts', forum_id=forum.id, thread_id=last_post.thread_id)}">${last_post.posted_time}</a>
            <br> in <a href="${url(controller='forum', action='posts', forum_id=forum.id, thread_id=last_post.thread_id)}">${last_post.thread.subject}</a>
            <br> by <a href="${url(controller='users', action='profile', id=last_post.author.id, name=last_post.author.name)}">${userlib.color_bar(last_post.author)} ${last_post.author.name}</a>
            % else:
            —
            % endif
        </td>

        <% relative_volume = c.forum_volume[forum.id] / c.max_volume %>\
        <td class="stats
            % if relative_volume < 0.1:
            verylow
            % elif relative_volume < 0.33:
            low
            % elif relative_volume < 0.5:
            okay
            % elif relative_volume < 0.67:
            high
            % elif relative_volume < 0.9:
            veryhigh
            % else:
            whoanelly
            % endif
        ">
            ${"{0:3.1f}".format(c.forum_volume[forum.id] * 100)}%
        </th>
        <% activity = c.forum_activity[forum.id] %>\
        <td class="stats
            % if activity < 0.25:
            verylow
            % elif activity < 0.5:
            low
            % elif activity < 1.0:
            okay
            % elif activity < 2.0:
            high
            % elif activity < 4.0:
            veryhigh
            % else:
            whoanelly
            % endif
        ">
            ${"{0:0.3f}".format(activity)}
        </td>
    </tr>
    % endfor
</tbody>
</table>
