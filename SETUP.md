# Animated GitHub profile cards

## Install

Copy the contents of this folder into the special profile repository named exactly:

`nishant25bce10660-cell/nishant25bce10660-cell`

That repository is not currently visible as a public repository on the profile, so create it as a public repository first if it does not exist. Keep the branch name as `main`, or change the workflow branch filter if you use another default branch.

Install the only Python dependency locally:

```bash
python -m pip install "fonttools[woff]"
```

The script fetches the Latin Inter source from Google Fonts, subsets the Regular and SemiBold faces with `pyftsubset`, and embeds each subset in SVG as a base64 WOFF data URI. In CI, the same step runs daily. The raw font sources and WOFF subsets are cached under `.cache/` and are not committed.

## Generate animated cards

```bash
python scripts/generate_profile_cards.py
```

## Generate final-frame cards for screenshots

macOS/Linux:

```bash
STATIC=1 python scripts/generate_profile_cards.py
```

PowerShell:

```powershell
$env:STATIC = "1"
python scripts/generate_profile_cards.py
Remove-Item Env:STATIC
```

Static mode emits the same layouts with all elements in their final positions and omits CSS keyframes and SMIL animation elements. Run the script again without `STATIC=1` before committing if you want the animated version.

## Customize

Edit `profile.json`:

- `name`, `tagline`, `location`: hero content.
- `theme`: background, surface, text, border, and brand accent colors.
- `tiles`: exactly three links. Each one becomes `cards/tile-1.svg` through `cards/tile-3.svg`.
- `repositories`: one card is generated for every entry.
- `portrait`: optional path relative to the repository root, such as `assets/portrait.jpg`. The image is embedded into the hero SVG as a data URI.
- `animation`: delays in seconds. Increase later card delays to preserve top-to-bottom playback.

The initial `data/contributions.json` is intentionally empty so the README does not display fabricated statistics. The GitHub Action replaces it with the account's contribution calendar on its first run.

## Daily GitHub Action

The workflow at `.github/workflows/update-profile-cards.yml`:

1. Queries GitHub's GraphQL contribution calendar for a 53-week calendar window (365 days are used for yearly metrics), including private contributions visible to the authenticated account.
2. Saves the response to `data/contributions.json`.
3. Runs the SVG renderer.
4. Commits and pushes the JSON and generated `cards/` only when content changed.

In the profile repository, go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**. The workflow also declares `contents: write`. For public-only contribution totals, the default `GITHUB_TOKEN` is sufficient. To include private contributions in the calendar, add a repository secret named `PROFILE_TOKEN` containing a personal access token with permission to read your user profile; the workflow uses it only for the GraphQL read. The commit itself still uses the repository `GITHUB_TOKEN`.

The workflow is scheduled at 00:17 UTC every day (05:47 IST). You can also run it manually from the **Actions** tab.

## SVG / GitHub behavior

Every card is a standalone SVG intended to be referenced with an HTML `<img>` tag. Animation uses inline SVG CSS keyframes and SMIL; each card has its own delay so the README plays from top to bottom. The SVG styles include `prefers-reduced-motion: reduce` rules that disable CSS animation and hide SMIL animation elements. The visual geometry is already authored at its final position, so reduced-motion and static modes remain readable.

GitHub controls SVG sanitization and rendering. After the first push, check the profile page in both light and dark GitHub themes and confirm that SVG cards render as expected. If your organization/account policy blocks SVG images, use the generated static mode and export the SVGs to PNG as a fallback.
