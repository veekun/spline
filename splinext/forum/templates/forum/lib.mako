<%namespace name="lib" file="/lib.mako" />

<%def name="write_thread_form(forum)">
% if c.user.can('create_forum_thread'):
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
% if c.user.can('create_forum_post'):
<h1>Reply</h1>
${h.form(url(controller='forum', action='write', forum_id=thread.forum.id, thread_id=thread.id))}
<dl class="standard-form">
    ${lib.field('content', form=c.write_post_form, rows=12, cols=80)}

    <dd><button type="submit">Post!</button></dd>
</dl>
${h.end_form()}
% endif  ## can create post
</%def>
