---
name: si-upscale4k
description: Audit game/app PNG and DDS texture dumps, detect RGBA transparency and power-of-two dimensions, and route batches for 4K ChaiNNer upscaling.
---

# SI-Upscale4K Skill

1. Run `python si_texture_audit.py --scan <dump_dir>` before launching ChaiNNer.
2. Process `4x_rgba_split` through the Split-Transparency node chain so UI fonts and foliage never get black halos.
3. Process `4x_opaque` with 16px Mirror Padding enabled so repeating wall/floor tiles stay 100% seamless.
4. Export final replacements as hardware-compressed `BC7 DDS` with mipmaps enabled.
