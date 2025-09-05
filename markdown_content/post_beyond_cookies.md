
## Introduction

Privacy regulations like GDPR and CCPA have forced companies to be transparent about cookie usage. But what if the most invasive tracking on your website doesn't use cookies at all? Modern browsers expose a massive amount of data that can be used to create a unique ‘fingerprint’ of every user, often without their consent. This practice, known as cookieless tracking, presents a significant and often overlooked **business risk**, from violating user trust to running afoul of privacy laws. This post will show you the techniques being used and, more importantly, what it means for your business.

All code examples are available in this [GitHub repository](https://github.com/user-at-host/Websites-Data-Collection-Examples).

## CIR - Cookie-less Identity Resolution

**CIR (Cookie-less Identity Resolution)** is a method of web data collection that doesn't involve cookies or any other form of persistent storage in the browser. Instead, a website collects every possible piece of data about a user's device and configuration to create a unique ‘fingerprint’.
This fingerprint can be cross-referenced later to identify returning users. While this technique is often used for legitimate purposes like fraud and bot detection, its applications extend beyond security into tracking and analytics. The browsers we use provide a vast amount of information about our hardware and software; the unique combination of these data points creates the fingerprint.

## Hardware Enumeration

JavaScript is a powerful tool that allows developers to collect extensive information about a user's device. The following examples are based on techniques seen on some of the largest web applications in use today.

### GPU Fingerprint

Every visitor to your site has a unique combination of hardware and software. Third-party scripts included in your website (like those for analytics or advertising) can exploit this to create a highly accurate user fingerprint. This means user activity can be tracked across sessions and even across different websites, potentially without their knowledge and outside the scope of your company's privacy policy.

Every device, even the smallest laptop, has a GPU. While the GPU model itself is a useful data point, websites use more advanced techniques to fingerprint users. Modern browsers support **WebGL**, an API that allows for rendering graphics directly in the browser without additional software. This same technology can be exploited for fingerprinting.

Several factors contribute to a unique WebGL fingerprint, including the **GPU model**, **browser version**, **operating system**, and **graphics drivers**.

#### GPU Model

The following code uses the WebGL API to retrieve the vendor and model of the user's GPU. To see a live example, visit [this page](/examples/gpu_vendor_and_model.html) which shows you the GPU information of your machine.

The full code of the page can be found [here](https://github.com/user-at-host/Websites-Data-Collection-Examples/blob/main/gpu_vendor_and_model.html).

```js
const canvas = document.getElementById('webgl-canvas');

const n = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

const o = {};

let i;

(i = n.getExtension("WEBGL_debug_renderer_info")) &&
    (o.UNMASKED_RENDERER_WEBGL = n.getParameter(i.UNMASKED_RENDERER_WEBGL),
        o.UNMASKED_VENDOR_WEBGL = n.getParameter(i.UNMASKED_VENDOR_WEBGL));

console.log(o.UNMASKED_VENDOR_WEBGL);
console.log(o.UNMASKED_RENDERER_WEBGL);
```

#### Render Fingerprinting

Websites use the `<canvas>` element to draw a specific, predetermined image using WebGL. This rendered image is then converted to a hash value, which serves as the fingerprint. The graphics drawn for this purpose are typically a combination of shapes, lines, and text with specific properties.

The code below draws a Pac-Man-like shape.

[Visit the render fingerprinting example](/examples/render_fingerprint.html) page to see a live example. A full HTML example can be found [here](https://github.com/user-at-host/Websites-Data-Collection-Examples/blob/main/render-fingerprint.html).

![Packman style render](/static/pacman.png)

```js
const canvas = document.createElement("canvas");
canvas.width = 256;
canvas.height = 128;
const p = canvas.getContext("webgl2") || canvas.getContext("webgl");


p.viewport(0, 0, p.drawingBufferWidth, p.drawingBufferHeight);
const m = p.createProgram();
const x = p.createShader(p.VERTEX_SHADER);
p.shaderSource(x, "attribute vec2 attrVertex;attribute vec4 attrColor;varying vec4 varyinColor;uniform mat4 transform;void main(){varyinColor=attrColor;gl_Position=transform*vec4(attrVertex,0,1);}");
p.compileShader(x);
p.attachShader(m, x);

const v = p.createShader(p.FRAGMENT_SHADER);
p.shaderSource(v, "precision mediump float;varying vec4 varyinColor;void main(){gl_FragColor=varyinColor;}");
p.compileShader(v);
p.attachShader(m, v);

p.linkProgram(m);
p.useProgram(m);

m.vertexPosAttrib = p.getAttribLocation(m, "attrVertex");
m.colorAttrib = p.getAttribLocation(m, "attrColor");
p.enableVertexAttribArray(m.vertexPosAttrib);
p.enableVertexAttribArray(m.colorAttrib);

m.transform = p.getUniformLocation(m, "transform");
p.uniformMatrix4fv(m.transform, false, [1.5, 0, 0, 0, 0, 1.5, 0, 0, 0, 0, 1, 0, 0.5, 0, 0, 1]);

const b = [];
const S = 128;
for (let C = 0; C < S; C++) {
    const L = (45 + C / S * 270) / 360 * 2 * Math.PI;
    const R = (45 + (C + 1) / S * 270) / 360 * 2 * Math.PI;
    b.push(-.25, 0, 1, .7, 0, 1);
    b.push(-.25 + .5 * Math.cos(L), .5 * Math.sin(L), 2, 1 - C / S, 0, 1);
    b.push(-.25 + .5 * Math.cos(R), .5 * Math.sin(R), 1, 1 - (C + 1) / S, 0, 1);
}
const T = new Float32Array(b);
const w = p.createBuffer();
p.bindBuffer(p.ARRAY_BUFFER, w);
p.bufferData(p.ARRAY_BUFFER, T, p.STATIC_DRAW);
p.vertexAttribPointer(m.vertexPosAttrib, 2, p.FLOAT, !1, 24, 0);
p.vertexAttribPointer(m.colorAttrib, 4, p.FLOAT, !1, 24, 8);

p.drawArrays(p.TRIANGLES, 0, T.length / 6);

h.appendChild(p.canvas);

const M = new Uint8Array(p.canvas.width * p.canvas.height * 4);
p.readPixels(0, 0, p.canvas.width, p.canvas.height, p.RGBA, p.UNSIGNED_BYTE, M);
const y = JSON.stringify(M).replace(/,?"[0-9]+":/g, "");
f.textContent = md5(y);
```

Each device renders the image slightly differently due to variations in hardware and software. These minute differences produce a unique hash, creating a highly effective fingerprint.

**The Risk:** If your website facilitates this kind of tracking, you lose control over user data. This can damage your brand's reputation and create legal liability if a third-party script is misusing this data.

### CPU and Memory

Browsers can also collect data about the system's CPU and memory. Although this information is less precise than GPU fingerprinting, it's a valuable data point when combined with other metrics.

**Business Implication:** Even seemingly minor data points contribute to a user's unique fingerprint. While CPU and memory data alone are not enough to identify a user, they are valuable pieces of the puzzle for third-party scripts aiming to build a comprehensive profile of your visitors.

#### CPU

JavaScript can access the number of logical CPU cores via the `navigator.hardwareConcurrency` property.
- This returns an integer representing the number of logical processor cores available to the browser.
- There is no direct web API to get the CPU model, frequency, or architecture.

#### Memory

A browser can approximate the amount of RAM on a device using the `navigator.deviceMemory` property.

- This is a non-standard feature primarily supported by Chrome-based browsers.
- It returns an approximate value in gigabytes, rounded to the nearest power of two: `0.25`, `0.5`, `1`, `2`, `4`, or `8`.
- The value is capped at `8`, so a device with 16 GB of RAM will still report `8`.

[Here](/examples/cpu_and_memory.html) is an example page that collects both CPU and Memory data. A live version of the page is [here](https://github.com/user-at-host/Websites-Data-Collection-Examples/blob/main/cpu_and_memory.html).

**The Risk:** On their own, these data points are a low-level risk. However, when combined with GPU, display, and font data, they contribute to a highly accurate fingerprint that can track users without their explicit consent. This "death by a thousand cuts" approach to data collection can create a significant privacy liability for your business.

### Media Devices

**Business Implication:** When a website requests access to a user's camera or microphone, it's a moment of critical trust. If a third-party script on your site triggers this permission prompt unexpectedly, it can alarm users and severely damage their perception of your brand's security and integrity.

Components like microphones, cameras, and speakers are also used for fingerprinting. Those are also used for fingerprinting. Each one of them has its own model and device ID. They can be accessed via the navigator.`mediaDevices.enumerateDevices()` method. It does require the user’s permission, but when granted it allows to get all the data about the devices. Below is an example.

Visit [this](/examples/list_media_devices.html) page to see a live example. The full code of the page can be found [here](https://github.com/user-at-host/Websites-Data-Collection-Examples/blob/main/list-media-devices.html).

```
--------------------------------
Microphone 1:
Label: Headset Microphone (Logitech G PRO X)
Kind: audioinput
Device ID: 4/G8pYd2V5xS6zF9aB3cE7hJ1kM4n7rT0uW3xZ5+A/C=
--------------------------------
Camera 1:
Label: Logitech BRIO
Kind: videoinput
Device ID: mNbVcXzLkJhGfDsApOiUyTrEwQqMnBvCxZlKjHgFdSaPoIuYtReWq12=
--------------------------------
Speaker 1:
Label: Headset Earphone (Logitech G PRO X)
Kind: audiooutput
Device ID: 9sR6qP0oN3mL5kI8jB1fD4eG7hA2c5gI0lO4m7n9qS=
```

While the device label stays the same all the time, the device ID is not. It is different for each  website you visit, so each website will see a different device ID for the same camera. microphone and speakers. Also a cache clean will reset it. It is done for privacy reasons.

**The Risk:** The list of a user's specific media devices (e.g., "Logitech BRIO," "Logitech G PRO X") is itself a powerful fingerprinting vector. The risk is twofold: you are **scaring away customers** with unexpected permission prompts while simultaneously **leaking unique identifying information** to third-party scripts.


## Display Enumeration

**Business Implication:** While screen details are essential for responsive web design and legitimate bot detection, this rich dataset is a goldmine for fingerprinting services. Every detail, from screen resolution to the exact browser window size, helps third parties create a more unique and persistent profile of your users.

In addition to core hardware data, websites collect extensive information about the user's display. This includes screen resolution, browser window size, color depth, and pixel density. While the legitimate reason for collecting this data is often bot and automation detection, it becomes a crucial part of the user's fingerprint when combined with other data points.

The display information available via JavaScript includes the following properties.

- `window.screen` - The main object.
  - `window.screen.width` and `window.screen.height` - The resolution of the monitor.
  - `window.screen.availWidth` and `window.screen.availHeight` - The width and height available to the browser window (Resolution minus the task bar).
  - `window.screen.colorDepth` and `window.screen.pixelDepth` - The number of bits the screen uses to represent color.
  - `window.screen.orientation.type` - Detects the orientation of the device (landscape or portrait).
- `window.devicePixelRatio` - Indicates the ratio of the screen's physical pixels to its logical (CSS) pixels. A value of 2 means there are two physical pixels for every one CSS pixel, which is typical for Retina displays.
- `window.innerWidth` and `window.innerHeight` - The actual dimensions of the browser's viewport (the space available for the web page), excluding the browser's UI like the URL bar, bookmarks bar, or open DevTools.

The last two properties, `window.innerWidth` and `window.innerHeight`, can be compared against `window.screen.availWidth` and `window.screen.availHeight` to infer whether the user has DevTools docked to the side or bottom of their browser.

An example page is available [here](/examples/display_info.html). The full code that shows all the display data can be found [here](https://github.com/user-at-host/Websites-Data-Collection-Examples/blob/main/display_info.html).

**The Risk:** You may be using a service for a legitimate purpose (like fraud detection) while that same service is also using the collected data for cross-site tracking, making your business an unwitting accomplice in a larger surveillance network. This creates a supply chain risk where a vendor's data practices become your liability.


## Networking

**Business Implication:** Users who employ VPNs or proxies are your most privacy-conscious audience. They are actively trying to protect their identity. If your website contains technology that bypasses these protections, it can be seen as a hostile action that fundamentally breaks user trust and destroys your credibility.

The usage of VPNs and proxies is very common. There are cases when the VPN or proxy are not set-up correctly, which results in a leak of the real IP address. It’s much more common than you would have expected. One way to detect usage of a VPN or proxy is via the WebRTC protocol.

WebRTC is used for real-time communication between browsers but it also can be used to leak the actual IP address of the user, as not all VPNs and proxies take care of this kind of connection. WebRTC is supported and enabled by default in all browsers.

[This](/examples/webrtc_ip_finder.html) page shows an example of how WebRTC is used to get the IP address of the user. A full HTML and JavaScript code can be found [here](https://github.com/user-at-host/Websites-Data-Collection-Examples/blob/main/webrtc_ip_finder.html).

**The Risk:** The risk here is severe. A WebRTC leak can expose a user's true IP address, completely nullifying their privacy measures. If your website is the source of such a leak, you could be held responsible for exposing sensitive user information, leading to significant brand damage and potential legal consequences.


## Summary: Your Website is a Black Box

As we've seen, a vast amount of user data can be collected silently, bypassing cookie consent banners. The modern website is a complex assembly of first-party code and dozens of third-party scripts, and it's nearly impossible to know what data is leaving your user's browser and where it's going.

**You cannot protect what you cannot see.**

If you are unsure exactly what data your website or application is collecting, I can help. I provide **comprehensive privacy and security audits** to identify these hidden tracking techniques, analyze the behavior of third-party scripts, and give you a clear picture of your data risk.

**Contact me for a [confidential consultation](/#contact) to understand and control your website's data footprint.**
