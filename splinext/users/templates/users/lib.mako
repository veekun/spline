<%def name="color_bar(user)">\
<span class="user-color-bar">
    % for width, color in user.unique_colors:
    <span class="user-color-bar-chunk" style="width: ${width * 100.0}%; background-color: ${color};"></span>
    % endfor
</span>\
</%def>
