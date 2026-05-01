# Packaging Plan

## Public v0.1 Order

1. Prepare `minimal` from global likes.
2. Prepare `public-preview` from private-filtered public candidates.
3. Upload `public-preview` and `resource_manifest.json` to a Hugging Face Dataset.
4. Verify:
   ```bash
   agentfiguregallery setup --pack public-preview --manifest-url <manifest-url>
   agentfiguregallery gallery --plot-type bar_chart --limit 50 --serve
   ```
5. Add `full-public` after the public-preview pack passes private-path scan.
6. Only after that, publish the GitHub repository.

## Full Mirror Policy

The development Drawing workspace can be mirrored, but it should be private by default. It contains raw upstream repos, generated outputs, and possible private-path context.

For public growth, publish only:

- private-filtered candidate indexes
- private-filtered previews
- source metadata
- license metadata
- ExtendAgent expansion instructions
