# SI-Upscale4K: Texture Dump Auditor & Alpha-Channel Router for ChaiNNer

**Created by [SI NEWS](https://www.youtube.com/channel/UC4m6veQiZdc_pAfxKQluRgA) • Official companion repo for *"ChaiNNer and Free Local AI: Upscale Any App or Game Texture Pack to 4K Automatically"*.**

When remastering a game or app texture dump (`PCSX2`, `Dolphin`, `Special K`, `MGSHDFix`), feeding every file blindly into a 4x neural upscaler causes two major bugs:
1. **Black Halo Artifacts on UI/Foliage**: RGBA textures with transparent alpha channels get dark outlines if RGB and Alpha aren't split first.
2. **8K VRAM Explosion**: Already-large `1024px–2048px` textures get scaled to `8192px`, causing GPU stutter.

`si-upscale4k` includes a **zero-dependency Python stdlib binary header scanner (`si_texture_audit.py`)** that reads `.png` (`IHDR`) and `.dds` headers directly in microseconds (no Pillow/OpenCV required!) and routes your texture dump into clean buckets:
- `4x_rgba_split/` (transparent UI/hud/foliage needing Split-Transparency chain)
- `4x_opaque/` (low-res `<512px` opaque wall/character textures)
- `2x_medium/` (`512px–1024px` textures needing 2x scale to hit 4K)
- `skip_already_hd/` (`>=2048px` textures that should not be re-upscaled)

## Quick Start (Windows PowerShell)
```powershell
git clone https://github.com/Grokeador/si-upscale4k
cd si-upscale4k
python -m unittest discover -s tests -v
python si_texture_audit.py --scan C:\Games\TextureDump
```

MIT Licensed — Built by [SI NEWS](https://www.youtube.com/channel/UC4m6veQiZdc_pAfxKQluRgA).
