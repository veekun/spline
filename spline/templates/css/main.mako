/*** Base page elements ***/

/* Base font.  This is a load of crap.  Why can't everyone have a default
 * browser font they actually want to see?  Fuck fuck fuckity fuck IE. */
body { font-family: DejaVu Sans, Verdana, sans-serif; font-size: 12px; }

/* Display */
body { background: #ddd; }
#header, #menu, #content, #footer { padding: 1em; }
#header { background: #2457a0; color: white; }
#menu { border-right: 1px solid #2457a0; background: #c6d8f2; }
#content { background: white; }
#footer { border-top: 1px solid #2457a0; background: #ddd; }

/* Layout: any-order columns */
#header {}
#content-wrapper { float: left; width: 100%; }
#content { margin-left: 15em; }
#menu { float: left; width: 13em; margin-left: -100%; }

/* Layout: equal-height columns */
#body { overflow: hidden; }
#menu, #content { padding-bottom: 1004em; margin-bottom: -1000em; }

/* Basics */
h1 { font-size: 2em; margin: 0.5em 0 0.25em 0 /* 1em 0 0.5em 0 */; padding-bottom: 0.125em /* 0.25em */; border-bottom: 1px solid #2457a0; color: #2457a0; }
h2 { font-size: 1.67em; margin: 0.6em 0 0.3em 0 /* 1em 0 0.5em 0 */; color: #2457a0; }

table th, table td { padding: 0.25em; }
table th { font-weight: normal; color: #2457a0; }
table tr.header-row th { border-bottom: 1px solid #2457a0; background: #c6d8f2; color: black; }

img { vertical-align: middle; }

form {}
input[type='text'].error { background-color: #f2c6d8; }

.faded { opacity: 0.33; }

tr.altrow { background: #f0f0f0; }

/* Definition lists via floats */
dl { overflow: hidden /* new float context */; }
dt { float: left; clear: left; width: 11.5em; margin-right: 0.5em; text-align: right; color: #2457a0; }
dt:after { content: ':'; }
dd { padding-left: 12em /* float width, so hover highlight includes dt but lines wrap correctly */; }
dd:after { content: 'float clear'; display: block; clear: both; height: 0; visibility: hidden; }
dt, dd { line-height: 1.33; }
