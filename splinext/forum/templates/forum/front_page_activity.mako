<%page args="obj" />
<%namespace name="userlib" file="/users/lib.mako" />

<h1>Forum activity</h1>

% if obj.threads:
<table class="striped-rows" style="width: 100%;">
<tbody>
    % for thread in obj.threads:
    <tr>
        <td class="name"><a href="${url(controller='forum', action='posts', forum_id=thread.forum.id, thread_id=thread.id)}">${thread.subject}</a></td>
    </tr>
    % endfor
</tbody>
</table>
% else:
<p>The forums are dead quiet.  No one is posting.  A lone tumbleweed rolls by.</p>
<p>Maybe you should <a href="${url(controller='forum', action='forums')}">do something about this</a>.</p>
% endif
