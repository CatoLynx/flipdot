#Server Protocol Specification

##Message Structure
The server receives either a single message or a list of messages to process.
Each message is wrapped in an envelope which specifies the type of message and which display it is intended for.

**Example:**
```json
[
  {
    "type": "data",
    "display": "my-display",
    "message": {...}
  }
]
```

The `message` parameter contains the actual message.

**Available message types:**

* `data`: Send data to be displayed
* `control`: Set display options
* `query-config`: Get configuration options
* `query-hwconfig`: Get hardware configuration
* `query-message`: Get the currently active message(s)
* `query-bitmap`: Get the current bitmaps displayed on the displays

##Message Types
In this section, we'll have a look at the different message types. In the following JSON examples, only the `message` parameter will be shown, the envelope will be omitted for better readability.

###Data message
This message type is used to send display data to the display. It has several subtypes which specify what kind of data will be sent.

**Available subtypes:**

* `sequence`: Send multiple frames to be displayed sequentially
* `single`: Send a "normal" frame to the display, that is everything needed to build the picture you want to display

####Sequence message
Sequence messages are not really a type of their own, the're just another envelope containing multiple messages. Their structure is as follows, `messages` being a list of `single`-type messages:

```json
{
  "type": "sequence",
  "interval": 5.0,
  "messages": [...]
}
```

####Single message
This message subtype is used to build a display frame by piecing together things like text and shapes. It looks like this:

```json
{
  "type": "single",
  "submessages": [...]
}
```

`submessages` is a list containing the separate pieces used to build the frame. The submessages are all added and overlayed to the frame in the order they're specified.

#####Submessage Types


```json
{
  "type": "graphics",
  "func": "analog_clock",
  "refresh_interval": 60,
  "params": {
    "size": 16,
    "align": "right"
  }
}
```

There are two base types of submessages:

* `bitmap`: This is used to directly send a pre-rendered bitmap to the display
* `graphics`: This is used to render graphics on the display using the `FlipdotGraphics` class

######Bitmap submessage
This subtype sends a bitmap to the display, starting at the upper left corner. There is no way to position the bitmap with this message type; it is intended to render the whole display at once.
If you need positioning, use the `graphics` submessage type instead.
Here's how it looks:

```json
{
  "type": "bitmap",
  "bitmap": [10, 65, 204, 2]
}
```

To avoid confusion: "bitmap" does *not* refer to an image file in this context. The server does only handle text and bitmaps in a special format.
The bitmap data needs to be formatted as a series of 8-bit values representing the upper 8 pixels of the first (leftmost) column, the lower 8 pixels of the first column, the upper 8 pixels of the second column, etc.
Suppose you have an image that is 4 pixels wide and 16 pixels tall, like this (1 being an active pixel and 0 being an inactive pixel):

```
0110
0101
0101
0011
1101
1111
0011
1000
1001
1000
0101
1010
1101
0010
0000
0100
```

To convert this to the special bitmap format, you need to start in the upper left corner and read the column downwards as two bytes, giving you the binary values `00001101` and `11011000`, or `13` and `216` in decimal.
So the first two bytes of the bitmap are `13` and `216`. Repeat this for every column from left to right and you're done!

#####Graphics submessage
This submessage type renders graphics on the display. They look like this:

```json
{
  "type": "graphics",
  "func": "text",
  "params": {
    "text": "Bewölkt",
    "valign": "middle",
    "x": 20,
    "font": "Arial Narrow Bold",
    "size": 20
  }
}
```

The `func` parameter is used to call the corresponding method of the `FlipdotGraphics` class and the `params` parameter is a mapping of arguments for that function and their values.
*To see the available functions and their parameters, take a look at the `graphics.py` file!*

###Control Messages
Control messages are used to set options in the matrix controller.

**Available options:**

Option|Choices|Description
------|-------|-----------
`backlight`|`true`, `false`|Controls the LED pixel backlight.
`inverting`|`true`, `false`|If set to `true`, the display is inverted. This is done by the matrix controller and has no effect on the data sent by the Python code.
`active`|`true`, `false`|If set to `false`, the display will not update until this parameter is set to `true` again. It will keep receiving bitmap data, it just won't update the flipdots.

**Example:**
```json
{
  "backlight": false,
  "active": false
}
```

###Config query message
This message type returns the specified configuration parameters for the specified displays. The following would return the backlight information for the displays `side` and `front`.

```json
{
  "type": "query-config",
  "displays": ["side", "front"],
  "keys": ["backlight"]
}
```

If `displays` or `keys` are omitted, they default to all displays and all parameters.

###Hardware config query message
This message type returns the hardware configuration, that is all connected displays with their name, resolution and address.

```json
{
    "type": "query-hwconfig"
}
```

###Message query message
This message type returns the current message for the specified displays, or for all displays if `displays` is omitted.

```json
{
  "type": "query-message",
  "displays": ["side"]
}
```

###Bitmap query message
This message type returns the current display bitmap for the specified displays, or for all displays if `displays` is omitted.

```json
{
  "type": "query-bitmap",
  "displays": ["front", "side"]
}
```

##Example message
Here's a complete message for reference and better understanding:

```json
[
  {
    "type": "data",
    "display": "side",
    "message": {
      "type": "sequence",
      "interval": 5.0,
      "messages": [
        {
          "type": "single",
          "submessages": [
            {
              "type": "bitmap",
              "bitmap": [10, 65, 204, 2]
            },
            {
              "type": "graphics",
              "func": "text",
              "params": {
                "text": "Bewölkt",
                "valign": "middle",
                "x": 20,
                "font": "Arial Narrow Bold",
                "size": 20
              }
            },
            {
              "type": "graphics",
              "func": "analog_clock",
              "refresh_interval": 60,
              "params": {
                "size": 16,
                "align": "right"
              }
            }
          ]
        },
        {
          "type": "single",
          "submessages": [
            {
              "type": "graphics",
              "func": "text",
              "params": {
                "text": "Regen",
                "halign": "center",
                "valign": "middle",
                "font": "Arial Narrow Bold",
                "size": 22
              }
            },
            {
              "type": "graphics",
              "func": "analog_clock",
              "refresh_interval": 60,
              "params": {
                "size": 16,
                "align": "right"
              }
            }
          ]
        }
      ]
    }
  },
  {
    "type": "control",
    "display": "side",
    "message": {
      "backlight": true
    }
  },
  {
    "type": "data",
    "display": "panel",
    "message": {
      "type": "single",
      "submessages": [
        {
          "type": "graphics",
          "func": "text",
          "refresh_interval": 60,
          "params": {
            "text": "%H:%M",
            "font": "PixelMix",
            "size": 8,
            "valign": "top",
            "timestring": true
          }
        },
        {
          "type": "graphics",
          "func": "binary_clock",
          "refresh_interval": 60,
          "params": {
            "valign": "bottom"
          }
        }
      ]
    }
  },
  {
    "type": "query-config",
    "displays": ["side", "panel"],
    "keys": ["backlight"]
  }
]
```