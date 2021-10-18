# github actions documentation

This command will run the super-linter locally in the current directory leaving
a file called `super-linter.log`.

```
docker run \
-e RUN_LOCAL=true \
-e USE_FIND_ALGORITHM=true \
-e VALIDATE_PYTHON_FLAKE8=true \
-e VALIDATE_PYTHON_ISORT=true \
-e VALIDATE_PYTHON_MYPY=true \
-e VALIDATE_PYTHON_PYLINT=true \
-e VALIDATE_DOCKERFILE=true \
-v $PWD:/tmp/lint \
github/super-linter:slim-v4
```
