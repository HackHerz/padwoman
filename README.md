# Padwoman

![Build Status](https://img.shields.io/docker/cloud/build/hackherz/padwoman) ![Docker Pulls](https://img.shields.io/docker/pulls/hackherz/padwoman) ![Docker Stars](https://img.shields.io/docker/stars/hackherz/padwoman)

Padwoman allows to organise Etherpad Lite groups in a simple and beautiful user interface. By creating the cookies for the etherpad instance it also serves as an authentication service for its pads.

Inspired by [Padman](https://github.com/d120/padman) with redis caching as a workaround to the slow etherpad lite api. But be aware that this is my first Python project.

You can find the Documentation and Screenshots [here](https://padwoman.hackherz.com).


## Features

* Organise Pads into Groups
* Restrict Access to Pads and only allow certain Users or Usergroups to see them
* Make Pads public to allow everyone to edit them if they have the link to the pad
* Enforce or suggest Padnames based on the date for specified groups
* Fill new Pads with a template upon creation
* Make use of caching to speed up the etherpad API requests
