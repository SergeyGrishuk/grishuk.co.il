There are many great network scanners, with `Nmap` being the best in the right hands. 
While techniques exist to anonymize scanning, they often require complicated manual setup, 
making them difficult to integrate into an automated production pipeline.

Dark Scan solves this problem. 
It is a zero-configuration tool that scans targets through the Tor network out of the box. 
It achieves this by automatically configuring all necessary Tor settings on each run and shipping with a pre-compiled, 
standalone Tor binary. Dark Scan can also scan targets on the Tor network itself, such as `.onion` services.
