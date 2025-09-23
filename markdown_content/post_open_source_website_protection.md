# Open Source Websites Protection


## Introduction

In today's digital economy, robust website security isn't a luxury, it's a necessity. However, for many small and medium sized businesses, the enterprise security market presents a significant barrier. With solutions often carrying five or six figure price tags, comprehensive protection can feel out of reach. But what if you could build a formidable defense without the enterprise budget?

The world of free and open-source software (`FOSS`) offers powerful, battle tested tools that can secure your web applications effectively. This post will serve as a practical guide to implementing a multi layered security strategy using these tools. We will move from the perimeter to the core of your application, covering defenses at the network, behavioral, and application layers to create a resilient and cost-effective security posture.

There are many free and open source tools that are used to protect websites from various types of attacks.
In this post I will demonstrate some of them.

All of the examples throughout the post are executed on this website (grishuk.co.il).

<!-- TODO: Update the intro once the post gets more text according to the text -->
<!-- TODO: Fact check and spell/grammar check -->


## Defense Layers

The defenses can be divided into several layers, in the post I will address the **network**, ***behavior*** and **application** layers.
Each layer of defense has it's own area of responsibility.

*Although behavior is not an actual technical layer I still treat it as one for this post.*

### Network Layer

The network layer deals with raw IP addresses and port numbers. Tools such as firewalls, `fail2ban` and nginx's rate limits are applied in this layer. It is used to control the traffic on the most basic (and powerful in cases) level.


### Behavior Layer

This layer is applied to the behavior of the users/clients and their incoming requests. As an example, a user that accidentally requested a non existent page is not a big deal, but a client that enumerates the website and generates hundreds or thousands of 404 requests might cause slower response times or even find an actual vulnerable page or parameter on the website.


### Application Layer

The application layer deals with the actual data that the web server receives. This is the place for tools such as WAFs (Web Application Firewall) to take action. This layer is used to prevent the actual attacks that involve malicious payloads, injections, executions, inclusions and so on.


*When applying the defenses it is important to consider the actual usage and use cases of the website in order to improve the security posture of the side while not blocking legitimate users and traffic. Those considerations are making the implementation of the security measures a little bit more "tricky".*

<!-- TODO: Fact check and spell/grammar check -->


## IP Dynamic Blocking

If you ever went over the access logs of your web server, you saw requests to non existing pages (404). Those requests are probably initiated by bots or automated tools which are used to enumerate and discover possible vulnerabilities in websites. To prevent such kinds of enumerations against your website you can simply block the requests on a network layer via the system firewall. This will not only block the HTTP requests but all the incoming traffic from the malicious IP address thus preventing any kind of attack originating from it.

A simple and know tool that provides such kind of functionality is `fail2ban`. It is available straight from the standard repositories of most Linux distributions. `fail2ban` allows to create custom rules for any kind of use case. In the example bellow I set it to monitor the access logs of my website and block the IP addresses that generate too many 404 status codes in a time frame of 10 minutes.

First, I will create a new filter for `fail2ban` which will detect the 404 requests. The filter is located in a separate file named `nginx-404.conf` under the `/etc/fail2ban/filter.d/` directory. The filter looks as follows:

```conf
[Definition]
failregex = ^<HOST> -.*"GET.*HTTP/.*" 404
```

It is a simple regular expression that catches 404 requests.
The next step is to tell `fail2ban` to actually monitor the `access.log` file, this is done via adding a new entry to the main jail file of `fail2ban`. The bellow section is an example for such an entry. It tells `fail2ban` to monitor the `/var/log/nginx/access.log` file and block each IP that has over 6 (in this example) 404 requests.

*A 'jail' is a `fail2ban` term for a set of rules that combines a filter with actions for a specific service.*

```conf
[nginx-404]
enabled  = true
port     = http,https
filter   = nginx-404
logpath  = /var/log/nginx/access.log
maxretry = 6
```

By default, `fail2ban` monitors the logs for the past 10 minutes and blocks a host (IP address) for 10 minutes. Those settings can also be configured in the jail file of `fail2ban` which usually located under `/etc/fail2ban/jail.local`. Bellow is an example from the file.

