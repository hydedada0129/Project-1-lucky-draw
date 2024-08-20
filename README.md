This Python script can scrape the draw website and export it as CSV file. 
It collects data without manually copy and paste.
Also, it is sent by gmail api to designated email address.

Google Chrome is default browser.

Gmail API setup.

trap and bump in the road:
if you use Firefox as your default browser, you might encounter a problem that when you run the gmail api authentication, the we browser may block you if you set "".

Bump in the road:
You might encounter block OAuth issue when your first authentication in your browser. Try temporarily disable the "add-ons" (I encountered and fixed the issue by disable my Firefox add-on "ClearURLs") or any other can cause to block the authentication from Gmail API.  
