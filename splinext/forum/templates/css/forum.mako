table.forum-list { width: 100%; }
table.forum-list .name { text-align: left; }
table.forum-list td.name a { display: block; font-size: 1.5em; padding: 0.33em; }
table.forum-list .stats { width: 10em; text-align: center; }

.forum-post-container { }
.forum-post { position: relative; margin: 1em 0; background: #fcfcfc; -moz-border-radius: 1em; -webkit-border-radius: 1em; }
.forum-post .author { position: absolute; top: 2.2em; right: 0; bottom: 0; width: 16em; padding: 0 1em; margin: 1em 0; border-left: 1px solid #b4c7e6; }
.forum-post .author .name { display: block; font-size: 1.5em; }
.forum-post .author .name .user-color-bar { display: block; font-size: 0.67em; width: auto; }
.forum-post .author .avatar { margin-bottom: 1em; }
.forum-post .author .avatar img { -moz-box-shadow: 0 0 2px black; }
.forum-post .meta { padding: 0.5em 1em; border: 1px solid #b4c7e6; background: url(${h.static_uri('local', 'images/layout/th-background.png')}) left bottom repeat-x; -moz-border-radius-topleft: 0.5em; -moz-border-radius-topright: 0.5em; -webkit-border-top-left-radius: 0.5em; -webkit-border-top-right-radius: 0.5em; }
.forum-post .content { min-height: 12em; margin-right: 16.5em; padding: 1em; }
.forum-post:nth-child(2n) { background: #f4f4f4; }
