# Changelog
All notable changes to this project will be documented in this file. See [conventional commits](https://www.conventionalcommits.org/) for commit guidelines.

- - -
## v0.7.0 - 2023-11-14
#### Bug Fixes
- **(deps)** bump numpy from 1.26.1 to 1.26.2 - (fa63298) - dependabot[bot]
#### Continuous Integration
- **(deps)** bump armakuni/github-actions from 0.18.2 to 0.19.0 - (24be854) - dependabot[bot]
- Remove tests from pipeline - (df00f80) - Billie Thompson
#### Features
- Handle long sentences by splitting them - (8b86020) - Billie Thompson
#### Tests
- Add tests to pipeline - (c137372) - Billie Thompson

- - -

## v0.6.0 - 2023-11-11
#### Features
- Cache sylable counting - (797c0e6) - Billie Thompson

- - -

## v0.5.1 - 2023-11-11
#### Bug Fixes
- Add ffmpeg - (88a26f9) - Billie Thompson
#### Build system
- **(deps-dev)** bump mypy from 1.6.1 to 1.7.0 - (f4cf61b) - dependabot[bot]
#### Refactoring
- Delete unused tar at end of ffmpeg install - (b452197) - Billie Thompson

- - -

## v0.5.0 - 2023-11-10
#### Bug Fixes
- Disable the small model - (cda5d32) - Billie Thompson
#### Features
- Allow the creation of prompts by voice - (1b2c854) - Billie Thompson
#### Refactoring
- Tidy up preprocess - (8f69ce7) - Billie Thompson

- - -

## v0.4.0 - 2023-11-10
#### Features
- Denoise audio - (0a296a6) - Billie Thompson

- - -

## v0.3.4 - 2023-11-10
#### Bug Fixes
- reduce pause - (3e59cff) - Billie Thompson
#### Build system
- **(deps-dev)** bump ruff from 0.1.4 to 0.1.5 - (5af4a09) - dependabot[bot]

- - -

## v0.3.3 - 2023-11-09
#### Bug Fixes
- Raise on bad response - (ea8117c) - Billie Thompson

- - -

## v0.3.2 - 2023-11-09
#### Bug Fixes
- formatting - (9d37e11) - Billie Thompson
- Add a squash in and make the output less noisy - (a653841) - Billie Thompson
#### Refactoring
- formatting - (73bfd64) - Billie Thompson

- - -

## v0.3.1 - 2023-11-09
#### Bug Fixes
- Add torch audio - (5eb12a5) - Billie Thompson

- - -

## v0.3.0 - 2023-11-08
#### Bug Fixes
- Remove unused dependency - (7e1eb85) - Billie Thompson
- Do not clear print line - (946cfa7) - Billie Thompson
- Install and then remove wget when installing cuda - (2d210ae) - Billie Thompson
- Remove some unused deps to reduce the image weight - (43dbaa3) - Billie Thompson
#### Features
- Use small models on CPU - (0a9f75c) - Billie Thompson
- Make the prompt customizable - (423b8fb) - Billie Thompson

- - -

## v0.2.0 - 2023-11-08
#### Continuous Integration
- Skip signing - (1447cf9) - Billie Thompson
#### Documentation
- Add link to license - (34fcdc2) - Billie Thompson
- update license to reflect license - (0687e21) - Billie Thompson
#### Features
- Allow text source to be an http url - (f038970) - Billie Thompson

- - -

## v0.1.2 - 2023-11-07
#### Bug Fixes
- Use pause based chunking - (b0ac35a) - Billie Thompson

- - -

## v0.1.1 - 2023-11-07
#### Bug Fixes
- Remove deprecated funtion call - (1b357f3) - Billie Thompson
- Give poetry it's own cache directory, rather than having it use the one that will be overriden - (6c34af8) - Billie Thompson
- Use history to prevent voice changing every sentence - (9d7f28f) - Billie Thompson
- Cache models to known directory - (e586e63) - Billie Thompson
#### Build system
- Enable CPU offloading for the moddel - (61039e6) - Billie Thompson
- Clean installers after installing - (f623207) - Billie Thompson
- Print when we remove the main.py we create - (58001c5) - Billie Thompson
- Correct creation of mkdir - (5879e23) - Billie Thompson
- Fix permissions of home - (2278a64) - Billie Thompson
- Correct permissions of src dir - (b49b867) - Billie Thompson
- Remove arm, it's not supported by the cuda dependencies we need - (865a3a2) - Billie Thompson
- Ensure cache dir is writable - (0dca381) - Billie Thompson
#### Continuous Integration
- Don't fill up drives totally - (0fcd4b4) - Billie Thompson
- Free up disk space for models - (e8c9825) - Billie Thompson
- Remove chmod - (a70804c) - Billie Thompson
- Mount only inside the work directory for docker volumes - (61e8e33) - Billie Thompson
- Change permissions on cache folders - (7cedfcc) - Billie Thompson
- Ensure that input and output folders are accessible as the user in the container - (9727ef6) - Billie Thompson
- Flag caches as rw - (4fd6a49) - Billie Thompson
- Ensure we run as our ubuntu user - (917adcb) - Billie Thompson
- Pass data via volumes rather than stdin for test - (f01c299) - Billie Thompson
- Try a pull before the test build - (a1304a4) - Billie Thompson
- Do not use docker build action as it is crashing - (a1cfdb8) - Billie Thompson
- Add a file into the src directory - (69734c0) - Billie Thompson
- Remove duplicated build step - (1636855) - Billie Thompson
- Remove duplicated build step - (38efdf0) - Billie Thompson
- Use gha for cache - (3b4e406) - Billie Thompson
- Add an explicit test run - (ddef304) - Billie Thompson
- correct package ecosystem for bumps - (a5ddecc) - Billie Thompson
#### Documentation
- Add note about cache dir to readme - (9004855) - Billie Thompson

- - -

## v0.1.0 - 2023-11-07
#### Build system
- Correct cuda repo name on arm - (0d50006) - Billie Thompson
#### Continuous Integration
- Add poetry to release step - (25eeb18) - Billie Thompson
#### Refactoring
- Formatting - (db01c82) - Billie Thompson

- - -

Changelog generated by [cocogitto](https://github.com/cocogitto/cocogitto).