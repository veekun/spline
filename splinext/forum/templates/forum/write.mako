<%inherit file="/base.mako" />
<%namespace name="lib" file="/lib.mako" />

<%def name="title()">Post to ${c.thread.subject} - ${c.thread.forum.name} - Forums</%def>

${h.form(url.current())}
<dl class="standard-form">
    ${lib.field('content', rows=12, cols=80)}

    <dd><button type="submit">Post!</button></dd>
</dl>
${h.end_form()}
