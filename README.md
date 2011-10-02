BTHEventSource
=

**Cross-browser Server-Sent Events Wrapper**

This is a small and experimental wrapper for EventSource. It's intended to work out differences between browser implementations and provide XHR long-polling fallback when EventSource isn't available.

Requirements
-

The only requirement is `window.JSON` object. If you target browsers that don't provide a native JSON implementation (e.g. IE 6/7) then it's required that you provide it. The usual (and recommended) implementation is [JSON-js](https://github.com/douglascrockford/JSON-js).

Backend
-

JSON is used as data format for all the messages, regardless of transport. When working with SSE the backend should set Content-Type header to "text/event-stream" (for Firefox and WebKits) or "application/x-dom-event-stream" (for Opera). EventSource URL will be passed an additional query string parameter `opera=1` to indicate that the UA is Opera. In case of XHR long-polling respond with "application/json".

XHR long-polling response format:

```javascript
{ 'id': 1234567890, 'event': 'event-name', 'data': 'event-data' }
```

The only required field is `data`. The `id` and `event` correspond to `id` and `event` fields of event stream. Consult [this tutorial](http://www.html5rocks.com/en/tutorials/eventsource/basics/) if you need more info. `retry` field isn't supported.

Event ID will be passed as an EventSource URL query string parameter `last_event_id` if previous request timed out or returned an error. If previous request was successful but no data was received (e.g. due to lack of data to send from backend) then Event ID won't be passed to the backend.

Check out `backend/btheventsource.py` for an example implementation for Tornado 2.

Frontend
-

### Installation

```javascript
var source = window.BTHEventSource('/events');
var xhr_source = window.BTHEventSource('/events', true);
```

The first argument is the URL of event stream. The second is optional and if you provide anything that's not `undefined` you'll force XHR long-polling.

### Registering event handlers

```javascript
source.open(function() { alert('The connection was opened!'); });
source.close(function() { alert('The connection was closed :(.'); });
source.error(function() { alert('Communication error. Crap.'); });
source.message(function(data) { alert('Received an unnamed event.'); });
source.message('myEvent', function(data) { alert('Received "myEvent" event.'); });
```

### Interacting with the source

```javascript
source.start();
source.stop();
```

### Caveats

* To open the communication channel (regardless of transport) you have to call `start()` explicitly,
* `open` event will fire after the transport receives the very first event. This applies both to SSE and XHR transports. Note that SSE behavior is browser-dependent and may change,
* `close` event will not be fired on Opera because the browser doesn't fire internal SSE `error` event when the connection is closed,
* `close` event will be fired for **every** XHR request that times out,
* cross-domain requests aren't supported.

Browser compatibility
-

I tested the wrapper on IE 6/7/8, FF 3.6/6/7, Safari 5, Chrome 14 and Opera 11.51 running under Mac OS X 10.6 and/or Windows XP.

Example
-

Under `examples/chat/` you'll find a small Tornado chat app that uses BTHEventSource to deliver updates to users. It's not perfect but does the job of both working and showing the wrapper in action.

License
-

MIT-style, see LICENSE.