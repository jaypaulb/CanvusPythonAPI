API expects lower case widget_type - but responses with mixed case widget_type!
POST {"widget_type":"note", other json settings here}
response
200 Ok
{"widget_type":"Note", other matching json)

not top of that the end points are the plural of the widget_type - just to make it so you can't easily form the endpoints from the Json array I would guess! ;-)