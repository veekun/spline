<%page args="update" />
<%namespace name="userlib" file="/users/lib.mako" />

<div class="frontpage-update">
    <div class="header">
        <div class="category"><img src="${h.static_uri('spline', "icons/{0}.png".format(update.icon or 'feed'))}" alt=""> ${update.category}:</div>
        <div class="date">${update.time}</div>
        <div class="title">
            <a href="${update.entry.link}">${update.entry.title | n}</a>
        </div>
    </div>
    <div class="content">${update.content}</div>
</div>
