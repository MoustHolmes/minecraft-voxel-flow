# GitHub Repository Setup Instructions

## Steps to Create and Push to GitHub

### 1. Create a New Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `minecraft-voxel-flow`
3. Description: `Flow Matching for Minecraft voxel structure generation with schematic rendering pipeline`
4. Visibility: Choose Public or Private
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### 2. Add GitHub Remote and Push

Once the repository is created, GitHub will show you commands. Use these:

```bash
cd /Users/moustholmes/minecraft_voxel_flow

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/minecraft-voxel-flow.git

# Push the code
git push -u origin main
```

Or if you prefer SSH:

```bash
git remote add origin git@github.com:YOUR_USERNAME/minecraft-voxel-flow.git
git push -u origin main
```

### 3. Verify the Push

After pushing, check that:
- README.md displays properly on the repository homepage
- Documentation is accessible in the `docs/` folder
- Code is properly organized in `src/minecraft_voxel_flow/`

## Repository Settings (Optional)

### Add Topics/Tags
In your repository settings, add relevant topics:
- `pytorch`
- `pytorch-lightning`
- `flow-matching`
- `minecraft`
- `generative-models`
- `machine-learning`
- `schematic-rendering`
- `chunky`

### Set Description
Use this description in the "About" section:
```
Flow Matching for Minecraft voxel structure generation with complete schematic rendering pipeline using Chunky. Includes multi-angle camera system, PyTorch Lightning training, and comprehensive documentation.
```

### Enable GitHub Pages (for documentation)
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main`, folder: `/docs`
4. Your docs will be available at: `https://YOUR_USERNAME.github.io/minecraft-voxel-flow/`

## Quick Links to Add to README

Consider adding these badges to the top of your README.md:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
```

## Sharing and Collaboration

Once pushed, you can:
- Share the repository URL
- Create releases/tags for versions
- Enable Issues for bug tracking
- Set up GitHub Actions for CI/CD
- Add collaborators

## Example Commands Summary

```bash
# After creating repository on GitHub
cd /Users/moustholmes/minecraft_voxel_flow

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/minecraft-voxel-flow.git

# Push initial commit
git push -u origin main

# Future updates
git add .
git commit -m "Your commit message"
git push
```

## What's Already Committed

✅ Complete source code  
✅ Documentation (README, CAMERA_ANGLE_SYSTEM, ANGLE_BUG_POSTMORTEM)  
✅ Configuration files (Hydra configs)  
✅ Tests  
✅ Scripts (rendering pipeline, scrapers)  
✅ .gitignore (properly excludes data files and large binaries)  
✅ LICENSE (MIT)  
✅ pyproject.toml and requirements

## What's Excluded (via .gitignore)

❌ Large data files (schematics, renders)  
❌ Model checkpoints  
❌ Chunky installation  
❌ Generated outputs  
❌ Virtual environments  
❌ Cache files

This keeps the repository clean and focused on code/documentation.
