# Security Policy

Stuart is a small project with one maintainer. This file says where to send
a vulnerability report so that it reaches someone, and what you can expect
once it does. It promises nothing that needs a second person.

## Reporting a vulnerability

**Please don't open a public issue for a security problem.** A public issue
tells everyone running Stuart about the hole at the same moment it tells the
maintainer.

Instead, use one of these:

- **GitHub's private vulnerability reporting** — go to the
  [Security tab](https://github.com/izrik/stuart/security) and choose
  *Report a vulnerability*. The report is visible only to the maintainer.
- **Contact the maintainer directly** — [@izrik](https://github.com/izrik),
  using the contact details on that GitHub profile.

A useful report says what the problem is, how to reproduce it, and what an
attacker gets out of it. A proof of concept against your own instance
helps; one against somebody else's doesn't — see *Scope* below.

## Scope

In scope:

- The code in this repository — `stuart.py`, the Jinja2 templates, the
  static assets, the `Dockerfile` and the scripts.
- The instances of Stuart that we run.

Out of scope:

- **Third-party dependencies.** If the bug is in Flask, Werkzeug,
  SQLAlchemy, py-gfm or anything else in
  [`requirements.txt`](requirements.txt), report it to that project — they
  can fix it and we can't. Tell us as well if you like, and we'll pick up
  the new version; [`CLAUDE.md`](CLAUDE.md) explains why a few of those
  pins are deliberately old.
- **Anything you'd have to attack a running production system to find.**
  Don't test against an instance you don't own: no load or
  denial-of-service testing, no attempts on other people's accounts or
  data, no social engineering. Run Stuart locally and attack that.

## What to expect

- An acknowledgement that your report arrived and was read.
- A fix, where the finding is real and the fix is something one maintainer
  can afford to write. Where it isn't, you'll be told that rather than left
  waiting.
- Credit in the release notes and the [changelog](CHANGELOG.md), if you
  want it. Say so in your report, along with how you'd like to be named.

There is no bounty, and no promised response time — this is a spare-time
project, and a number here would be a number nobody is on the hook for.
Reports do get read.

## Supported versions

The latest release and the current `master`. Stuart ships from `master` and
tags releases; there are no maintained release branches, and no older
version gets a backported fix. If you're running something older than the
latest tag, upgrading is the first step.
