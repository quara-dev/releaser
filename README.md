# quara-releaser

## Example usage in Azure Devops

- Create a file named `manifest.json` and publish it as pipeline artefact:

```yaml
steps:
  - script: python -m releaser create-manifest -o manifest.json
    displayName: Create manifest.json file

  - publish: "$(System.DefaultWorkingDirectory)/manifest.json"
    displayName: Publish manifest.json as pipeline artefact
    artifact: manifest.json
```

- Define a string variable named `MANIFEST` holding a manifest:

```yaml
steps:
  - script: |
      manifest="$(python -m releaser analyze-manifest)"
      echo "##vso[task.setvariable variable=MANIFEST;isoutput=true]$manifest"
    displayName: Create MANIFEST variable holding release manifest as JSON string

  - script: echo $MANIFEST
    displayName: Display MANIFEST variable
```

- Define a comma-separated list variable holding all tags to build:

```yaml
parameters:
  - name: application
    type: string

steps:
  - script: |
      tags=$(releaser analyze-manifest --list-tags --app {{ parameters.application }} --no-platform
      comma_separated_tags=$(echo $tags | jq -r 'join(",")')
      echo "##vso[task.setvariable variable=TAGS;isoutput=true]$comma_separated_tags"
    displayName: Create TAGS variable holding comma-separated list of docker image tags to build for app

  - script: echo $TAGS
    displayName: Display TAGS variable
```

- Build a multi-platform docker image manifest:

```yaml
parameters:
  - name: application
    type: string
  - name: platform
    type: string

steps:
  - step: |
      for repository in $(releaser analyze-manifest --list-repositories --app {{ parameters.application }}); do
        for image in $(releaser analyze-manifest --list-images --repository "$repository" --platform {{ parameters.platform }}); do
          # Build image for platform
          docker build -t $image --platform {{ parameters.platform }} --push ...
        done
      done
    displayName: Build docker image for platform {{ parameters.platform }}

  - step: |
      for repository in $(releaser analyze-manifest --list-repositories --app {{ parameters.application }}); do
        for tag in $(releaser analyze-manifest --list-tags --repository $repository --no-platform); do
          json_images=$(releaser analyze-manifest --list-images --repository $repository --manifest-tag "$tag")
          manifest_image="$repository:$tag"
          platform_images=$(echo $json_images | jq -r 'join(" ")')
          docker manifest create $manifest_image $platform_images
      done
    done

```

## Command Line Reference

### Create a release manifest

The `create-manifest` command can be used to generate a manifest in JSON format.

- By default, manifest is written to standard output, but `-o` or `--output` option can be provided to write manifest to a file:

```bash
releaser create-manifest -o manifest.json
```

### Analyze the manifest

- Use the `analyze-manifest` command to show all or part of a manifest in standard output:

```bash
releaser analyze-manifest
```

This command first generates a manifest by default, but also accept a `-i` or `--input` option to read an existing manifest from a file:

```bash
releaser analyze-manifest -i manifest.json
```

Many options are available to query specific information within the manifest.

#### List images

- It's possible to list all images declared within a manifest:

  ```bash
  releaser analyze-manifest --list-images
  ```

- To list images for a single application, use the `--app` option:

  ```bash
  releaser analyze-manifest --list-images --app myapp
  ```

- To list images for a single platform, use the `--platform` option:

  ```bash
  releaser analyze-manifest --list-images --platform linux/arm64
  ```

  > Note: Using `--platform` excludes non-platform images and returns platform images only.

- To list images for all platforms matching a manifest tag, use the `--manifest-tag`:

  ```bash
  releaser analyze-manifest --list-images --app myapp --manifest-tag "edge"
  ```

  > Note: Using `--manifest-tag` excludes non-platform images and returns platform images only.

#### List tags

- Like images, it's possible to list all tags, but the query must always be scoped to an application:

  ```bash
  releaser analyze-manifest --list-tags --app myapp
  ```

  > Note: This will list all tags, including platform tags.

- To exclude platform tags, use the `--no-platform` option:

  ```bash
  releaser analyze-manifest --list-tags --app myapp --no-platform
  ```

- To list tags for a single platform, use the `--platform` option:

  ```bash
  releaser analyze-manifest --list-tags --app myapp --platform="linux/arm64"
  ```

  > Note: Using `--platform` excludes non-platform tags and returns only plaform tags for any of given platforms only.

### Upload the manifest

A command can be used to publish manifest using a POST request:

```bash
releaser upload-manifest -i manifest.json --webhook $AZ_DEVOPS_WEBHOOK_URL
```