```conf
# "bantime" is the amount of time that a host is banned, integer in seconds or
# time abbreviation format (m - minutes, h - hours, d - days, w - weeks, mo - months, y - years).
# This is to consider as an initial time if bantime.increment gets enabled.
bantime  = 10m

# A host is banned if it has generated "maxretry" during the last "findtime"
# seconds.
findtime = 10m

# "maxretry" is the number of failures before a host get banned.
maxretry = 5
```

On this server, `fail2ban` is configured for 3 days (on the day of writing this) and it already banned a number of IP address. The banned addresses can be found in the `/var/log/fail2ban.log` log file.

```log
2025-09-21 03:26:45,562 fail2ban.filter         [9229]: INFO    [nginx-404] Found 172.189.56.43 - 2025-09-21 03:26:45
2025-09-21 08:59:47,727 fail2ban.filter         [9229]: INFO    [nginx-404] Found 198.235.24.166 - 2025-09-21 08:59:47
2025-09-21 14:23:55,024 fail2ban.filter         [9229]: INFO    [nginx-404] Found 104.210.140.129 - 2025-09-21 14:23:54
2025-09-21 14:23:55,066 fail2ban.filter         [9229]: INFO    [nginx-404] Found 104.210.140.129 - 2025-09-21 14:23:55
2025-09-22 04:35:43,075 fail2ban.filter         [9229]: INFO    [nginx-404] Found 17.241.75.211 - 2025-09-22 04:35:42
2025-09-22 06:08:01,801 fail2ban.filter         [9229]: INFO    [nginx-404] Found 185.203.132.199 - 2025-09-22 06:08:01
2025-09-22 06:08:14,235 fail2ban.filter         [9229]: INFO    [nginx-404] Found 185.203.132.199 - 2025-09-22 06:08:14
2025-09-22 09:44:03,468 fail2ban.filter         [9229]: INFO    [nginx-404] Found 104.210.140.134 - 2025-09-22 09:44:03
2025-09-22 09:44:05,072 fail2ban.filter         [9229]: INFO    [nginx-404] Found 104.210.140.134 - 2025-09-22 09:44:05
2025-09-22 10:58:58,104 fail2ban.filter         [9229]: INFO    [nginx-404] Found 79.177.133.201 - 2025-09-22 10:58:58
2025-09-22 10:58:58,105 fail2ban.filter         [9229]: INFO    [nginx-404] Found 79.177.133.201 - 2025-09-22 10:58:58
2025-09-22 10:58:58,107 fail2ban.filter         [9229]: INFO    [nginx-404] Found 79.177.133.201 - 2025-09-22 10:58:58
2025-09-22 12:30:07,319 fail2ban.filter         [9229]: INFO    [sshd] Found 79.177.133.201 - 2025-09-22 12:30:06
2025-09-22 15:53:23,906 fail2ban.filter         [9229]: INFO    [nginx-404] Found 66.249.64.173 - 2025-09-22 15:53:23
2025-09-22 22:35:33,293 fail2ban.filter         [9229]: INFO    [nginx-404] Found 4.227.36.13 - 2025-09-22 22:35:33
2025-09-23 06:07:59,045 fail2ban.filter         [9229]: INFO    [nginx-404] Found 104.210.140.139 - 2025-09-23 06:07:58
2025-09-23 06:08:00,801 fail2ban.filter         [9229]: INFO    [nginx-404] Found 104.210.140.139 - 2025-09-23 06:08:00
2025-09-23 08:07:43,341 fail2ban.filter         [9229]: INFO    [nginx-404] Found 4.227.36.41 - 2025-09-23 08:07:43
```

## Rate Limiting

Nginx is a powerful HTTP server and reverse proxy. In my case I use it as a reverse proxy for my FastAPI application which serves the website. One of the built is capabilities of nginx is rate limits. Rate limits are useful as a protection against enumeration and DDoS attacks. In case a client sends too many requests in a given time period it will get a response from `nginx` that prohibits the access to the actual page. In case of this website, I set it to response with a status of 429 which means "Too Many Requests". 

