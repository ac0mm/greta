# greta

Greta is a C2 framework written in Python for interacting with remote targets using various forms of traffic. Currently, it supports TCP, UDP, and TLS over TCP with generic open-source callback shell techniques such as Netcat and Openssl. 

## Description

Greta is targeted to help penetration testers evaluate a customer's defenses' ability to detect or respond to various forms of command and control traffic. It additionally logs all commands and target responses per target.

## Table of Contents

  - Requirements
  - Installation
  - Use
  - Three Main Points
  - Why I am interested
  - Areas of Improvement

## Requirements
  - A Linux O/S capable of running Greta
  - python3 ( Tested on python 3.9.2)
  - root permissions (required for UDP traffic)
  - ssl certificate and key
  - A directory called "logs" in the same directory as greta is running out of

## Installation

Note: Use sudo where necessary

1. Clone the repository

   git clone https://github.com/ac0mm/greta.git

2. Change into the greta directory

3. Make a logs directory

     mkdir logs

4. Generate Certificates

    Example Command:
       openssl req -newkey rsa:4096 -x509 -sha256 -days 3650 -nodes -out example.crt -keyout example.key
          
5. Installed!

## Use

  python3 greta_server.py -c example.crt -k example.key

  - Listeners will start up on 50000 (TCP), 50001 (TLS), 50003 (UDP)
  - You won't have any sessions to interact with until you have a shell callback
  - The session token being looked for is the IP address and port ( 192.168.1.3:59821 )
  - Interactive session is just a continuous loop
  - Logs are done by server and by target ( IP:port.log)

## Three Main Points
  - Provide a one-stop framework for catching generic open-source shells
  - Log all interactions with targets
  - Offer encrypted and unencrypted means

## Why I am Interested

Threat actors use various methods for communicating with compromised hosts within a network. As they seek to move away from credentialed or exploit shell-based access to their own tools, network defenders have an opportunity to detect and respond to them. I hope to provide a framework to give penetration testers a single source for interacting with targets with various C2 communication options. 

There has been a shift in threat actors to "live off the land" more, increasing the difficulty for defenders to catch them. The hope is paired with the right penetration tester a campaign of escalation from initial compromise to where more exquisite C2 techniques will be used.

## Areas of Improvement

- C2 Communications Methods
  - DNS
  - ICMP
  - DTLS
  - SMTP
  - IMAP
  - SSH
  - HTTP
  - HTTPS
  - 
- C2 Communications Mode
  - Consistent
  - Random re-sync
  - Beacon
 
- Utility
  - Open Source Shell Command Generator to include redirection of traffic to listening port (IE TLS callback to 443 that is redirected to the standard listening port 50001)
  - Traffic Redirection on Target
    - Open source
      - SSH tunnels
      - openssl tunnels
      - netcat tunnels
      - netsh tunnels
    - Builtin
      - TCP
      - UDP
      - ICMP
  - Uploading and Downloading Files
    - Open source
      - web
      - SSH
      - netcat
      - openssl
    - Builtin
  - Improved Logging
    - Tagging data by target
    - Splitting useful command output
    - directory walks
  - Survey Module
    - Integrating winpeas, linpeas, and other potential useful survey tools
    - directory walks

- User Interface
  - Improved layout
  - Allowing additional terminal windows for interacting with the target
    - Local
    - Remote
  - Better session tracking and interactivity
