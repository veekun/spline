<%page args="update" />
<%namespace name="userlib" file="/users/lib.mako" />

<div class="frontpage-update">
    <div class="header">
        <div class="category">
            <a href="${update.source.link}"><img src="${h.static_uri('spline', "icons/{0}.png".format(update.source.icon))}" alt=""> ${update.source.title}</a>:
        </div>
        <div class="date">${update.time}</div>
        <div class="title">
            <a href="${update.entry.link}">${update.entry.title | n}</a>
        </div>
    </div>
    <div class="content">${update.content}</div>
</div>
