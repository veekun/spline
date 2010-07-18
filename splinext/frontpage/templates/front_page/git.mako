<%page args="update" />

<div class="frontpage-update">
    <div class="header">
        <div class="category"><img src="${h.static_uri('spline', "icons/{0}.png".format('gear--pencil'))}" alt=""> ${update.category}:</div>
        <div class="date">${update.time}</div>
        <div class="title">${update.tag}</div>
    </div>
    <div class="content">
        <table class="frontpage-repository striped-rows">
            <% last_repo = None %>\
            % for commit in update.log:
            % if commit.repo != last_repo:
            <tr class="frontpage-repository-header">
                <th colspan="4">${commit.repo}</th>
            </tr>
            % endif

            <tr>
                <td class="hash"><a href="${update.gitweb}?p=${commit.repo}.git;a=commit;h=${commit.hash}">${commit.hash}</a></td>
                <td class="author">${commit.author}</td>
                <td class="subject">${commit.subject}</td>
                <td class="time">${commit.time}</td>
            </tr>
            <% last_repo = commit.repo %>\
            % endfor
        </table>
    </div>
</div>
