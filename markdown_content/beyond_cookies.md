# Beyond Cookies

## Are You Aware of How Much Data Your Website is Really Collecting?

# Introduction

Privacy regulations like GDPR and CCPA have forced companies to be transparent about cookie usage. But what if the most invasive tracking on your website doesn't use cookies at all? Modern browsers expose a massive amount of data that can be used to create a unique ‘fingerprint’ of every user, often without their consent. This practice, known as cookieless tracking, presents a significant and often overlooked **business risk**, from violating user trust to running afoul of privacy laws. This post will show you the techniques being used and, more importantly, what it means for your business.

All code examples are available in this [GitHub repository](https://github.com/user-at-host/Websites-Data-Collection-Examples).

# CIR - Cookie-less Identity Resolution

**CIR (Cookie-less Identity Resolution)** is a method of web data collection that doesn't involve cookies or any other form of persistent storage in the browser. Instead, a website collects every possible piece of data about a user's device and configuration to create a unique ‘fingerprint’.
This fingerprint can be cross-referenced later to identify returning users. While this technique is often used for legitimate purposes like fraud and bot detection, its applications extend beyond security into tracking and analytics. The browsers we use provide a vast amount of information about our hardware and software; the unique combination of these data points creates the fingerprint.

# Hardware Enumeration

JavaScript is a powerful tool that allows developers to collect extensive information about a user's device. The following examples are based on techniques seen on some of the largest web applications in use today.

## GPU Fingerprint

Every visitor to your site has a unique combination of hardware and software. Third-party scripts included in your website (like those for analytics or advertising) can exploit this to create a highly accurate user fingerprint. This means user activity can be tracked across sessions and even across different websites, potentially without their knowledge and outside the scope of your company's privacy policy.

Every device, even the smallest laptop, has a GPU. While the GPU model itself is a useful data point, websites use more advanced techniques to fingerprint users. Modern browsers support **WebGL**, an API that allows for rendering graphics directly in the browser without additional software. This same technology can be exploited for fingerprinting.

Several factors contribute to a unique WebGL fingerprint, including the **GPU model**, **browser version**, **operating system**, and **graphics drivers**.

### GPU Model

The following code uses the WebGL API to retrieve the vendor and model of the user's GPU. To see a live example, visit [this page](/examples/gpu_vendor_and_model.html) which shows you the GPU information of your machine.

The full code of the page can be found [here]().