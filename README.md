# greta
#
#    / \__
#   (    @\___
#   /         O 
#  /   (_____/
# /_____/ U
#                                ___               
#                               (   )              
#   .--.    ___ .-.      .--.    | |_       .---.  
#  /    \  (   )   \    /    \  (   __)    / .-, \ 
# ;  ,-. '  | ' .-. ;  |  .-. ;  | |      (__) ; | 
# | |  | |  |  / (___) |  | | |  | | ___    .'`  | 
# | |  | |  | |        |  |/  |  | |(   )  / .'| | 
# | |  | |  | |        |  ' _.'  | | | |  | /  | | 
# | '  | |  | |        |  .'.-.  | ' | |  ; |  ; | 
# '  `-' |  | |        '  `-' /  ' `-' ;  ' `-'  | 
#  `.__. | (___)        `.__.'    `.__.   `.__.'_. 
#  ( `-' ;                                         
#   `.__.                                          


Greta was written by Andrew Morrow as part of the first security tool project for Dakota State University, CSC-842 Security Tool Development.

Description

Greta is a penetration testing tool used to catch various C2 callbacks, log commmands and output written in python. The intent is to allow an escalation of testing various C2 methods to determine a defenders ability to detect various methods of command and control.

At this time Greta supports TCP and TLS shells that can be launched by netcat, openssl or /dev/tcp. Ports can be specified but have defaults, at this time the TLS is required.