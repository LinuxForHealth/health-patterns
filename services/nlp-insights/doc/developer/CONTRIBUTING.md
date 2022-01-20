## Contributing In General
Our project welcomes external contributions. If you have an itch, please feel
free to scratch it.

To contribute code or documentation, please submit a [pull request](https://github.com/Alvearie/health-patterns/pulls).

A good way to familiarize yourself with the codebase and contribution process is
to look for and tackle low-hanging fruit in the [issue tracker](https://github.com/Alvearie/health-patterns/issues).
Before embarking on a more ambitious contribution, please [communicate](#communication) with us.

*We appreciate your effort, and want to avoid a situation where a contribution
requires extensive rework (by you or by us), sits in backlog for a long time, or
cannot be accepted at all!*

### Proposing new features

If you would like to implement a new feature, please [raise an issue](https://github.com/Alvearie/health-patterns/issues)
before sending a pull request so the feature can be discussed. This is to avoid
you wasting your valuable time working on a feature that the project developers
are not interested in accepting into the code base.

### Fixing bugs

If you would like to fix a bug, please [raise an issue](https://github.com/Alvearie/health-patterns/issues) before sending a
pull request so it can be tracked.

### Merge approval

The project maintainers use LGTM (Looks Good To Me) in comments on the code
review to indicate acceptance. A change requires LGTMs from two of the
maintainers of each component affected.

For a list of the maintainers, see the [MAINTAINERS.md](MAINTAINERS.md) page.

## Legal

Each source file must include a license header for the Apache
Software License 2.0.

We have tried to make it as easy as possible to make contributions. This
applies to how we handle the legal aspects of contribution. We use the
same approach - the [Developer's Certificate of Origin 1.1 (DCO)](https://github.com/hyperledger/fabric/blob/master/docs/source/DCO1.1.txt) - that the Linux® Kernel [community](https://elinux.org/Developer_Certificate_Of_Origin)
uses to manage code contributions.

We simply ask that when submitting a patch for review, the developer
must include a sign-off statement in the commit message.

Here is an example Signed-off-by line, which indicates that the
submitter accepts the DCO:

```
Signed-off-by: John Doe <john.doe@example.com>
```

You can include this automatically when you commit a change to your
local git repository using the following command:

```
git commit -s
```

## Communication
Connect with us by opening an [issue](https://github.com/Alvearie/health-patterns/issues).

# Coding style guidelines
This project makes use of several coding conventions and tools.


## Formatting
The project is formatted using [Black](https://black.readthedocs.io/en/stable/). New code should continue to follow this formatter. The formatter is able to automatically format an entire source tree, however we do not have that feature included in the build. Please format before a pull request.


## Unit tests
Unit tests and Doc tests are run as part of the build process. New function should include appropiate additional tests.  

Tests can be executed with the build command
`./gradlew test`


## Static code checking
The project uses a combination of flake8, pylint, and mypy to detect static code problems. The configuration is defined in `setup.cfg`. These checks can be run as a build task (this will also run unit tests).
`./gradlew checkSource`

When making a pull request, all warnings and errors should be resolved. When a warning can be safely ignored, a 'disabling' comment should be added to the line of code that causes the problem. (This will prevent the warning from being reported by checkSource). An alternative is to modify setup.cfg so that a warning is not generated. An example of this would be to add an additional 'good-name' so that non-standard variable names are not flagged.
