# Welcome to Padwoman

Padwoman allows to organise Etherpad Lite groups in a simple and beautiful user interface.
By creating the cookies for the etherpad instance it also serves as an authentication service for its pads.

## Features

* Organise Pads into Groups
* Restrict Access to Pads and only allow certain Users or Usergroups to see them
* Make Pads public to allow everyone to edit them if they have the link to the pad
* Enforce or suggest Padnames based on the date for specified groups
* Fill new Pads with a template upon creation
* Make use of caching to speed up the etherpad API requests


## Screenshots

![Login](images/screen-0.png)
*Login to Padwoman*. Currently the only supported authentication backend is LDAP. The Groups which the user is able to access is configured manually or through membership in specified LDAP-Groups.

![List of Pads](images/screen-1.png)
*List of Pads*. Pads are listed per Group and sorted by Modification date. As much of this as possible is cached to allow for faster loadtimes. The icon on the left hand side allows to switch pads between private and public access. 

![New Pad](images/screen-2.png)
*New Pad*. Upon Pad-creation you can specify if you want to use the Group-specific template for the new pad. Padwoman can be configured to always enforce this option. The same applies to the name of the pad.

