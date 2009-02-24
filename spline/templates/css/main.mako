<%include file="reset.mako"/>

/*** Base page elements ***/

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
h1 { font-size: 2em; }
