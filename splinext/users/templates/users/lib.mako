<%def name="color_bar(user)">\
<span class="user-color-bar">
    % for width, color in user.unique_colors:
    <span class="user-color-bar-chunk" style="width: ${width * 100.0}%; background-color: ${color};"></span>
    % endfor
</span>\
</%def>

## XXX support user emails, oops
<%def name="avatar(user, size=96)">\
<%! import hashlib %>\
<img src="http://www.gravatar.com/avatar/${hashlib.md5(str(user.id)).hexdigest()}?r=x&amp;s=${size}&amp;d=identicon" alt="${user.name}'s avatar" title="${user.name}">\
</%def>