To enable rate limits in `nginx` simply add few lines to the configuration files. The first one is the creation of a "zone", which is an abstract name for a set of configurations. Below is an example from the main configuration file of `nginx` (`/etc/nginx/nginx.conf`).

```conf
http {
    limit_req_zone $binary_remote_addr zone=mylimit:10m rate=10r/s;
}
```

It creates a new zone with the name `mylimit` with a size of 10 MB and sets a rate limit of 10 requests per second. Once the zone is created, it has to be applied to either a `server` or a `location` block.

```conf
server {
    limit_req zone=mylimit burst=10 nodelay;
    limit_req_status 429;
}
```

The above configuration uses the `mylimit` zone and adds a burst of 10 requests which are processed with no delay. The burst is used allow few extra requests for a client, it is useful for the initial load of a page which usually send more than one request to the server (styles, favicon, scripts, etc.).

<!-- TODO: Fact check and spell/grammar check -->


## Web Application Security

While the previous layers are a great foundation for the defense mechanisms, they still are not complete. The website still might be vulnerable to application level attacks. This is the place where a solution such as a WAF takes place. It is designed to operate on the application level and inspect the requests for possible signs of attacks. Each requests passes through the WAF and checked for malicious payloads or activity, if such a request is detected it gets blocked. In my case (grishuk.co.il) I went with a tool called [ModSecurity](https://github.com/owasp-modsecurity/ModSecurity) which is an open source WAF that integrates with knows HTTP servers (`nginx`, `apache`). The basic (core) rules for `ModSecurity` are available in the official [GitHub repository](https://github.com/coreruleset/coreruleset).

It is important to not enable the blocking of the requests immediately after the installation. Instead, let the WAF operate in a "neutral" mode for a period of time, after which inspect the logs to make sure no valid traffic gets blocked.

In the case of `nginx`, `ModSecurity` is used as a loadable module, all you need to do (after the installation) is to add few lines to the configuration file of `nginx`. At the top of the main `nginx` configuration file load the `ModSecurity` module.

```conf
load_module modules/ngx_http_modsecurity_module.so;
```

And in the `server` block enable `ModSecurity` and point it to the file containing the reference to the rules of `coreruleset`.

```conf
server {
    modsecurity on;
    modsecurity_rules_file /etc/nginx/modsec/main.conf;
}
```

Before actually restarting the `nginx` server, make sure that the `SecRuleEngine` setting is set to `DetectionOnly`. Once you are satisfied with the results of the WAF, set it to `On`.

The logs of the matched rules are located in the `/var/log/modsec_audit.log` file. Bello is an example of such a match.

```log
ModSecurity: Warning. Matched "Operator `PmFromFile' with parameter `scanners-user-agents.data' against variable `REQUEST_HEADERS:User-Agent' (Value: `Mozilla/5.0 zgrab/0.x' ) [file "/etc/nginx/modsec/coreruleset/rules/REQUEST-913-SCANNER-DETECTION.conf"] [line "38"] [id "913100"] [rev ""] [msg "Found User-Agent associated with security scanner"] [data "Matched Data: zgrab found within REQUEST_HEADERS:User-Agent: Mozilla/5.0 zgrab/0.x"] [severity "2"] [ver "OWASP_CRS/4.19.0-dev"] [maturity "0"] [accuracy "0"] [tag "application-multi"] [tag "language-multi"] [tag "platform-multi"] [tag "attack-reputation-scanner"] [tag "paranoia-level/1"] [tag "OWASP_CRS"] [tag "OWASP_CRS/SCANNER-DETECTION"] [tag "capec/1000/118/224/541/310"] [hostname "grishuk.co.il"] [uri "/"] [unique_id "175859323163.835235"] [ref "o12,5v47,21"]
ModSecurity: Warning. Matched "Operator `Ge' with parameter `5' against variable `TX:BLOCKING_INBOUND_ANOMALY_SCORE' (Value: `5' ) [file "/etc/nginx/modsec/coreruleset/rules/REQUEST-949-BLOCKING-EVALUATION.conf"] [line "222"] [id "949110"] [rev ""] [msg "Inbound Anomaly Score Exceeded (Total Score: 5)"] [data ""] [severity "0"] [ver "OWASP_CRS/4.19.0-dev"] [maturity "0"] [accuracy "0"] [tag "anomaly-evaluation"] [tag "OWASP_CRS"] [hostname "grishuk.co.il"] [uri "/"] [unique_id "175859323163.835235"] [ref ""]
```


## Running Attacks

Now that the security measures are in place, it is time for the "fun part". I am going to launch few simple attacks against my webserver to demonstrate it's abilities to stand against them.

### Enumeration

There are many enumeration tools available, `birb`, `gobuster` and `ffuf` are just a few. Using `ffuf` I will run an enumeration against my server, for the demo of the attack I will use the `common.txt` file from [SecLists](https://github.com/danielmiessler/SecLists/blob/master/Discovery/Web-Content/common.txt) repository.

```sh
ffuf -w common.txt -u https://grishuk.co.il/FUZZ
```

```


        /'___\  /'___\           /'___\
       /\ \__/ /\ \__/  __  __  /\ \__/
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/
         \ \_\   \ \_\  \ \____/  \ \_\
          \/_/    \/_/   \/___/    \/_/

       v2.1.0
________________________________________________

 :: Method           : GET
 :: URL              : https://grishuk.co.il/FUZZ
 :: Wordlist         : FUZZ: /root/ffuf/common.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
________________________________________________

:: Progress: [485/4750] :: Job [1/1] :: 2 req/sec :: Duration: [0:02:38] :: Errors: 359 ::
```

As seen in the output of `ffuf`, most of the requested pages generate an error (359). This error is a result of a firewall block created by `fail2ban`. Bellow is an output of the `iptables` rules from the web server.

```
Chain INPUT (policy ACCEPT 326K packets, 1129M bytes)
 pkts bytes target     prot opt in     out     source               destination
59418 4714K f2b-nginx-404  tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            multiport dports 80,443
50370   65M f2b-sshd   tcp  --  *      *       0.0.0.0/0            0.0.0.0/0            multiport dports 1322

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination

Chain f2b-nginx-404 (1 references)
 pkts bytes target     prot opt in     out     source               destination
 5768  404K REJECT     all  --  *      *       64.176.173.15        0.0.0.0/0            reject-with icmp-port-unreachable
22024 2458K RETURN     all  --  *      *       0.0.0.0/0            0.0.0.0/0

Chain f2b-sshd (1 references)
 pkts bytes target     prot opt in     out     source               destination
50370   65M RETURN     all  --  *      *       0.0.0.0/0            0.0.0.0/0
```

As you can see, in the `f2b-nginx-404` chain, the `64.176.173.15` IP address gets rejected. This is the IP address of the server that I am using for the attack.


### DoS (Denial of Service)

There are many types of DoS and DDoS attacks, the measures implemented in the examples above provide defenses against some of them. Specifically, the rate limits are created to protect the `FastAPI` application from extensive load which can lead to increased usage of memory, CPU, disk, database and etc.

For the attack I will be using a tool called `hey` which is a replacement for `ab` (according to the [GitHub repository](https://github.com/rakyll/hey)). This tool is used to generate a lot of HTTP request in and send them to a target website.

All for testing purposes of course ;)

I am using the following command to generate 5000 requests against my server.

```sh
hey -n 5000 -c 100 https://grishuk.co.il/
```

The `-n` option specifies the number of requests and the `-c` option is used to specify the number of workers.

The results of the execution are as follows:

```
Status code distribution:
  [200] 148 responses
  [429] 4852 responses
```

Out of the 5000 requests only 148 actually got a response, this means that 97.04% of the requests got blocked. They got a response code of 429 from `nginx` which means that they did not get to the `FastAPI` application behind it.


### Application Protection

The third layer of the defenses on the server is the WAF. 


## Conclusion

