CHANGE LOG
==========

3.3.3
-----
- Add marathon-lb labels to app definitions

3.3.2
-----
- ensure int values for health check timeouts

3.3.1
-----
- allow health check timeouts to be configurable

3.3.0
-----
- added description field
- ensure org change doesn't result in 404 if org permssions are good
- ensure all marathon calls are done via celery
- re-introduce log driver
- added app restart webhook
- UI improvements + tweaks
- increase graceperiod for when apps start with healthchecks
- small docker image with python:2.7.11-alpine

3.2.11
------
- add hypothesis testing
- upgrade to latest version of grappelli (fixes delete bug)

3.2.10
-----
- remove freebasics

3.2.9
-----
- add marathon labels

3.2.8
-----
- ensure cards can be clicked properly
- cleanup old settings
- remove dependency of ws4redis
- fix delete of app
- allow hub domain to be specified in ENV

3.2.7
-----
- specify user/pass env for smtp

3.2.6
-----
- expose SMPT settings as env variables

3.2.5
-----
- user json serializer for email

3.2.4
-----
- ensure bool env (DEBUG) is read correctly

3.2.3
-----
- enable restart button
- allow debug to be set using env variable

3.2.2
-----
- update UI fields on homepage
- Fix redirect issue when logging in

3.2.1
-----
- fix password reset
- add domain URLs for docker controllers
- tweaks to the UI

3.2.0
-----
- Added single-sign-on support for Molo
- Enable email login + password reset

3.1.1
-----
- Fix for marathon cmd when blank

3.1.0
-----
- Docker container now fully functional
- Use Environment variables to specify settings
- Add volume support use xylem plugin
- Allow marathon cmd to be blank for docker controller

3.0.5
-----
- ensure all static files are packaged

3.0.4
-----
- use json serialiser for celery

3.0.3
-----
- fix E402 in latest flake8 version

3.0.2
-----
- update celery to be inline with 3.1.19

3.0.1
-----
- make settings variables configurable via ENV

3.0.0
-----
- release as pip installable
- refactored namespace to use mc2
- allow deleting of app

2.0.0
-----
- Initial 2.0 release (non-backwards compatible)
- refactored code structure
- introduced controller base
- simplified model definitions

< 2.0
-----
- Mission Control for Universal Core
